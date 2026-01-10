'# MWS Version: Version 2025.1 - Oct 28 2024 - ACIS 34.0.1 -

'# length = mm
'# frequency = GHz
'# time = ns
'# frequency range: fmin = 0 fmax = 6
'# created = '[VERSION]2024.1|33.0.1|20231016[/VERSION]


'@ use template: Antenna - Planar_2.cfg

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
'set the units
With Units
    .SetUnit "Length", "mm"
    .SetUnit "Frequency", "GHz"
    .SetUnit "Voltage", "V"
    .SetUnit "Resistance", "Ohm"
    .SetUnit "Inductance", "nH"
    .SetUnit "Temperature",  "degC"
    .SetUnit "Time", "ns"
    .SetUnit "Current", "A"
    .SetUnit "Conductance", "S"
    .SetUnit "Capacitance", "pF"
End With

ThermalSolver.AmbientTemperature "0"

'----------------------------------------------------------------------------

'set the frequency range
Solver.FrequencyRange "0", "10"

'----------------------------------------------------------------------------

Plot.DrawBox True

With Background
     .Type "Normal"
     .Epsilon "1.0"
     .Mu "1.0"
     .XminSpace "0.0"
     .XmaxSpace "0.0"
     .YminSpace "0.0"
     .YmaxSpace "0.0"
     .ZminSpace "0.0"
     .ZmaxSpace "0.0"
End With

With Boundary
     .Xmin "expanded open"
     .Xmax "expanded open"
     .Ymin "expanded open"
     .Ymax "expanded open"
     .Zmin "expanded open"
     .Zmax "expanded open"
     .Xsymmetry "none"
     .Ysymmetry "none"
     .Zsymmetry "none"
End With

' optimize mesh settings for planar structures

With Mesh
     .MergeThinPECLayerFixpoints "True"
     .RatioLimit "20"
     .AutomeshRefineAtPecLines "True", "6"
     .FPBAAvoidNonRegUnite "True"
     .ConsiderSpaceForLowerMeshLimit "False"
     .MinimumStepNumber "5"
     .AnisotropicCurvatureRefinement "True"
     .AnisotropicCurvatureRefinementFSM "True"
End With

With MeshSettings
     .SetMeshType "Hex"
     .Set "RatioLimitGeometry", "20"
     .Set "EdgeRefinementOn", "1"
     .Set "EdgeRefinementRatio", "6"
End With

With MeshSettings
     .SetMeshType "HexTLM"
     .Set "RatioLimitGeometry", "20"
End With

With MeshSettings
     .SetMeshType "Tet"
     .Set "VolMeshGradation", "1.5"
     .Set "SrfMeshGradation", "1.5"
End With

' change mesh adaption scheme to energy
' 		(planar structures tend to store high energy
'     	 locally at edges rather than globally in volume)

MeshAdaption3D.SetAdaptionStrategy "Energy"

' switch on FD-TET setting for accurate farfields

FDSolver.ExtrudeOpenBC "True"

PostProcess1D.ActivateOperation "vswr", "true"
PostProcess1D.ActivateOperation "yz-matrices", "true"

With FarfieldPlot
	.ClearCuts ' lateral=phi, polar=theta
	.AddCut "lateral", "0", "1"
	.AddCut "lateral", "90", "1"
	.AddCut "polar", "90", "1"
End With

'----------------------------------------------------------------------------

With MeshSettings
     .SetMeshType "Hex"
     .Set "Version", 1%
End With

With Mesh
     .MeshType "PBA"
End With

'set the solver type
ChangeSolverType("HF Time Domain")

'----------------------------------------------------------------------------

'@ new component: component1

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Component.New "component1"

'@ define brick: component1:solid1

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
With Brick
     .Reset 
     .Name "solid1" 
     .Component "component1" 
     .Material "PEC" 
     .Xrange "-W/2", "W/2" 
     .Yrange "0", "h" 
     .Zrange "0", "l" 
     .Create
End With

