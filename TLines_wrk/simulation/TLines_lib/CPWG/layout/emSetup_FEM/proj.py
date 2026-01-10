# Automatically generated file proj.py"

# Generated with $Id: extrusion_to_empro.cpp 11193 2012-11-22 13:42:22Z mdewilde $ 

import empro, empro.toolkit

def getVersion():
	return 11

def getSessionVersion(session):
	try:
		return session.getVersion()
	except AttributeError:
		return 0

def get_ads_import_version():
	try:
		ads_import_version = empro.toolkit.ads_import.getVersion()
	except AttributeError:
		ads_import_version = 0
	return ads_import_version

def ads_simulation_settings():
	set_frequency_plan_and_common_options()
	set_FEM_options()

def set_frequency_plan_and_common_options():
	try:
		sim=empro.activeProject.simulationSettings
	except AttributeError:
		sim=empro.activeProject.createSimulationData()
	# Frequency plan:
	frequency_plan_list=sim.femFrequencyPlanList()
	frequency_plan=empro.simulation.FrequencyPlan()
	frequency_plan.type="Adaptive"
	frequency_plan.startFrequency=0
	frequency_plan.stopFrequency=6000000000
	frequency_plan.samplePointsLimit=101
	frequency_plan_list.append(frequency_plan)
	if 'minFreq' in empro.activeProject.parameters:
		empro.activeProject.parameters.setFormula('minFreq','0 GHz')
	if 'maxFreq' in empro.activeProject.parameters:
		empro.activeProject.parameters.setFormula('maxFreq','6 GHz')
	sim.saveFieldsFor="NoFrequencies"

def set_FEM_options():
	# Simulation options:
	try:
		sim=empro.activeProject.simulationSettings
	except AttributeError:
		sim=empro.activeProject.createSimulationData()
	sim.engine = empro.toolkit.simulation.FEM
	try:
		sim.ambientConditions.backgroundTemperature = "25 degC"
	except AttributeError:
		pass
	try:
		sim.femEigenMode = False
	except AttributeError:
		pass
	try:
		sim.portOnlyMode = False
	except AttributeError:
		pass
	try:
		sim.transfinitePorts  = False
	except AttributeError:
		pass
	sim.femMeshSettings.minimumNumberOfPasses      = 2
	sim.femMeshSettings.maximumNumberOfPasses      = 15
	sim.femMeshSettings.deltaError                 = 0.02
	sim.femMeshSettings.refineAtSpecificFrequency  = False
	sim.femMeshSettings.refinementFrequency        = "0 GHz"
	sim.femMeshSettings.requiredConsecutivePasses  = 1
	sim.femMeshSettings.meshRefinementPercentage   = 25
	sim.femMeshSettings.orderOfBasisFunctions      = 2
	try:
		sim.femMeshSettings.useMinMeshSize               = False
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.minMeshSize                  = "0 m" 
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.autoTargetMeshSize           = True
		sim.femMeshSettings.useTargetMeshSize            = True
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.targetMeshSize               = "0 m" 
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.edgeMeshLength               = "0 m" 
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.vertexMeshLength               = "0 m" 
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.mergeObjectsOfSameMaterial = True
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.alwaysSolveOnFinestMesh = False
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.autoConductorMeshing = False
	except AttributeError:
		pass
	try:
		empro.activeProject.gridGenerator.femPadding.useDefault = False
	except AttributeError:
		pass
	try:
		sim.dataSetFileName                            = ''
	except AttributeError:
		pass
	try:
		sim.femMatrixSolver.solverType                    = "MatrixSolverAuto"
	except ValueError: # Old versions of EMPro (< 2017) do not have the auto-select solver option
		sim.femMatrixSolver.solverType                    = "MatrixSolverDirect"
	sim.femMatrixSolver.maximumNumberOfIterations     = 500
	sim.femMatrixSolver.tolerance                     = 1e-05
	try:
		sim.femMeshSettings.refinementStrategy="maxFrequency"
	except AttributeError:
		pass

def get_session(usedFlow="ADS"):
	ads_import_version = get_ads_import_version()
	if ads_import_version >= 3:
		session=empro.toolkit.ads_import.Import_session(units="mm", wall_boundary="Radiation",usedFlow=usedFlow,adsProjVersion=getVersion())
		return session
	try:
		session=empro.toolkit.ads_import.Import_session(units="mm", wall_boundary="Radiation",usedFlow=usedFlow)
	except TypeError: # usedFlow may not be available in old FEM bits
		session=empro.toolkit.ads_import.Import_session(units="mm", wall_boundary="Radiation")
	return session

def _dummyUpdateProgress(value):
	pass

def _createIfToggleExtensionToBoundingBoxExpression(exprTrue,exprFalse):
	if get_ads_import_version() >= 11:
		return "if(toggleExtensionToBoundingBox, %s, %s)" % (exprTrue, exprFalse)
	else:
		return exprFalse

def ads_import(usedFlow="ADS",topAssembly=None,session=None,demoMode=False,includeInvalidPorts=True,suppressNotification=False,updateProgressFunction=_dummyUpdateProgress,materialForEachLayer=False):
	ads_simulation_settings()
	importer = projImporter(usedFlow,session,updateProgressFunction)
	rv = importer.ads_import(usedFlow,topAssembly,demoMode,includeInvalidPorts,suppressNotification,materialForEachLayer)
	try:
		empro.activeProject.gridGenerator.femPadding.useDefault = False
	except AttributeError:
		pass
	return rv