'@ define material: material1

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
With Material 
     .Reset 
     .Name "material1"
     .Folder ""
     .Rho "0"
     .ThermalType "Normal"
     .ThermalConductivity "0"
     .SpecificHeat "0", "J/K/kg"
     .DynamicViscosity "0"
     .UseEmissivity "True"
     .Emissivity "0"
     .MetabolicRate "0.0"
     .VoxelConvection "0.0"
     .BloodFlow "0"
     .Absorptance "0"
     .MechanicsType "Unused"
     .IntrinsicCarrierDensity "0"
     .FrqType "all"
     .Type "Normal"
     .MaterialUnit "Frequency", "GHz"
     .MaterialUnit "Geometry", "mm"
     .MaterialUnit "Time", "ns"
     .MaterialUnit "Temperature", "degC"
     .Epsilon "2.2"
     .Mu "1"
     .Sigma "0"
     .TanD "0.0"
     .TanDFreq "0.0"
     .TanDGiven "False"
     .TanDModel "ConstTanD"
     .SetConstTanDStrategyEps "AutomaticOrder"
     .ConstTanDModelOrderEps "3"
     .DjordjevicSarkarUpperFreqEps "0"
     .SetElParametricConductivity "False"
     .ReferenceCoordSystem "Global"
     .CoordSystemType "Cartesian"
     .SigmaM "0"
     .TanDM "0.0"
     .TanDMFreq "0.0"
     .TanDMGiven "False"
     .TanDMModel "ConstTanD"
     .SetConstTanDStrategyMu "AutomaticOrder"
     .ConstTanDModelOrderMu "3"
     .DjordjevicSarkarUpperFreqMu "0"
     .SetMagParametricConductivity "False"
     .DispModelEps  "None"
     .DispModelMu "None"
     .DispersiveFittingSchemeEps "Nth Order"
     .MaximalOrderNthModelFitEps "10"
     .ErrorLimitNthModelFitEps "0.1"
     .UseOnlyDataInSimFreqRangeNthModelEps "False"
     .DispersiveFittingSchemeMu "Nth Order"
     .MaximalOrderNthModelFitMu "10"
     .ErrorLimitNthModelFitMu "0.1"
     .UseOnlyDataInSimFreqRangeNthModelMu "False"
     .UseGeneralDispersionEps "False"
     .UseGeneralDispersionMu "False"
     .NLAnisotropy "False"
     .NLAStackingFactor "1"
     .NLADirectionX "1"
     .NLADirectionY "0"
     .NLADirectionZ "0"
     .Colour "0", "1", "1" 
     .Wireframe "False" 
     .Reflection "False" 
     .Allowoutline "True" 
     .Transparentoutline "False" 
     .Transparency "0" 
     .Create
End With

'@ change material: component1:solid1 to: material1

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Solid.ChangeMaterial "component1:solid1", "material1"

'@ define brick: component1:solid2

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
With Brick
     .Reset 
     .Name "solid2" 
     .Component "component1" 
     .Material "material1" 
     .Xrange "-ws/2", "ws/2" 
     .Yrange "h", "h+t" 
     .Zrange "0", "L" 
     .Create
End With

'@ define brick: component1:solid3

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
With Brick
     .Reset 
     .Name "solid3" 
     .Component "component1" 
     .Material "material1" 
     .Xrange "-w/2", "w/2" 
     .Yrange "-t", "0" 
     .Zrange "L", "L" 
     .Create
End With

'@ transform: translate component1:solid2

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
With Transform 
     .Reset 
     .Name "component1:solid2" 
     .Vector "0", "-h", "0" 
     .UsePickedPoints "False" 
     .InvertPickedPoints "False" 
     .MultipleObjects "True" 
     .GroupObjects "False" 
     .Repetitions "1" 
     .MultipleSelection "False" 
     .Destination "" 
     .Material "" 
     .AutoDestination "True" 
     .Transform "Shape", "Translate" 
End With

'@ change material: component1:solid2 to: PEC

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Solid.ChangeMaterial "component1:solid2", "PEC"

'@ change material: component1:solid2_1 to: PEC

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Solid.ChangeMaterial "component1:solid2_1", "PEC"

'@ change material: component1:solid3 to: PEC

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Solid.ChangeMaterial "component1:solid3", "PEC"

'@ clear picks

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.ClearAllPicks

'@ align wcs with edge and face

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickFaceFromId "component1:solid1", "2" 
Pick.PickEdgeFromId "component1:solid2_1", "4", "4" 
WCS.AlignWCSWithSelected "EdgeAndFace"

'@ align wcs with edge and face

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickFaceFromId "component1:solid2_1", "3" 
Pick.PickEdgeFromId "component1:solid2_1", "4", "4" 
WCS.AlignWCSWithSelected "EdgeAndFace"

'@ align wcs with edge and face

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickFaceFromId "component1:solid2_1", "3" 
Pick.PickEdgeFromId "component1:solid2_1", "4", "4" 
WCS.AlignWCSWithSelected "EdgeAndFace"

'@ align wcs with edge and face

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickFaceFromId "component1:solid2_1", "3" 
Pick.PickEdgeFromId "component1:solid2_1", "4", "4" 
WCS.AlignWCSWithSelected "EdgeAndFace"

'@ pick edge

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickEdgeFromId "component1:solid2_1", "4", "4"

'@ pick edge

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickEdgeFromId "component1:solid2", "4", "4"

'@ define discrete face port: 1

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
With DiscreteFacePort 
     .Reset 
     .PortNumber "1" 
     .Type "SParameter"
     .Label ""
     .Folder ""
     .Impedance "50.0"
     .VoltageAmplitude "1.0"
     .CurrentAmplitude "1.0"
     .Monitor "True"
     .CenterEdge "True"
     .SetP1 "True", "0", "0", "0"
     .SetP2 "True", "0", "0", "0.8"
     .LocalCoordinates "True"
     .InvertDirection "False"
     .UseProjection "False"
     .ReverseProjection "False"
     .FaceType "Linear"
     .Create 
End With

'@ align wcs with edge

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickEdgeFromId "component1:solid2_1", "2", "2" 
WCS.AlignWCSWithSelected "EdgeCenter"

'@ align wcs with edge and face

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickFaceFromId "component1:solid2_1", "3" 
Pick.PickEdgeFromId "component1:solid2_1", "2", "2" 
WCS.AlignWCSWithSelected "EdgeAndFace"

'@ align wcs with edge

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickEdgeFromId "component1:solid2_1", "2", "2" 
WCS.AlignWCSWithSelected "EdgeCenter"

'@ align wcs with edge

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickEdgeFromId "component1:solid2_1", "2", "2" 
WCS.AlignWCSWithSelected "EdgeCenter"

'@ align wcs with edge and face

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickFaceFromId "component1:solid2_1", "3" 
Pick.PickEdgeFromId "component1:solid2_1", "2", "2" 
WCS.AlignWCSWithSelected "EdgeAndFace"

'@ pick edge

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickEdgeFromId "component1:solid2_1", "2", "2"

'@ pick edge

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickEdgeFromId "component1:solid2", "2", "2"

'@ define discrete face port: 2

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
With DiscreteFacePort 
     .Reset 
     .PortNumber "2" 
     .Type "SParameter"
     .Label ""
     .Folder ""
     .Impedance "50.0"
     .VoltageAmplitude "1.0"
     .CurrentAmplitude "1.0"
     .Monitor "True"
     .CenterEdge "True"
     .SetP1 "True", "0", "0", "0"
     .SetP2 "True", "0", "0", "0.8"
     .LocalCoordinates "True"
     .InvertDirection "False"
     .UseProjection "False"
     .ReverseProjection "False"
     .FaceType "Linear"
     .Create 
End With

'@ clear picks

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.ClearAllPicks

'@ define time domain solver parameters

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Mesh.SetCreator "High Frequency" 