class projImporter():
	def __init__(self,usedFlow="ADS",session=None,updateProgressFunction=_dummyUpdateProgress):
		self.usedFlow = usedFlow
		if session==None:
			self.session=get_session(usedFlow)
		else:
			self.session = session
		if getSessionVersion(self.session) >= 8:
			self.session.setProjImporter(self)
		self.roughnesses={}
		self.materials={}
		self.substratePartNameMap={}
		self.substrateLayers=[] # ordered list with substrate layers
		self.waveforms={}
		self.circuitComponentDefinitions={}
		self.initNetlists()
		self.updateProgressFunction = updateProgressFunction
		if updateProgressFunction == _dummyUpdateProgress:
			if getSessionVersion(self.session) >= 10:
				self.updateProgressFunction = self.session.getUpdateProgressFunction()
		self.geoProgress = 0

	def _updateProgress(self,progress):
		self.updateProgressFunction(progress)

	def _setModelTypeForMetals(self,material,value):
		if getSessionVersion(self.session) >= 2:
			self.session.setModelTypeForMetals(material,value)
			return
		try:
			material.details.electricProperties.parameters.useSurfaceConductivityCorrection = value
		except:
			pass
	def _checked_roughness(self,roughnessTypeString,*args):
		try:
			roughnessConstructor = getattr(empro.material,roughnessTypeString)
			return roughnessConstructor(*args)
		except AttributeError:
			print("Warning: unsupported surface roughness type %s. Roughness will be ignored." % roughnessTypeString)
			return None
	def _create_parameter(self,iParName,iFormula,iNotes,iUserEditable,fixGridAxis=""):
		if getSessionVersion(self.session) >= 2:
			self.session.create_parameter(iParName,iFormula,iNotes,iUserEditable,fixGridAxis)
			return
		try:
			self.session.create_parameter(iParName,iFormula,iNotes,iUserEditable)
		except AttributeError:
			empro.activeProject.parameters.append(iParName,iFormula,iNotes,iUserEditable)
		if fixGridAxis in ['X','Y','Z']:
			gG = empro.activeProject.gridGenerator
			newFP = empro.libpyempro.mesh.FixedPoint()
			if fixGridAxis == 'X':
				location = (iParName,0,0)
			elif fixGridAxis == 'Y':
				location = (0,iParName,0)
			elif fixGridAxis == 'Z':
				location = (0,0,iParName)
			newFP.location = location
			newFP.axes=fixGridAxis
			gG.addManualFixedPoint(newFP)
	def _circularGridRegion(self,x,y,radius):
		radius = empro.core.Expression(radius)
		newGRP = empro.libpyempro.mesh.ManualGridRegionParameters()
		newGRP.cellSizes.target = (radius,radius,0)
		newGRP.gridRegionDirections="X|Y"
		newGRP.regionBounds.lower = (x-radius,y-radius,0)
		newGRP.regionBounds.upper = (x+radius,y+radius,0)
		return newGRP
	def _partGridParameters(self,targetCellSize):
		targetCellSize = empro.core.Expression(targetCellSize)
		newGP = empro.libpyempro.mesh.PartGridParameters()
		newGP.cellSizes.target = (targetCellSize,targetCellSize,0)
		newGP.gridRegionDirections="X|Y"
		newGP.useGridRegions = True
		return newGP
	def _create_sketch(self,pointString,sketch=None,closed=True):
		if getSessionVersion(self.session) >= 4:
			return self.session.create_sketch(pointString,sketch,closed)
		V=empro.geometry.Vector3d
		L=empro.geometry.Line
		def stringToPoint(s):
			sList = s.split('#')
			return V(sList[0],sList[1],0)
		if sketch == None:
			sketch=empro.geometry.Sketch()
		pointList = [ stringToPoint(x) for x in pointString.split(';') ]
		if closed:
			edges = [ L(pointList[i-1],pointList[i]) for i in range(len(pointList)) ]
		else:
			edges = [ L(pointList[2*i],pointList[2*i+1]) for i in range(len(pointList)/2) ]
		sketch.addEdges(edges)
		return sketch
	def _create_extrude(self, pointStrings, height, up):
		if getSessionVersion(self.session) >= 14:
			return self.session.create_extrude(pointStrings, height, up)
		else:
			sketch = None
			for pointString in pointStrings:
				sketch = self._create_sketch(pointString, sketch)
			part = empro.geometry.Model()
			part.recipe.append(empro.geometry.Extrude(sketch, height, empro.geometry.Vector3d(0, 0, (-1, 1)[up])))
			return part
	def _create_cover(self, pointStrings):
		if getSessionVersion(self.session) >= 14:
			return self.session.create_cover(pointStrings)
		else:
			sketch = None
			for pointString in pointStrings:
				sketch = self._create_sketch(pointString, sketch)
			part = empro.geometry.Model()
			part.recipe.append(empro.geometry.Cover(sketch))
			return part
	def _create_bondwire(self,radius, segments, points, name=None,bwAssembly=None,topAssembly=None,material=None,partModifier=(lambda x : x),profile=None,above=True):
		if getSessionVersion(self.session) >= 13:
			part = self.session.create_bondwire(radius, segments, points, name, bwAssembly,topAssembly,material,partModifier,profile,above)
		else:
			if profile is not None:
				part = empro.geometry.Model()
				try:
					part.recipe.append(empro.geometry.Bondwire(points[0],points[-1],profile))
				except TypeError:
					# Only for compatibility with EMPro 2011.02 or older
					self.session.warnings.append('For importing bondwires with profile definitions it is advised to use EMPro 2012.09 or later.')
					bw=empro.geometry.Bondwire(points[0],points[-1],empro.geometry.BondwireDefinition(name,radius,segments))
					bw.definition=profile
					part.recipe.append(bw)
				if not above:
					import math
					part.coordinateSystem.rotate(math.pi,0,0)
				part = partModifier(part)
				bwAssembly.append(part)
				part.name = name
				empro.toolkit.applyMaterial(part,material)
			else:
				try:
					part = self.session.create_bondwire(radius, segments, points, name, bwAssembly,topAssembly,material,partModifier)
				except TypeError:
					part = self.session.create_bondwire(radius, segments, points)
					part = partModifier(part)
					bwAssembly.append(part)
					part.name = name
					empro.toolkit.applyMaterial(part,material)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=2000
		return part
	def _create_internal_port(self, name, definitionString, head, tail, extent=None):
		if getSessionVersion(self.session) < 15 and (isinstance(head, list) or isinstance(tail, list)):
			raise RuntimeError("Ports having multiple positive or negative pins are not yet supported")
		if getSessionVersion(self.session) >= 9:
			return self.session.create_internal_port(name, definitionString, head, tail, extent)
		port=empro.components.CircuitComponent()
		port.name=name
		port.definition=self.circuitComponentDefinitions[definitionString]
		port.head=head
		port.tail=tail
		if extent != None:
			port.extent=extent
			port.useExtent=True
		return port
	def _set_extra_port_info(self, port, termType, number, name, feedType, mode = -1):
		try:
			if get_ads_import_version() >= 17:
				self.session.set_extra_port_info(port=port, termType=termType, number=number, name=name, mode=mode, feedType=feedType)
			else:
				self.session.set_extra_port_info(port=port, termType=termType, number=number, name=name, mode=mode)
		except AttributeError:
			pass
		global g_portNbToName
		g_portNbToName[number] = (name, mode)
	def _setAssemblyMeshSettings(self,a,vertexMeshLength=0,edgeMeshLength=0,surfaceMeshLength=0):
		if vertexMeshLength==0 and edgeMeshLength==0 and surfaceMeshLength==0:
			return
		if getSessionVersion(self.session) >= 12:
			self.session.setAssemblyMeshSettings(a,vertexMeshLength,edgeMeshLength,surfaceMeshLength)
			return
		parts = [x for x in a.flatList(False)]
		for x in parts:
			x.meshParameters.vertexMeshLength=vertexMeshLength
			x.meshParameters.edgeMeshLength=edgeMeshLength
			x.meshParameters.surfaceMeshLength=surfaceMeshLength
	def _getEMProMaterialName(self,ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1):
		EMProMaterialName=ADSmaterialName
		if ADSmaterialName in [x for (x,y) in ADSmaterialMap.keys()]:
			EMProMaterialName+="_"+str(extraMaterialProperties)
			if not ADSmaterialName in ADSmaterialsNo1to1:
				ADSmaterialsNo1to1.append(ADSmaterialName)
				self.session.warnings.append('The ADS material '+ADSmaterialName+' is used on masks with different precedence, sheet thickness or modeltype for metals and has therefore been mapped to multiple EMPro materials.')
		return EMProMaterialName
	def create_bondwire_definitions(self):
		self.bondwire_definitions={}
		if not hasattr(empro.activeProject,"bondwireDefinitions"):
			return
	def create_materials(self,materialForEachLayer=False):
		ADSmaterialMap={}
		EMProNameMaterialMap={}
		layerEMProMaterialNameMap={}
		ADSmaterialsNo1to1=[]
		ADSmaterialName=["AIR","simulation_box"][materialForEachLayer]
		extraMaterialProperties=(0,None,None,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(255,255,255,0), permittivity=1, permeability=1)
			try:
				material.priority=0
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["simulation_box"]=material
		layerEMProMaterialNameMap["simulation_box"]=EMProMaterialName
		ADSmaterialName=["Copper","cond"][materialForEachLayer]
		extraMaterialProperties=(162,1.25e-05,False,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(255,0,0,255), conductivity=58000000, imag_conductivity=0, permeability=1)
			self._setModelTypeForMetals(material,False)
			try:
				material.priority=162
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["cond"]=material
		layerEMProMaterialNameMap["cond"]=EMProMaterialName
		ADSmaterialName=["Copper","cond2"][materialForEachLayer]
		extraMaterialProperties=(162,1.25e-05,False,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(0,0,255,255), conductivity=58000000, imag_conductivity=0, permeability=1)
			self._setModelTypeForMetals(material,False)
			try:
				material.priority=162
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["cond2"]=material
		layerEMProMaterialNameMap["cond2"]=EMProMaterialName
		ADSmaterialName=["PERFECT_CONDUCTOR","cond_cond2"][materialForEachLayer]
		extraMaterialProperties=(64,1e-09,False,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(255,76,172,255), thickness="1e-09 m", resistance=0)
			try:
				material.details.electricProperties.parameters.thickness = "1e-09 m"
			except AttributeError:
				pass
			self._setModelTypeForMetals(material,False)
			try:
				material.priority=64
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["cond_cond2"]=material
		layerEMProMaterialNameMap["cond_cond2"]=EMProMaterialName
		ADSmaterialName=["FR4_CUSTOM","__SubstrateLayer1"][materialForEachLayer]
		extraMaterialProperties=(50,None,None,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(202,225,255,128), permittivity=4.4, losstangent=0.04, permeability=1, use_djordjevic=True, lowfreq=1000, evalfreq=1000000000, highfreq=1000000000000)
			try:
				material.priority=50
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["__SubstrateLayer1"]=material
		layerEMProMaterialNameMap["__SubstrateLayer1"]=EMProMaterialName
		self.substratePartNameMap["__SubstrateLayer1"]=ADSmaterialName
		self.substrateLayers.append("__SubstrateLayer1")
		self.numberSubstratePartNameMap()
		if getSessionVersion(self.session) >= 6:
			self.session.appendUniqueMaterials(EMProNameMaterialMap)
		else:
			for name,material in EMProNameMaterialMap.items():
				empro.activeProject.materials().append(material)
				EMProNameMaterialMap[name] = empro.activeProject.materials().at(empro.activeProject.materials().size()-1)
		self.materials={}
		for layerName in layerEMProMaterialNameMap.keys():
			self.materials[layerName]=EMProNameMaterialMap.get(layerEMProMaterialNameMap.get(layerName,None),None)
		# End of create_materials
	def numberSubstratePartNameMap(self):
		materialCount={}
		for m in self.substratePartNameMap.keys():
			materialCount[self.substratePartNameMap[m]] = materialCount.get(self.substratePartNameMap[m],0) + 1
		multipleUsedMaterials = [m for m in materialCount.keys() if materialCount[m] > 1]
		for layer in self.substrateLayers:
			mat=self.substratePartNameMap.get(layer,None)
			if mat in multipleUsedMaterials:
				self.substratePartNameMap[layer]+=' '+str(materialCount[mat])
				materialCount[mat]-=1
	def setBoundaryConditions(self):
		pass
		# End of setBoundaryConditions
	def setPortWarnings(self,includeInvalidPorts):
		pass
		# End of setPortWarnings
	def initNetlists(self):
		netlistNames = ['net_0','net_1_P1_P2']
		if getSessionVersion(self.session) >= 5:
			self.session.initNetlists(netlistNames)
			return
		self.groupList = []
		try:
			for i in netlistNames:
				g = empro.core.ShortcutGroup(i)
				self.groupList.append(g)
		except:
			pass
	def addShortcut(self,netId,part):
		if getSessionVersion(self.session) >= 5:
			self.session.addShortcut(netId,part)
			return
		try:
			s = empro.core.Shortcut(part)
			self.groupList[netId].append(s)
		except:
			pass
	def addShortcutsToProject(self):
		if getSessionVersion(self.session) >= 5:
			self.session.addShortcutsToProject()
			return
		try:
			for g in self.groupList:
				empro.activeProject.shortcuts().append(g)
		except:
			pass

	def ads_import(self,usedFlow="ADS",topAssembly=None,demoMode=False,includeInvalidPorts=True,suppressNotification=False,materialForEachLayer=False):
		if getSessionVersion(self.session) >= 1:
			self.session.prepare_import()
		self.create_materials(materialForEachLayer=materialForEachLayer)
		self.create_parameters()
		if topAssembly != None:
			topAssemblyShouldBeAdded = False
		else:
			topAssembly = empro.geometry.Assembly()
			topAssembly.name = usedFlow+'_import'
			if demoMode:
				empro.activeProject.geometry.append(topAssembly)
				topAssemblyShouldBeAdded = False
			else:
				topAssemblyShouldBeAdded = True
		param_list = empro.activeProject.parameters
		param_list.setFormula( "lateralExtension", "0 mm")
		param_list.setFormula( "verticalExtension", "0 mm")
		self.create_bondwire_definitions()
		self.setBoundaryConditions()
		symbPinData = self.create_geometry(topAssembly)
		self.create_ports( topAssembly, includeInvalidPorts, symbPinData )
		if get_ads_import_version() >= 11 :
			Expr=empro.core.Expression
			if topAssembly != None:
				bbox_geom = topAssembly.boundingBox()
			else:
				bbox_geom = empro.activeProject.geometry.boundingBox()
			param_list = empro.activeProject.parameters
			param_list.setFormula( "xLowerBoundingBox", str(bbox_geom.lower.x.formula()) +" m - xLowerExtension" )
			param_list.setFormula( "xUpperBoundingBox", str(bbox_geom.upper.x.formula()) +" m + xUpperExtension" )
			param_list.setFormula( "yLowerBoundingBox", str(bbox_geom.lower.y.formula()) +" m - yLowerExtension" )
			param_list.setFormula( "yUpperBoundingBox", str(bbox_geom.upper.y.formula()) +" m + yUpperExtension" )
			param_list.setFormula( "zLowerBoundingBox", str(bbox_geom.lower.z.formula()) +" m - zLowerExtension" )
			param_list.setFormula( "zUpperBoundingBox", str(bbox_geom.upper.z.formula()) +" m + zUpperExtension" )
			param_list.setFormula( "toggleExtensionToBoundingBox", "1" )
		param_list.setFormula( "lateralExtension", "3.125 mm")
		param_list.setFormula("verticalExtension", "5 mm")
		self.addShortcutsToProject()
		if topAssemblyShouldBeAdded:
			empro.activeProject.geometry.append(topAssembly)
			self.session.adjust_view()
		self.session.renumber_waveguides()
		if getSessionVersion(self.session) >= 10:
			self.session.post_import()
		if not suppressNotification:
			self.session.notify_success()
		return self.session.warnings
		#End of ads_import method

	def create_geometry(self,topAssembly):
		V=empro.geometry.Vector3d
		L=empro.geometry.Line
		unit2meterFactor = 0.001
		symbPinData = None
		mask_heights=self.getMaskHeights()
		mask_heights_parameterized=self.getMaskHeightsParameterized()
		s3dc_files={}
		s3dc_files["libS3D.xml"]="eJyzCTZ2cbbjstGH0AAcBANS"
		if hasattr(self.session, "create_3d_components"):
			if get_ads_import_version() >= 11 :
				symbPinData = self.session.create_3d_components(s3dc_files, mask_heights, topAssembly, unit2meterFactor)
			else:
				try:
					self.session.create_3d_components(s3dc_files, mask_heights,topAssembly)
				except TypeError:
					self.session.create_3d_components(s3dc_files, mask_heights)
		assembly=empro.geometry.Assembly()
		assembly.name="bondwires"
		assembly=empro.geometry.Assembly()
		part=empro.geometry.Model()
		simBox = empro.geometry.Box( _createIfToggleExtensionToBoundingBoxExpression("xUpperBoundingBox-xLowerBoundingBox", "abs((-0.005-xLowerExtension)-(0.045+xUpperExtension))"), _createIfToggleExtensionToBoundingBoxExpression("zUpperBoundingBox-zLowerBoundingBox", "((((stack_tech_layer_7_Z) + (zUpperExtension)) - ((stack_tech_layer_1_Z) - (zLowerExtension))))"), _createIfToggleExtensionToBoundingBoxExpression("yUpperBoundingBox-yLowerBoundingBox" , " abs((-0.01-yLowerExtension)-(0.01+yUpperExtension))"))
		part.recipe.append(simBox)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(_createIfToggleExtensionToBoundingBoxExpression("(xUpperBoundingBox+xLowerBoundingBox)/2", "(0.045+xUpperExtension+-0.005-xLowerExtension)/2"), _createIfToggleExtensionToBoundingBoxExpression("(yUpperBoundingBox+yLowerBoundingBox)/2", "(0.01+yUpperExtension+-0.01-yLowerExtension)/2"), _createIfToggleExtensionToBoundingBoxExpression("zLowerBoundingBox","(((stack_tech_layer_1_Z) - (zLowerExtension)) - (0))")))
		part.name="Simulation box"
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=0
		empro.toolkit.applyMaterial(part,self.materials["simulation_box"])
		assembly.append(part)
		assembly.name="simulation_box"
		self.session.hide_part(assembly)
		topAssembly.append(assembly)
		self.session.adjust_view()
		assembly=empro.geometry.Assembly()
		pointString='0.045+xUpperExtension#-0.01-yLowerExtension;0.045+xUpperExtension#0.01+yUpperExtension;-0.005-xLowerExtension#0.01+yUpperExtension;-0.005-xLowerExtension#-0.01-yLowerExtension'
		sketch = self._create_sketch(pointString)
		sketch.constraintManager().append(empro.geometry.FixedPositionConstraint("vertex0",V(_createIfToggleExtensionToBoundingBoxExpression("xLowerBoundingBox","-0.005-xLowerExtension"),_createIfToggleExtensionToBoundingBoxExpression("yLowerBoundingBox","-0.01-yLowerExtension"),0)))
		sketch.constraintManager().append(empro.geometry.FixedPositionConstraint("vertex1",V(_createIfToggleExtensionToBoundingBoxExpression("xUpperBoundingBox","0.045+xUpperExtension"),_createIfToggleExtensionToBoundingBoxExpression("yLowerBoundingBox","-0.01-yLowerExtension"),0)))
		sketch.constraintManager().append(empro.geometry.FixedPositionConstraint("vertex2",V(_createIfToggleExtensionToBoundingBoxExpression("xUpperBoundingBox","0.045+xUpperExtension"),_createIfToggleExtensionToBoundingBoxExpression("yUpperBoundingBox","0.01+yUpperExtension"),0)))
		sketch.constraintManager().append(empro.geometry.FixedPositionConstraint("vertex3",V(_createIfToggleExtensionToBoundingBoxExpression("xLowerBoundingBox","-0.005-xLowerExtension"),_createIfToggleExtensionToBoundingBoxExpression("yUpperBoundingBox","0.01+yUpperExtension"),0)))
		part=empro.geometry.Model()
		part.recipe.append(empro.geometry.Extrude(sketch,"(stack_tech_layer_5_Z) - (stack_tech_layer_3_Z)",V(0,0,1)))
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(stack_tech_layer_3_Z) - (0)"))
		part.name=self.substratePartNameMap["__SubstrateLayer1"]
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=50
		empro.toolkit.applyMaterial(part,self.materials["__SubstrateLayer1"])
		self.session.hide_part(part)
		assembly.append(part)
		assembly.name="substrate"
		topAssembly.append(assembly)
		assembly=empro.geometry.Assembly()
		pointStrings=['0.045#-0.001;0.045#0.001;-0.005#0.001;-0.005#-0.001']
		part = self._create_extrude(pointStrings, "(mask_cond_Zmax) - (mask_cond_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 2)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=162
		empro.toolkit.applyMaterial(part,self.materials["cond"])
		assembly.append(part)
		self.addShortcut(1,part)
		self._update_geoProgress()
		self._setAssemblyMeshSettings(assembly,0,0,0)
		assembly.name="cond"
		topAssembly.append(assembly)
		assembly=empro.geometry.Assembly()
		pointStrings=['0.045#-0.01;0.045#0.01;-0.005#0.01;-0.005#-0.01']
		part = self._create_extrude(pointStrings, "(mask_cond2_Zmax) - (mask_cond2_Zmin)", up=False)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond2_Zmax) - (0)"))
		part.setAttribute('LtdLayerNumber', 3)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=162
		empro.toolkit.applyMaterial(part,self.materials["cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._setAssemblyMeshSettings(assembly,0,0,0)
		assembly.name="cond2"
		topAssembly.append(assembly)
		assembly=empro.geometry.Assembly()
		pointStrings=['-0.0048043#0.0087704;-0.0046743#0.0085757;-0.0044796#0.0084457;-0.00425#0.0084;-0.0038257#0.0085757;-0.00365#0.009;-0.0037304#0.0093;-0.00395#0.0095196;-0.00425#0.0096;-0.0044796#0.0095543;-0.0046743#0.0094243;-0.0048043#0.0092296;-0.00485#0.009']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['-0.0047543#-0.0092296;-0.0046243#-0.0094243;-0.0044296#-0.0095543;-0.0042#-0.0096;-0.0039#-0.0095196;-0.0036804#-0.0093;-0.0036#-0.009;-0.0037757#-0.0085757;-0.0042#-0.0084;-0.0044296#-0.0084457;-0.0046243#-0.0085757;-0.0047543#-0.0087704;-0.0048#-0.009']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['-0.0047543#0.0015704;-0.0046243#0.0013757;-0.0044296#0.0012457;-0.0042#0.0012;-0.0039704#0.0012457;-0.0037757#0.0013757;-0.0036457#0.0015704;-0.0036#0.0018;-0.0037757#0.0022243;-0.0042#0.0024;-0.0044296#0.0023543;-0.0046243#0.0022243;-0.0047543#0.0020296;-0.0048#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['-0.0047543#0.0042704;-0.0046243#0.0040757;-0.0044296#0.0039457;-0.0042#0.0039;-0.0037757#0.0040757;-0.0036#0.0045;-0.0037757#0.0049243;-0.0042#0.0051;-0.0044296#0.0050543;-0.0046243#0.0049243;-0.0047543#0.0047296;-0.0048#0.0045']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['-0.0047543#0.0069704;-0.0046243#0.0067757;-0.0044296#0.0066457;-0.0042#0.0066;-0.0037757#0.0067757;-0.0036#0.0072;-0.0037757#0.0076243;-0.0042#0.0078;-0.0044296#0.0077543;-0.0046243#0.0076243;-0.0047543#0.0074296;-0.0048#0.0072']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['-0.0046696#-0.0021;-0.00445#-0.0023196;-0.00415#-0.0024;-0.00385#-0.0023196;-0.0036304#-0.0021;-0.00355#-0.0018;-0.0035957#-0.0015704;-0.0037257#-0.0013757;-0.0039204#-0.0012457;-0.00415#-0.0012;-0.0043796#-0.0012457;-0.0045743#-0.0013757;-0.0047043#-0.0015704;-0.00475#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['-0.0045743#-0.0076243;-0.0043053#-0.0077796;-0.0039947#-0.0077796;-0.0037257#-0.0076243;-0.0035704#-0.0073553;-0.0035704#-0.0070447;-0.0037257#-0.0067757;-0.0039947#-0.0066204;-0.0043053#-0.0066204;-0.0045743#-0.0067757;-0.0047296#-0.0070447;-0.0047296#-0.0073553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['-0.0045743#-0.0049243;-0.0043053#-0.0050796;-0.0039947#-0.0050796;-0.0037257#-0.0049243;-0.0035704#-0.0046553;-0.0035704#-0.0043447;-0.0037257#-0.0040757;-0.0039947#-0.0039204;-0.0043053#-0.0039204;-0.0045743#-0.0040757;-0.0047296#-0.0043447;-0.0047296#-0.0046553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['-0.0020696#0.0087;-0.0017552#0.0084362;-0.0013448#0.0084362;-0.0010304#0.0087;-0.0009591#0.0091042;-0.0011643#0.0094596;-0.00155#0.0096;-0.0019357#0.0094596;-0.0021409#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['-0.0020543#0.0015704;-0.0019243#0.0013757;-0.0017296#0.0012457;-0.0015#0.0012;-0.0012704#0.0012457;-0.0010757#0.0013757;-0.0009457#0.0015704;-0.0009#0.0018;-0.0010757#0.0022243;-0.0015#0.0024;-0.0019243#0.0022243;-0.0021#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['-0.0019243#-0.0094243;-0.0016553#-0.0095796;-0.0013447#-0.0095796;-0.0010757#-0.0094243;-0.0009204#-0.0091553;-0.0009204#-0.0088447;-0.0010757#-0.0085757;-0.0013447#-0.0084204;-0.0016553#-0.0084204;-0.0019243#-0.0085757;-0.0020796#-0.0088447;-0.0020796#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['-0.0017296#0.0039457;-0.0012704#0.0039457;-0.0009457#0.0042704;-0.0009457#0.0047296;-0.0012704#0.0050543;-0.0017296#0.0050543;-0.0020543#0.0047296;-0.0020543#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['-0.0017296#0.0066457;-0.0012704#0.0066457;-0.0009457#0.0069704;-0.0009457#0.0074296;-0.0012704#0.0077543;-0.0017296#0.0077543;-0.0020543#0.0074296;-0.0020543#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['-0.0018743#-0.0022243;-0.00145#-0.0024;-0.0010257#-0.0022243;-0.00085#-0.0018;-0.0008957#-0.0015704;-0.0010257#-0.0013757;-0.0012204#-0.0012457;-0.00145#-0.0012;-0.0016796#-0.0012457;-0.0018743#-0.0013757;-0.0020043#-0.0015704;-0.00205#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['-0.0016796#-0.0077543;-0.0012204#-0.0077543;-0.0008957#-0.0074296;-0.0008957#-0.0069704;-0.0012204#-0.0066457;-0.0016796#-0.0066457;-0.0020043#-0.0069704;-0.0020043#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['-0.0016796#-0.0050543;-0.0012204#-0.0050543;-0.0008957#-0.0047296;-0.0008957#-0.0042704;-0.0012204#-0.0039457;-0.0016796#-0.0039457;-0.0020043#-0.0042704;-0.0020043#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0006304#0.0087;0.0009448#0.0084362;0.0013552#0.0084362;0.0016696#0.0087;0.0017409#0.0091042;0.0015357#0.0094596;0.00115#0.0096;0.0007643#0.0094596;0.0005591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0006457#0.0015704;0.0007757#0.0013757;0.0009704#0.0012457;0.0012#0.0012;0.0014296#0.0012457;0.0016243#0.0013757;0.0017543#0.0015704;0.0018#0.0018;0.0016243#0.0022243;0.0012#0.0024;0.0007757#0.0022243;0.0006#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0007757#-0.0094243;0.0010447#-0.0095796;0.0013553#-0.0095796;0.0016243#-0.0094243;0.0017796#-0.0091553;0.0017796#-0.0088447;0.0016243#-0.0085757;0.0013553#-0.0084204;0.0010447#-0.0084204;0.0007757#-0.0085757;0.0006204#-0.0088447;0.0006204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0009704#0.0039457;0.0014296#0.0039457;0.0017543#0.0042704;0.0017543#0.0047296;0.0014296#0.0050543;0.0009704#0.0050543;0.0006457#0.0047296;0.0006457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0009704#0.0066457;0.0014296#0.0066457;0.0017543#0.0069704;0.0017543#0.0074296;0.0014296#0.0077543;0.0009704#0.0077543;0.0006457#0.0074296;0.0006457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0008257#-0.0022243;0.00125#-0.0024;0.0016743#-0.0022243;0.00185#-0.0018;0.0018043#-0.0015704;0.0016743#-0.0013757;0.0014796#-0.0012457;0.00125#-0.0012;0.0010204#-0.0012457;0.0008257#-0.0013757;0.0006957#-0.0015704;0.00065#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0010204#-0.0077543;0.0014796#-0.0077543;0.0018043#-0.0074296;0.0018043#-0.0069704;0.0014796#-0.0066457;0.0010204#-0.0066457;0.0006957#-0.0069704;0.0006957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0010204#-0.0050543;0.0014796#-0.0050543;0.0018043#-0.0047296;0.0018043#-0.0042704;0.0014796#-0.0039457;0.0010204#-0.0039457;0.0006957#-0.0042704;0.0006957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0033304#0.0087;0.0036448#0.0084362;0.0040552#0.0084362;0.0043696#0.0087;0.0044409#0.0091042;0.0042357#0.0094596;0.00385#0.0096;0.0034643#0.0094596;0.0032591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0033457#0.0015704;0.0034757#0.0013757;0.0036704#0.0012457;0.0039#0.0012;0.0041296#0.0012457;0.0043243#0.0013757;0.0044543#0.0015704;0.0045#0.0018;0.0043243#0.0022243;0.0039#0.0024;0.0034757#0.0022243;0.0033#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0034757#-0.0094243;0.0037447#-0.0095796;0.0040553#-0.0095796;0.0043243#-0.0094243;0.0044796#-0.0091553;0.0044796#-0.0088447;0.0043243#-0.0085757;0.0040553#-0.0084204;0.0037447#-0.0084204;0.0034757#-0.0085757;0.0033204#-0.0088447;0.0033204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0036704#0.0039457;0.0041296#0.0039457;0.0044543#0.0042704;0.0044543#0.0047296;0.0041296#0.0050543;0.0036704#0.0050543;0.0033457#0.0047296;0.0033457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0036704#0.0066457;0.0041296#0.0066457;0.0044543#0.0069704;0.0044543#0.0074296;0.0041296#0.0077543;0.0036704#0.0077543;0.0033457#0.0074296;0.0033457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0035257#-0.0022243;0.00395#-0.0024;0.0043743#-0.0022243;0.00455#-0.0018;0.0045043#-0.0015704;0.0043743#-0.0013757;0.0041796#-0.0012457;0.00395#-0.0012;0.0037204#-0.0012457;0.0035257#-0.0013757;0.0033957#-0.0015704;0.00335#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0037204#-0.0077543;0.0041796#-0.0077543;0.0045043#-0.0074296;0.0045043#-0.0069704;0.0041796#-0.0066457;0.0037204#-0.0066457;0.0033957#-0.0069704;0.0033957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0037204#-0.0050543;0.0041796#-0.0050543;0.0045043#-0.0047296;0.0045043#-0.0042704;0.0041796#-0.0039457;0.0037204#-0.0039457;0.0033957#-0.0042704;0.0033957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0060304#0.0087;0.0063448#0.0084362;0.0067552#0.0084362;0.0070696#0.0087;0.0071409#0.0091042;0.0069357#0.0094596;0.00655#0.0096;0.0061643#0.0094596;0.0059591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0060457#0.0015704;0.0061757#0.0013757;0.0063704#0.0012457;0.0066#0.0012;0.0068296#0.0012457;0.0070243#0.0013757;0.0071543#0.0015704;0.0072#0.0018;0.0070243#0.0022243;0.0066#0.0024;0.0061757#0.0022243;0.006#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0061757#-0.0094243;0.0064447#-0.0095796;0.0067553#-0.0095796;0.0070243#-0.0094243;0.0071796#-0.0091553;0.0071796#-0.0088447;0.0070243#-0.0085757;0.0067553#-0.0084204;0.0064447#-0.0084204;0.0061757#-0.0085757;0.0060204#-0.0088447;0.0060204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0063704#0.0039457;0.0068296#0.0039457;0.0071543#0.0042704;0.0071543#0.0047296;0.0068296#0.0050543;0.0063704#0.0050543;0.0060457#0.0047296;0.0060457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0063704#0.0066457;0.0068296#0.0066457;0.0071543#0.0069704;0.0071543#0.0074296;0.0068296#0.0077543;0.0063704#0.0077543;0.0060457#0.0074296;0.0060457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0062257#-0.0022243;0.00665#-0.0024;0.0070743#-0.0022243;0.00725#-0.0018;0.0072043#-0.0015704;0.0070743#-0.0013757;0.0068796#-0.0012457;0.00665#-0.0012;0.0064204#-0.0012457;0.0062257#-0.0013757;0.0060957#-0.0015704;0.00605#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0064204#-0.0077543;0.0068796#-0.0077543;0.0072043#-0.0074296;0.0072043#-0.0069704;0.0068796#-0.0066457;0.0064204#-0.0066457;0.0060957#-0.0069704;0.0060957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0064204#-0.0050543;0.0068796#-0.0050543;0.0072043#-0.0047296;0.0072043#-0.0042704;0.0068796#-0.0039457;0.0064204#-0.0039457;0.0060957#-0.0042704;0.0060957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0087304#0.0087;0.0090448#0.0084362;0.0094552#0.0084362;0.0097696#0.0087;0.0098409#0.0091042;0.0096357#0.0094596;0.00925#0.0096;0.0088643#0.0094596;0.0086591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0087457#0.0015704;0.0088757#0.0013757;0.0090704#0.0012457;0.0093#0.0012;0.0095296#0.0012457;0.0097243#0.0013757;0.0098543#0.0015704;0.0099#0.0018;0.0097243#0.0022243;0.0093#0.0024;0.0088757#0.0022243;0.0087#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0088757#-0.0094243;0.0091447#-0.0095796;0.0094553#-0.0095796;0.0097243#-0.0094243;0.0098796#-0.0091553;0.0098796#-0.0088447;0.0097243#-0.0085757;0.0094553#-0.0084204;0.0091447#-0.0084204;0.0088757#-0.0085757;0.0087204#-0.0088447;0.0087204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0090704#0.0039457;0.0095296#0.0039457;0.0098543#0.0042704;0.0098543#0.0047296;0.0095296#0.0050543;0.0090704#0.0050543;0.0087457#0.0047296;0.0087457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0090704#0.0066457;0.0095296#0.0066457;0.0098543#0.0069704;0.0098543#0.0074296;0.0095296#0.0077543;0.0090704#0.0077543;0.0087457#0.0074296;0.0087457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0089257#-0.0022243;0.00935#-0.0024;0.0097743#-0.0022243;0.00995#-0.0018;0.0099043#-0.0015704;0.0097743#-0.0013757;0.0095796#-0.0012457;0.00935#-0.0012;0.0091204#-0.0012457;0.0089257#-0.0013757;0.0087957#-0.0015704;0.00875#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0091204#-0.0077543;0.0095796#-0.0077543;0.0099043#-0.0074296;0.0099043#-0.0069704;0.0095796#-0.0066457;0.0091204#-0.0066457;0.0087957#-0.0069704;0.0087957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0091204#-0.0050543;0.0095796#-0.0050543;0.0099043#-0.0047296;0.0099043#-0.0042704;0.0095796#-0.0039457;0.0091204#-0.0039457;0.0087957#-0.0042704;0.0087957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0114304#0.0087;0.0117448#0.0084362;0.0121552#0.0084362;0.0124696#0.0087;0.0125409#0.0091042;0.0123357#0.0094596;0.01195#0.0096;0.0115643#0.0094596;0.0113591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0114457#0.0015704;0.0115757#0.0013757;0.0117704#0.0012457;0.012#0.0012;0.0122296#0.0012457;0.0124243#0.0013757;0.0125543#0.0015704;0.0126#0.0018;0.0124243#0.0022243;0.012#0.0024;0.0115757#0.0022243;0.0114#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0115757#-0.0094243;0.0118447#-0.0095796;0.0121553#-0.0095796;0.0124243#-0.0094243;0.0125796#-0.0091553;0.0125796#-0.0088447;0.0124243#-0.0085757;0.0121553#-0.0084204;0.0118447#-0.0084204;0.0115757#-0.0085757;0.0114204#-0.0088447;0.0114204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0117704#0.0039457;0.0122296#0.0039457;0.0125543#0.0042704;0.0125543#0.0047296;0.0122296#0.0050543;0.0117704#0.0050543;0.0114457#0.0047296;0.0114457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0117704#0.0066457;0.0122296#0.0066457;0.0125543#0.0069704;0.0125543#0.0074296;0.0122296#0.0077543;0.0117704#0.0077543;0.0114457#0.0074296;0.0114457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0116257#-0.0022243;0.01205#-0.0024;0.0124743#-0.0022243;0.01265#-0.0018;0.0126043#-0.0015704;0.0124743#-0.0013757;0.0122796#-0.0012457;0.01205#-0.0012;0.0118204#-0.0012457;0.0116257#-0.0013757;0.0114957#-0.0015704;0.01145#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0118204#-0.0077543;0.0122796#-0.0077543;0.0126043#-0.0074296;0.0126043#-0.0069704;0.0122796#-0.0066457;0.0118204#-0.0066457;0.0114957#-0.0069704;0.0114957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0118204#-0.0050543;0.0122796#-0.0050543;0.0126043#-0.0047296;0.0126043#-0.0042704;0.0122796#-0.0039457;0.0118204#-0.0039457;0.0114957#-0.0042704;0.0114957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0141304#0.0087;0.0144448#0.0084362;0.0148552#0.0084362;0.0151696#0.0087;0.0152409#0.0091042;0.0150357#0.0094596;0.01465#0.0096;0.0142643#0.0094596;0.0140591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0141457#0.0015704;0.0142757#0.0013757;0.0144704#0.0012457;0.0147#0.0012;0.0149296#0.0012457;0.0151243#0.0013757;0.0152543#0.0015704;0.0153#0.0018;0.0151243#0.0022243;0.0147#0.0024;0.0142757#0.0022243;0.0141#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0142757#-0.0094243;0.0145447#-0.0095796;0.0148553#-0.0095796;0.0151243#-0.0094243;0.0152796#-0.0091553;0.0152796#-0.0088447;0.0151243#-0.0085757;0.0148553#-0.0084204;0.0145447#-0.0084204;0.0142757#-0.0085757;0.0141204#-0.0088447;0.0141204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0144704#0.0039457;0.0149296#0.0039457;0.0152543#0.0042704;0.0152543#0.0047296;0.0149296#0.0050543;0.0144704#0.0050543;0.0141457#0.0047296;0.0141457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0144704#0.0066457;0.0149296#0.0066457;0.0152543#0.0069704;0.0152543#0.0074296;0.0149296#0.0077543;0.0144704#0.0077543;0.0141457#0.0074296;0.0141457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0143257#-0.0022243;0.01475#-0.0024;0.0151743#-0.0022243;0.01535#-0.0018;0.0153043#-0.0015704;0.0151743#-0.0013757;0.0149796#-0.0012457;0.01475#-0.0012;0.0145204#-0.0012457;0.0143257#-0.0013757;0.0141957#-0.0015704;0.01415#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0145204#-0.0077543;0.0149796#-0.0077543;0.0153043#-0.0074296;0.0153043#-0.0069704;0.0149796#-0.0066457;0.0145204#-0.0066457;0.0141957#-0.0069704;0.0141957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0145204#-0.0050543;0.0149796#-0.0050543;0.0153043#-0.0047296;0.0153043#-0.0042704;0.0149796#-0.0039457;0.0145204#-0.0039457;0.0141957#-0.0042704;0.0141957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0168304#0.0087;0.0171448#0.0084362;0.0175552#0.0084362;0.0178696#0.0087;0.0179409#0.0091042;0.0177357#0.0094596;0.01735#0.0096;0.0169643#0.0094596;0.0167591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0168457#0.0015704;0.0169757#0.0013757;0.0171704#0.0012457;0.0174#0.0012;0.0176296#0.0012457;0.0178243#0.0013757;0.0179543#0.0015704;0.018#0.0018;0.0178243#0.0022243;0.0174#0.0024;0.0169757#0.0022243;0.0168#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0169757#-0.0094243;0.0172447#-0.0095796;0.0175553#-0.0095796;0.0178243#-0.0094243;0.0179796#-0.0091553;0.0179796#-0.0088447;0.0178243#-0.0085757;0.0175553#-0.0084204;0.0172447#-0.0084204;0.0169757#-0.0085757;0.0168204#-0.0088447;0.0168204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0171704#0.0039457;0.0176296#0.0039457;0.0179543#0.0042704;0.0179543#0.0047296;0.0176296#0.0050543;0.0171704#0.0050543;0.0168457#0.0047296;0.0168457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0171704#0.0066457;0.0176296#0.0066457;0.0179543#0.0069704;0.0179543#0.0074296;0.0176296#0.0077543;0.0171704#0.0077543;0.0168457#0.0074296;0.0168457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0170257#-0.0022243;0.01745#-0.0024;0.0178743#-0.0022243;0.01805#-0.0018;0.0180043#-0.0015704;0.0178743#-0.0013757;0.0176796#-0.0012457;0.01745#-0.0012;0.0172204#-0.0012457;0.0170257#-0.0013757;0.0168957#-0.0015704;0.01685#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0172204#-0.0077543;0.0176796#-0.0077543;0.0180043#-0.0074296;0.0180043#-0.0069704;0.0176796#-0.0066457;0.0172204#-0.0066457;0.0168957#-0.0069704;0.0168957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0172204#-0.0050543;0.0176796#-0.0050543;0.0180043#-0.0047296;0.0180043#-0.0042704;0.0176796#-0.0039457;0.0172204#-0.0039457;0.0168957#-0.0042704;0.0168957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0195304#0.0087;0.0198448#0.0084362;0.0202552#0.0084362;0.0205696#0.0087;0.0206409#0.0091042;0.0204357#0.0094596;0.02005#0.0096;0.0196643#0.0094596;0.0194591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0195457#0.0015704;0.0196757#0.0013757;0.0198704#0.0012457;0.0201#0.0012;0.0203296#0.0012457;0.0205243#0.0013757;0.0206543#0.0015704;0.0207#0.0018;0.0205243#0.0022243;0.0201#0.0024;0.0196757#0.0022243;0.0195#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0196757#-0.0094243;0.0199447#-0.0095796;0.0202553#-0.0095796;0.0205243#-0.0094243;0.0206796#-0.0091553;0.0206796#-0.0088447;0.0205243#-0.0085757;0.0202553#-0.0084204;0.0199447#-0.0084204;0.0196757#-0.0085757;0.0195204#-0.0088447;0.0195204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0198704#0.0039457;0.0203296#0.0039457;0.0206543#0.0042704;0.0206543#0.0047296;0.0203296#0.0050543;0.0198704#0.0050543;0.0195457#0.0047296;0.0195457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0198704#0.0066457;0.0203296#0.0066457;0.0206543#0.0069704;0.0206543#0.0074296;0.0203296#0.0077543;0.0198704#0.0077543;0.0195457#0.0074296;0.0195457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0197257#-0.0022243;0.02015#-0.0024;0.0205743#-0.0022243;0.02075#-0.0018;0.0207043#-0.0015704;0.0205743#-0.0013757;0.0203796#-0.0012457;0.02015#-0.0012;0.0199204#-0.0012457;0.0197257#-0.0013757;0.0195957#-0.0015704;0.01955#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0199204#-0.0077543;0.0203796#-0.0077543;0.0207043#-0.0074296;0.0207043#-0.0069704;0.0203796#-0.0066457;0.0199204#-0.0066457;0.0195957#-0.0069704;0.0195957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0199204#-0.0050543;0.0203796#-0.0050543;0.0207043#-0.0047296;0.0207043#-0.0042704;0.0203796#-0.0039457;0.0199204#-0.0039457;0.0195957#-0.0042704;0.0195957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0222304#0.0087;0.0225448#0.0084362;0.0229552#0.0084362;0.0232696#0.0087;0.0233409#0.0091042;0.0231357#0.0094596;0.02275#0.0096;0.0223643#0.0094596;0.0221591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0222457#0.0015704;0.0223757#0.0013757;0.0225704#0.0012457;0.0228#0.0012;0.0230296#0.0012457;0.0232243#0.0013757;0.0233543#0.0015704;0.0234#0.0018;0.0232243#0.0022243;0.0228#0.0024;0.0223757#0.0022243;0.0222#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0223757#-0.0094243;0.0226447#-0.0095796;0.0229553#-0.0095796;0.0232243#-0.0094243;0.0233796#-0.0091553;0.0233796#-0.0088447;0.0232243#-0.0085757;0.0229553#-0.0084204;0.0226447#-0.0084204;0.0223757#-0.0085757;0.0222204#-0.0088447;0.0222204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0225704#0.0039457;0.0230296#0.0039457;0.0233543#0.0042704;0.0233543#0.0047296;0.0230296#0.0050543;0.0225704#0.0050543;0.0222457#0.0047296;0.0222457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0225704#0.0066457;0.0230296#0.0066457;0.0233543#0.0069704;0.0233543#0.0074296;0.0230296#0.0077543;0.0225704#0.0077543;0.0222457#0.0074296;0.0222457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0224257#-0.0022243;0.02285#-0.0024;0.0232743#-0.0022243;0.02345#-0.0018;0.0234043#-0.0015704;0.0232743#-0.0013757;0.0230796#-0.0012457;0.02285#-0.0012;0.0226204#-0.0012457;0.0224257#-0.0013757;0.0222957#-0.0015704;0.02225#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0226204#-0.0077543;0.0230796#-0.0077543;0.0234043#-0.0074296;0.0234043#-0.0069704;0.0230796#-0.0066457;0.0226204#-0.0066457;0.0222957#-0.0069704;0.0222957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0226204#-0.0050543;0.0230796#-0.0050543;0.0234043#-0.0047296;0.0234043#-0.0042704;0.0230796#-0.0039457;0.0226204#-0.0039457;0.0222957#-0.0042704;0.0222957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0249304#0.0087;0.0252448#0.0084362;0.0256552#0.0084362;0.0259696#0.0087;0.0260409#0.0091042;0.0258357#0.0094596;0.02545#0.0096;0.0250643#0.0094596;0.0248591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0249457#0.0015704;0.0250757#0.0013757;0.0252704#0.0012457;0.0255#0.0012;0.0257296#0.0012457;0.0259243#0.0013757;0.0260543#0.0015704;0.0261#0.0018;0.0259243#0.0022243;0.0255#0.0024;0.0250757#0.0022243;0.0249#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0250757#-0.0094243;0.0253447#-0.0095796;0.0256553#-0.0095796;0.0259243#-0.0094243;0.0260796#-0.0091553;0.0260796#-0.0088447;0.0259243#-0.0085757;0.0256553#-0.0084204;0.0253447#-0.0084204;0.0250757#-0.0085757;0.0249204#-0.0088447;0.0249204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0252704#0.0039457;0.0257296#0.0039457;0.0260543#0.0042704;0.0260543#0.0047296;0.0257296#0.0050543;0.0252704#0.0050543;0.0249457#0.0047296;0.0249457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0252704#0.0066457;0.0257296#0.0066457;0.0260543#0.0069704;0.0260543#0.0074296;0.0257296#0.0077543;0.0252704#0.0077543;0.0249457#0.0074296;0.0249457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0251257#-0.0022243;0.02555#-0.0024;0.0259743#-0.0022243;0.02615#-0.0018;0.0261043#-0.0015704;0.0259743#-0.0013757;0.0257796#-0.0012457;0.02555#-0.0012;0.0253204#-0.0012457;0.0251257#-0.0013757;0.0249957#-0.0015704;0.02495#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0253204#-0.0077543;0.0257796#-0.0077543;0.0261043#-0.0074296;0.0261043#-0.0069704;0.0257796#-0.0066457;0.0253204#-0.0066457;0.0249957#-0.0069704;0.0249957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0253204#-0.0050543;0.0257796#-0.0050543;0.0261043#-0.0047296;0.0261043#-0.0042704;0.0257796#-0.0039457;0.0253204#-0.0039457;0.0249957#-0.0042704;0.0249957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0276304#0.0087;0.0279448#0.0084362;0.0283552#0.0084362;0.0286696#0.0087;0.0287409#0.0091042;0.0285357#0.0094596;0.02815#0.0096;0.0277643#0.0094596;0.0275591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0276457#0.0015704;0.0277757#0.0013757;0.0279704#0.0012457;0.0282#0.0012;0.0284296#0.0012457;0.0286243#0.0013757;0.0287543#0.0015704;0.0288#0.0018;0.0286243#0.0022243;0.0282#0.0024;0.0277757#0.0022243;0.0276#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0277757#-0.0094243;0.0280447#-0.0095796;0.0283553#-0.0095796;0.0286243#-0.0094243;0.0287796#-0.0091553;0.0287796#-0.0088447;0.0286243#-0.0085757;0.0283553#-0.0084204;0.0280447#-0.0084204;0.0277757#-0.0085757;0.0276204#-0.0088447;0.0276204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0279704#0.0039457;0.0284296#0.0039457;0.0287543#0.0042704;0.0287543#0.0047296;0.0284296#0.0050543;0.0279704#0.0050543;0.0276457#0.0047296;0.0276457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0279704#0.0066457;0.0284296#0.0066457;0.0287543#0.0069704;0.0287543#0.0074296;0.0284296#0.0077543;0.0279704#0.0077543;0.0276457#0.0074296;0.0276457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0278257#-0.0022243;0.02825#-0.0024;0.0286743#-0.0022243;0.02885#-0.0018;0.0288043#-0.0015704;0.0286743#-0.0013757;0.0284796#-0.0012457;0.02825#-0.0012;0.0280204#-0.0012457;0.0278257#-0.0013757;0.0276957#-0.0015704;0.02765#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0280204#-0.0077543;0.0284796#-0.0077543;0.0288043#-0.0074296;0.0288043#-0.0069704;0.0284796#-0.0066457;0.0280204#-0.0066457;0.0276957#-0.0069704;0.0276957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0280204#-0.0050543;0.0284796#-0.0050543;0.0288043#-0.0047296;0.0288043#-0.0042704;0.0284796#-0.0039457;0.0280204#-0.0039457;0.0276957#-0.0042704;0.0276957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0303304#0.0087;0.0306448#0.0084362;0.0310552#0.0084362;0.0313696#0.0087;0.0314409#0.0091042;0.0312357#0.0094596;0.03085#0.0096;0.0304643#0.0094596;0.0302591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0303457#0.0015704;0.0304757#0.0013757;0.0306704#0.0012457;0.0309#0.0012;0.0311296#0.0012457;0.0313243#0.0013757;0.0314543#0.0015704;0.0315#0.0018;0.0313243#0.0022243;0.0309#0.0024;0.0304757#0.0022243;0.0303#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0304757#-0.0094243;0.0307447#-0.0095796;0.0310553#-0.0095796;0.0313243#-0.0094243;0.0314796#-0.0091553;0.0314796#-0.0088447;0.0313243#-0.0085757;0.0310553#-0.0084204;0.0307447#-0.0084204;0.0304757#-0.0085757;0.0303204#-0.0088447;0.0303204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0306704#0.0039457;0.0311296#0.0039457;0.0314543#0.0042704;0.0314543#0.0047296;0.0311296#0.0050543;0.0306704#0.0050543;0.0303457#0.0047296;0.0303457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0306704#0.0066457;0.0311296#0.0066457;0.0314543#0.0069704;0.0314543#0.0074296;0.0311296#0.0077543;0.0306704#0.0077543;0.0303457#0.0074296;0.0303457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0305257#-0.0022243;0.03095#-0.0024;0.0313743#-0.0022243;0.03155#-0.0018;0.0315043#-0.0015704;0.0313743#-0.0013757;0.0311796#-0.0012457;0.03095#-0.0012;0.0307204#-0.0012457;0.0305257#-0.0013757;0.0303957#-0.0015704;0.03035#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0307204#-0.0077543;0.0311796#-0.0077543;0.0315043#-0.0074296;0.0315043#-0.0069704;0.0311796#-0.0066457;0.0307204#-0.0066457;0.0303957#-0.0069704;0.0303957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0307204#-0.0050543;0.0311796#-0.0050543;0.0315043#-0.0047296;0.0315043#-0.0042704;0.0311796#-0.0039457;0.0307204#-0.0039457;0.0303957#-0.0042704;0.0303957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0330304#0.0087;0.0333448#0.0084362;0.0337552#0.0084362;0.0340696#0.0087;0.0341409#0.0091042;0.0339357#0.0094596;0.03355#0.0096;0.0331643#0.0094596;0.0329591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0330457#0.0015704;0.0331757#0.0013757;0.0333704#0.0012457;0.0336#0.0012;0.0338296#0.0012457;0.0340243#0.0013757;0.0341543#0.0015704;0.0342#0.0018;0.0340243#0.0022243;0.0336#0.0024;0.0331757#0.0022243;0.033#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0331757#-0.0094243;0.0334447#-0.0095796;0.0337553#-0.0095796;0.0340243#-0.0094243;0.0341796#-0.0091553;0.0341796#-0.0088447;0.0340243#-0.0085757;0.0337553#-0.0084204;0.0334447#-0.0084204;0.0331757#-0.0085757;0.0330204#-0.0088447;0.0330204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0333704#0.0039457;0.0338296#0.0039457;0.0341543#0.0042704;0.0341543#0.0047296;0.0338296#0.0050543;0.0333704#0.0050543;0.0330457#0.0047296;0.0330457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0333704#0.0066457;0.0338296#0.0066457;0.0341543#0.0069704;0.0341543#0.0074296;0.0338296#0.0077543;0.0333704#0.0077543;0.0330457#0.0074296;0.0330457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0332257#-0.0022243;0.03365#-0.0024;0.0340743#-0.0022243;0.03425#-0.0018;0.0342043#-0.0015704;0.0340743#-0.0013757;0.0338796#-0.0012457;0.03365#-0.0012;0.0334204#-0.0012457;0.0332257#-0.0013757;0.0330957#-0.0015704;0.03305#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0334204#-0.0077543;0.0338796#-0.0077543;0.0342043#-0.0074296;0.0342043#-0.0069704;0.0338796#-0.0066457;0.0334204#-0.0066457;0.0330957#-0.0069704;0.0330957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0334204#-0.0050543;0.0338796#-0.0050543;0.0342043#-0.0047296;0.0342043#-0.0042704;0.0338796#-0.0039457;0.0334204#-0.0039457;0.0330957#-0.0042704;0.0330957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0357304#0.0087;0.0360448#0.0084362;0.0364552#0.0084362;0.0367696#0.0087;0.0368409#0.0091042;0.0366357#0.0094596;0.03625#0.0096;0.0358643#0.0094596;0.0356591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0357457#0.0015704;0.0358757#0.0013757;0.0360704#0.0012457;0.0363#0.0012;0.0365296#0.0012457;0.0367243#0.0013757;0.0368543#0.0015704;0.0369#0.0018;0.0367243#0.0022243;0.0363#0.0024;0.0358757#0.0022243;0.0357#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0358757#-0.0094243;0.0361447#-0.0095796;0.0364553#-0.0095796;0.0367243#-0.0094243;0.0368796#-0.0091553;0.0368796#-0.0088447;0.0367243#-0.0085757;0.0364553#-0.0084204;0.0361447#-0.0084204;0.0358757#-0.0085757;0.0357204#-0.0088447;0.0357204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0360704#0.0039457;0.0365296#0.0039457;0.0368543#0.0042704;0.0368543#0.0047296;0.0365296#0.0050543;0.0360704#0.0050543;0.0357457#0.0047296;0.0357457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0360704#0.0066457;0.0365296#0.0066457;0.0368543#0.0069704;0.0368543#0.0074296;0.0365296#0.0077543;0.0360704#0.0077543;0.0357457#0.0074296;0.0357457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0359257#-0.0022243;0.03635#-0.0024;0.0367743#-0.0022243;0.03695#-0.0018;0.0369043#-0.0015704;0.0367743#-0.0013757;0.0365796#-0.0012457;0.03635#-0.0012;0.0361204#-0.0012457;0.0359257#-0.0013757;0.0357957#-0.0015704;0.03575#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0361204#-0.0077543;0.0365796#-0.0077543;0.0369043#-0.0074296;0.0369043#-0.0069704;0.0365796#-0.0066457;0.0361204#-0.0066457;0.0357957#-0.0069704;0.0357957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0361204#-0.0050543;0.0365796#-0.0050543;0.0369043#-0.0047296;0.0369043#-0.0042704;0.0365796#-0.0039457;0.0361204#-0.0039457;0.0357957#-0.0042704;0.0357957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0384304#0.0087;0.0387448#0.0084362;0.0391552#0.0084362;0.0394696#0.0087;0.0395409#0.0091042;0.0393357#0.0094596;0.03895#0.0096;0.0385643#0.0094596;0.0383591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0384457#0.0015704;0.0385757#0.0013757;0.0387704#0.0012457;0.039#0.0012;0.0392296#0.0012457;0.0394243#0.0013757;0.0395543#0.0015704;0.0396#0.0018;0.0394243#0.0022243;0.039#0.0024;0.0385757#0.0022243;0.0384#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0385757#-0.0094243;0.0388447#-0.0095796;0.0391553#-0.0095796;0.0394243#-0.0094243;0.0395796#-0.0091553;0.0395796#-0.0088447;0.0394243#-0.0085757;0.0391553#-0.0084204;0.0388447#-0.0084204;0.0385757#-0.0085757;0.0384204#-0.0088447;0.0384204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0387704#0.0039457;0.0392296#0.0039457;0.0395543#0.0042704;0.0395543#0.0047296;0.0392296#0.0050543;0.0387704#0.0050543;0.0384457#0.0047296;0.0384457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0387704#0.0066457;0.0392296#0.0066457;0.0395543#0.0069704;0.0395543#0.0074296;0.0392296#0.0077543;0.0387704#0.0077543;0.0384457#0.0074296;0.0384457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0386257#-0.0022243;0.03905#-0.0024;0.0394743#-0.0022243;0.03965#-0.0018;0.0396043#-0.0015704;0.0394743#-0.0013757;0.0392796#-0.0012457;0.03905#-0.0012;0.0388204#-0.0012457;0.0386257#-0.0013757;0.0384957#-0.0015704;0.03845#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0388204#-0.0077543;0.0392796#-0.0077543;0.0396043#-0.0074296;0.0396043#-0.0069704;0.0392796#-0.0066457;0.0388204#-0.0066457;0.0384957#-0.0069704;0.0384957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0388204#-0.0050543;0.0392796#-0.0050543;0.0396043#-0.0047296;0.0396043#-0.0042704;0.0392796#-0.0039457;0.0388204#-0.0039457;0.0384957#-0.0042704;0.0384957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0411304#0.0087;0.0414448#0.0084362;0.0418552#0.0084362;0.0421696#0.0087;0.0422409#0.0091042;0.0420357#0.0094596;0.04165#0.0096;0.0412643#0.0094596;0.0410591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0411457#0.0015704;0.0412757#0.0013757;0.0414704#0.0012457;0.0417#0.0012;0.0419296#0.0012457;0.0421243#0.0013757;0.0422543#0.0015704;0.0423#0.0018;0.0421243#0.0022243;0.0417#0.0024;0.0412757#0.0022243;0.0411#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0412757#-0.0094243;0.0415447#-0.0095796;0.0418553#-0.0095796;0.0421243#-0.0094243;0.0422796#-0.0091553;0.0422796#-0.0088447;0.0421243#-0.0085757;0.0418553#-0.0084204;0.0415447#-0.0084204;0.0412757#-0.0085757;0.0411204#-0.0088447;0.0411204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0414704#0.0039457;0.0419296#0.0039457;0.0422543#0.0042704;0.0422543#0.0047296;0.0419296#0.0050543;0.0414704#0.0050543;0.0411457#0.0047296;0.0411457#0.0042704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0414704#0.0066457;0.0419296#0.0066457;0.0422543#0.0069704;0.0422543#0.0074296;0.0419296#0.0077543;0.0414704#0.0077543;0.0411457#0.0074296;0.0411457#0.0069704']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0413257#-0.0022243;0.04175#-0.0024;0.0421743#-0.0022243;0.04235#-0.0018;0.0423043#-0.0015704;0.0421743#-0.0013757;0.0419796#-0.0012457;0.04175#-0.0012;0.0415204#-0.0012457;0.0413257#-0.0013757;0.0411957#-0.0015704;0.04115#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0415204#-0.0077543;0.0419796#-0.0077543;0.0423043#-0.0074296;0.0423043#-0.0069704;0.0419796#-0.0066457;0.0415204#-0.0066457;0.0411957#-0.0069704;0.0411957#-0.0074296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0415204#-0.0050543;0.0419796#-0.0050543;0.0423043#-0.0047296;0.0423043#-0.0042704;0.0419796#-0.0039457;0.0415204#-0.0039457;0.0411957#-0.0042704;0.0411957#-0.0047296']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0434304#0.0087;0.0437448#0.0084362;0.0441552#0.0084362;0.0444696#0.0087;0.0445409#0.0091042;0.0443357#0.0094596;0.04395#0.0096;0.0435643#0.0094596;0.0433591#0.0091042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0434457#0.0015704;0.0435757#0.0013757;0.0437704#0.0012457;0.044#0.0012;0.0442296#0.0012457;0.0444243#0.0013757;0.0445543#0.0015704;0.0446#0.0018;0.0444854#0.0021527;0.0441854#0.0023706;0.0438146#0.0023706;0.0435146#0.0021527;0.0434#0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0434804#0.0042;0.0437948#0.0039362;0.0442052#0.0039362;0.0445196#0.0042;0.0445909#0.0046042;0.0443857#0.0049596;0.044#0.0051;0.0436143#0.0049596;0.0434091#0.0046042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0434804#0.0069;0.0437948#0.0066362;0.0442052#0.0066362;0.0445196#0.0069;0.0445909#0.0073042;0.0443857#0.0076596;0.044#0.0078;0.0436143#0.0076596;0.0434091#0.0073042']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0435757#-0.0094243;0.0438447#-0.0095796;0.0441553#-0.0095796;0.0444243#-0.0094243;0.0445796#-0.0091553;0.0445796#-0.0088447;0.0444243#-0.0085757;0.0441553#-0.0084204;0.0438447#-0.0084204;0.0435757#-0.0085757;0.0434204#-0.0088447;0.0434204#-0.0091553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0435646#-0.0021527;0.0438646#-0.0023706;0.0442354#-0.0023706;0.0445354#-0.0021527;0.04465#-0.0018;0.0446043#-0.0015704;0.0444743#-0.0013757;0.0442796#-0.0012457;0.04405#-0.0012;0.0438204#-0.0012457;0.0436257#-0.0013757;0.0434957#-0.0015704;0.04345#-0.0018']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0436257#-0.0076243;0.0438947#-0.0077796;0.0442053#-0.0077796;0.0444743#-0.0076243;0.0446296#-0.0073553;0.0446296#-0.0070447;0.0444743#-0.0067757;0.0442053#-0.0066204;0.0438947#-0.0066204;0.0436257#-0.0067757;0.0434704#-0.0070447;0.0434704#-0.0073553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.0436257#-0.0049243;0.0438947#-0.0050796;0.0442053#-0.0050796;0.0444743#-0.0049243;0.0446296#-0.0046553;0.0446296#-0.0043447;0.0444743#-0.0040757;0.0442053#-0.0039204;0.0438947#-0.0039204;0.0436257#-0.0040757;0.0434704#-0.0043447;0.0434704#-0.0046553']
		part = self._create_extrude(pointStrings, "(mask_cond_cond2_Zmax) - (mask_cond_cond2_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_cond2_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["cond_cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._setAssemblyMeshSettings(assembly,0,0,0)
		assembly.name="cond_cond2"
		topAssembly.append(assembly)
		return symbPinData
		# End of create_geometry

	def _update_geoProgress(self):
		self.geoProgress+= 1
		if self.geoProgress % 1 == 0:
			progress = (self.geoProgress * 100)/31
			self._updateProgress(progress)

	def getMaskHeights(self,parameterized=False):
		mask_heights={}
		mask_heights_parameterized={}
		mask_heights[3]=(0, 1.25e-05)
		mask_heights_parameterized[3]=("(mask_cond2_Zmin) - (0)", "(mask_cond2_Zmax) - (0)")
		mask_heights[5]=(1.25e-05, 0.0008125)
		mask_heights_parameterized[5]=("(mask_cond_cond2_Zmin) - (0)", "(mask_cond_cond2_Zmax) - (0)")
		mask_heights[2]=(0.0008125, 0.000825)
		mask_heights_parameterized[2]=("(mask_cond_Zmin) - (0)", "(mask_cond_Zmax) - (0)")
		if(parameterized):
			return mask_heights_parameterized
		else:
			return mask_heights

	def getMaskHeightsParameterized(self):
		return self.getMaskHeights(parameterized=True)

	def create_ports( self, topAssembly, includeInvalidPorts=True, symbPinData=None):
		self.setPortWarnings(includeInvalidPorts)
		V=empro.geometry.Vector3d
		L=empro.geometry.Line
		SPAresabs=empro.activeProject.newPartModelingUnit.toReferenceUnits(1e-6)
		if topAssembly != None:
			bbox_geom = topAssembly.boundingBox()
		else:
			bbox_geom = empro.activeProject.geometry.boundingBox()
		xLowerBoundary = float(bbox_geom.lower.x)
		xUpperBoundary = float(bbox_geom.upper.x)
		yLowerBoundary = float(bbox_geom.lower.y)
		yUpperBoundary = float(bbox_geom.upper.y)
		zLowerBoundary = float(bbox_geom.lower.z)
		zUpperBoundary = float(bbox_geom.upper.z)
		internalPortOnXLowerBoundary = False
		internalPortOnXUpperBoundary = False
		internalPortOnYLowerBoundary = False
		internalPortOnYUpperBoundary = False
		internalPortOnZLowerBoundary = False
		internalPortOnZUpperBoundary = False
		ports=[]
		waveguides={}
		portShortcutGroups=[]
		assembly=empro.geometry.Assembly()
		waveform=empro.waveform.Waveform("Broadband Pulse")
		waveform.shape=empro.waveform.MaximumFrequencyWaveformShape()
		self.waveforms["Broadband Pulse"]=waveform
		if getSessionVersion(self.session) >= 7:
			self.session.appendUniqueWaveforms(self.waveforms)
		else:
			for name,waveform in self.waveforms.items():
				empro.activeProject.waveforms.append(waveform)
				self.waveforms[name] = empro.activeProject.waveforms[len(empro.activeProject.waveforms)-1]
		feed=empro.components.Feed()
		feed.name="50 ohm Voltage Source"
		feed.impedance.resistance=50
		feed.waveform=self.waveforms["Broadband Pulse"]
		self.circuitComponentDefinitions[feed.name]=feed
		if getSessionVersion(self.session) >= 7:
			self.session.appendUniqueCircuitComponentDefinitions(self.circuitComponentDefinitions)
		else:
			for name,compDef in self.circuitComponentDefinitions.items():
				empro.activeProject.circuitComponentDefinitions.append(compDef)
				self.circuitComponentDefinitions[name] = empro.activeProject.circuitComponentDefinitions[len(empro.activeProject.circuitComponentDefinitions)-1]
		head=V("(-0.005) - (0)","(0) - (0)","(((mask_cond_Zmax) + (mask_cond_Zmin)) / (2)) - (0)")
		tail=V("(-0.005) - (0)","(0) - (0)","(((mask_cond2_Zmax) + (mask_cond2_Zmin)) / (2)) - (0)")
		extent=empro.components.SheetExtent()
		extent.endPoint1Position=V("(-0.005) - (0)","(-0.001) - (0)","(((mask_cond2_Zmax) + (mask_cond2_Zmin)) / (2)) - (0)")
		extent.endPoint2Position=V("(-0.005) - (0)","(0.001) - (0)","(((mask_cond_Zmax) + (mask_cond_Zmin)) / (2)) - (0)")
		port = self._create_internal_port("P1","50 ohm Voltage Source",head,tail,extent)
		portShortcutGroups.append((1,port))
		ports.append(port)
		self._set_extra_port_info(port, "inputOutput", 1, "P1", "Direct")
		headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
		for headOrTail in headsAndTails:
			if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
			if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
			if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
			if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
			if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
			if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		head=V("(0.045) - (0)","(0) - (0)","(((mask_cond_Zmax) + (mask_cond_Zmin)) / (2)) - (0)")
		tail=V("(0.045) - (0)","(0) - (0)","(((mask_cond2_Zmax) + (mask_cond2_Zmin)) / (2)) - (0)")
		extent=empro.components.SheetExtent()
		extent.endPoint1Position=V("(0.045) - (0)","(-0.001) - (0)","(((mask_cond2_Zmax) + (mask_cond2_Zmin)) / (2)) - (0)")
		extent.endPoint2Position=V("(0.045) - (0)","(0.001) - (0)","(((mask_cond_Zmax) + (mask_cond_Zmin)) / (2)) - (0)")
		port = self._create_internal_port("P2","50 ohm Voltage Source",head,tail,extent)
		portShortcutGroups.append((1,port))
		ports.append(port)
		self._set_extra_port_info(port, "inputOutput", 2, "P2", "Direct")
		headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
		for headOrTail in headsAndTails:
			if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
			if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
			if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
			if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
			if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
			if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		setPortNbToNameMappingInitialized()
		try:
			if getSessionVersion(self.session) >= 5:
				self.session.appendPortList(ports,None,portShortcutGroups)
			else:
				self.session.appendPortList(ports,self.groupList,portShortcutGroups)
		except AttributeError:
			empro.activeProject.circuitComponents().appendList(ports)
			for group,port in portShortcutGroups:
				self.addShortcut(group,port)
		for i in waveguides.keys():
			empro.activeProject.waveGuides.append(waveguides[i])
		assembly.name="waveguide_planes"
		self.session.hide_part(assembly)

	def create_grid_regions(self):
		gG = empro.activeProject.gridGenerator

	def create_parameters(self):
		self._create_parameter("stack_tech_layer_1_Z", "0 mm", "Z of topology level (level 1 of stack tech)",True,fixGridAxis='Z')
		self._create_parameter("stack_tech_layer_3_Z", "0.0125 mm", "Z of topology level (level 3 of stack tech)",True,fixGridAxis='Z')
		self._create_parameter("stack_tech_layer_5_Z", "0.8125 mm", "Z of topology level (level 5 of stack tech)",True,fixGridAxis='Z')
		self._create_parameter("stack_tech_layer_7_Z", "0.825 mm", "Z of topology level (level 7 of stack tech)",True,fixGridAxis='Z')
		self._create_parameter("lateralExtension","3.125 mm","Substrate LATERAL extension", True)
		self._create_parameter("verticalExtension","5 mm","Substrate VERTICAL extension", True)
		self._create_parameter("xLowerExtension", "lateralExtension", "Lower X extension", True)
		self._create_parameter("xUpperExtension", "lateralExtension", "Upper X extension", True)
		self._create_parameter("yLowerExtension", "lateralExtension", "Lower Y extension", True)
		self._create_parameter("yUpperExtension", "lateralExtension", "Upper Y extension", True)
		self._create_parameter("zLowerExtension", "verticalExtension", "Lower Z extension", True)
		self._create_parameter("zUpperExtension", "verticalExtension", "Upper Z extension", True)
		if get_ads_import_version() >= 11 :
			self._create_parameter("toggleExtensionToBoundingBox", 0, "toggle extension of gnd/substrate layers to bounding box of geometry", True)
			self._create_parameter("xLowerBoundingBox", 0.0, "lower X coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("yLowerBoundingBox", 0.0, "lower Y coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("zLowerBoundingBox", 0.0, "lower Z coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("xUpperBoundingBox", 0.0, "upper X coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("yUpperBoundingBox", 0.0, "upper Y coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("zUpperBoundingBox", 0.0, "upper Z coordinate of bounding box of geometry (for extension of covers)", True)
		self._create_parameter("mask_cond2_Zmin",str("0 mm"),"Zmin of mask cond2",True,fixGridAxis='Z')
		self._create_parameter("mask_cond2_Zmax",str("0.0125 mm"),"Zmax of mask cond2",True,fixGridAxis='Z')
		self._create_parameter("mask_cond_cond2_Zmin",str("0.0125 mm"),"Zmin of mask cond_cond2",True,fixGridAxis='Z')
		self._create_parameter("mask_cond_cond2_Zmax",str("0.8125 mm"),"Zmax of mask cond_cond2",True,fixGridAxis='Z')
		self._create_parameter("mask_cond_Zmin",str("0.8125 mm"),"Zmin of mask cond",True,fixGridAxis='Z')
		self._create_parameter("mask_cond_Zmax",str("0.825 mm"),"Zmax of mask cond",True,fixGridAxis='Z')

def maxNbThreadsADS():
	maxNbThreads=0
	return maxNbThreads


g_portNbToName={}
g_portNbToNameInitialized=False

def portNbToName():
	if g_portNbToNameInitialized == True:
		return g_portNbToName
	raise RuntimeError("portNbToName used uninitialized")

def setPortNbToNameMappingInitialized( state = True ):
	global g_portNbToNameInitialized
	g_portNbToNameInitialized = True

def radiationPossible():
	return True

def main():
	try:
		demoMode=empro.toolkit.ads_import.useDemoMode()
	except AttributeError:
		demoMode=False
	try:
		ads_import(demoMode=demoMode)
	except Exception:
		empro.toolkit.ads_import.notify_failure()
		raise

if __name__=="__main__":
	main()
	del ads_import