With Solver 
     .Method "Hexahedral"
     .CalculationType "TD-S"
     .StimulationPort "All"
     .StimulationMode "All"
     .SteadyStateLimit "-40"
     .MeshAdaption "False"
     .AutoNormImpedance "False"
     .NormingImpedance "50"
     .CalculateModesOnly "False"
     .SParaSymmetry "False"
     .StoreTDResultsInCache  "False"
     .RunDiscretizerOnly "False"
     .FullDeembedding "False"
     .SuperimposePLWExcitation "False"
     .UseSensitivityAnalysis "False"
End With

'@ set PBA version

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Discretizer.PBAVersion "2023101624"

'@ define material: material1

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
With Material 
     .Reset 
     .Name "material1"
     .Folder ""
     .Rho "0"
     .ThermalType "Normal"
     .ThermalConductivity "0"
     .SpecificHeat "0", "J/K/kg"
     .DynamicViscosity "0"
     .UseEmissivity "True"
     .Emissivity "0"
     .MetabolicRate "0.0"
     .VoxelConvection "0.0"
     .BloodFlow "0"
     .Absorptance "0"
     .MechanicsType "Unused"
     .IntrinsicCarrierDensity "0"
     .FrqType "all"
     .Type "Normal"
     .MaterialUnit "Frequency", "GHz"
     .MaterialUnit "Geometry", "mm"
     .MaterialUnit "Time", "ns"
     .MaterialUnit "Temperature", "degC"
     .Epsilon "er"
     .Mu "1"
     .Sigma "0.004"
     .TanD "tangdelta"
     .TanDFreq "0.0"
     .TanDGiven "True"
     .TanDModel "ConstTanD"
     .SetConstTanDStrategyEps "AutomaticOrder"
     .ConstTanDModelOrderEps "3"
     .DjordjevicSarkarUpperFreqEps "0"
     .SetElParametricConductivity "False"
     .ReferenceCoordSystem "Global"
     .CoordSystemType "Cartesian"
     .SigmaM "0"
     .TanDM "0.0"
     .TanDMFreq "0.0"
     .TanDMGiven "False"
     .TanDMModel "ConstTanD"
     .SetConstTanDStrategyMu "AutomaticOrder"
     .ConstTanDModelOrderMu "3"
     .DjordjevicSarkarUpperFreqMu "0"
     .SetMagParametricConductivity "False"
     .DispModelEps "None"
     .DispModelMu "None"
     .DispersiveFittingSchemeEps "Nth Order"
     .MaximalOrderNthModelFitEps "10"
     .ErrorLimitNthModelFitEps "0.1"
     .UseOnlyDataInSimFreqRangeNthModelEps "False"
     .DispersiveFittingSchemeMu "Nth Order"
     .MaximalOrderNthModelFitMu "10"
     .ErrorLimitNthModelFitMu "0.1"
     .UseOnlyDataInSimFreqRangeNthModelMu "False"
     .UseGeneralDispersionEps "False"
     .UseGeneralDispersionMu "False"
     .NLAnisotropy "False"
     .NLAStackingFactor "1"
     .NLADirectionX "1"
     .NLADirectionY "0"
     .NLADirectionZ "0"
     .Colour "0", "1", "0.501961" 
     .Wireframe "False" 
     .Reflection "False" 
     .Allowoutline "True" 
     .Transparentoutline "False" 
     .Transparency "0" 
     .Create
End With

'@ define material: Copper (annealed)

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
With Material
     .Reset
     .Name "Copper (annealed)"
     .Folder ""
     .FrqType "static"
     .Type "Normal"
     .SetMaterialUnit "Hz", "mm"
     .Epsilon "1"
     .Mu "1.0"
     .Kappa "5.8e+007"
     .TanD "0.0"
     .TanDFreq "0.0"
     .TanDGiven "False"
     .TanDModel "ConstTanD"
     .KappaM "0"
     .TanDM "0.0"
     .TanDMFreq "0.0"
     .TanDMGiven "False"
     .TanDMModel "ConstTanD"
     .DispModelEps "None"
     .DispModelMu "None"
     .DispersiveFittingSchemeEps "Nth Order"
     .DispersiveFittingSchemeMu "Nth Order"
     .UseGeneralDispersionEps "False"
     .UseGeneralDispersionMu "False"
     .FrqType "all"
     .Type "Lossy metal"
     .SetMaterialUnit "GHz", "mm"
     .Mu "1.0"
     .Kappa "5.8e+007"
     .Rho "8930.0"
     .ThermalType "Normal"
     .ThermalConductivity "401.0"
     .SpecificHeat "390", "J/K/kg"
     .MetabolicRate "0"
     .BloodFlow "0"
     .VoxelConvection "0"
     .MechanicsType "Isotropic"
     .YoungsModulus "120"
     .PoissonsRatio "0.33"
     .ThermalExpansionRate "17"
     .Colour "1", "1", "0"
     .Wireframe "False"
     .Reflection "False"
     .Allowoutline "True"
     .Transparentoutline "False"
     .Transparency "0"
     .Create
End With

'@ change material: component1:solid2 to: Copper (annealed)

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Solid.ChangeMaterial "component1:solid2", "Copper (annealed)"

'@ change material: component1:solid2_1 to: Copper (annealed)

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Solid.ChangeMaterial "component1:solid2_1", "Copper (annealed)"

'@ define frequency range

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Solver.FrequencyRange "0", "6"

'@ change material: component1:solid3 to: Copper (annealed)

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Solid.ChangeMaterial "component1:solid3", "Copper (annealed)"

'@ transform: translate component1:solid2_1

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
With Transform 
     .Reset 
     .Name "component1:solid2_1" 
     .Vector "0", "0", "-t" 
     .UsePickedPoints "False" 
     .InvertPickedPoints "False" 
     .MultipleObjects "False" 
     .GroupObjects "False" 
     .Repetitions "1" 
     .MultipleSelection "False" 
     .AutoDestination "True" 
     .Transform "Shape", "Translate" 
End With

'@ delete port: port1

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Port.Delete "1"

'@ pick edge

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickEdgeFromId "component1:solid2_1", "8", "8"

'@ pick edge

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickEdgeFromId "component1:solid2", "6", "6"

'@ define discrete face port: 1

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
With DiscreteFacePort 
     .Reset 
     .PortNumber "1" 
     .Type "SParameter"
     .Label ""
     .Folder ""
     .Impedance "50.0"
     .VoltageAmplitude "1.0"
     .CurrentAmplitude "1.0"
     .Monitor "True"
     .CenterEdge "True"
     .SetP1 "True", "0", "20", "-0.018"
     .SetP2 "True", "0", "20", "0.782"
     .LocalCoordinates "True"
     .InvertDirection "False"
     .UseProjection "False"
     .ReverseProjection "False"
     .FaceType "Linear"
     .Create 
End With

'@ delete port: port2

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Port.Delete "2"

'@ pick edge

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickEdgeFromId "component1:solid2_1", "2", "2"

'@ pick edge

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.PickEdgeFromId "component1:solid2", "4", "4"

'@ define discrete face port: 2

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
With DiscreteFacePort 
     .Reset 
     .PortNumber "2" 
     .Type "SParameter"
     .Label ""
     .Folder ""
     .Impedance "50.0"
     .VoltageAmplitude "1.0"
     .CurrentAmplitude "1.0"
     .Monitor "True"
     .CenterEdge "True"
     .SetP1 "True", "0", "0", "-0.018"
     .SetP2 "True", "0", "0", "0.782"
     .LocalCoordinates "True"
     .InvertDirection "False"
     .UseProjection "False"
     .ReverseProjection "False"
     .FaceType "Linear"
     .Create 
End With

'@ clear picks

'[VERSION]2024.1|33.0.1|20231016[/VERSION]
Pick.ClearAllPicks

'@ define brick: component1:solid4

'[VERSION]2025.1|34.0.1|20241028[/VERSION]
With Brick
     .Reset 
     .Name "solid4" 
     .Component "component1" 
     .Material "Copper (annealed)" 
     .Xrange "-w/2", "w/2" 
     .Yrange "0", "L" 
     .Zrange "-t", "0" 
     .Create
End With

