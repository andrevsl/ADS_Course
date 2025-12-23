# -*- coding: utf-8 -*-

import shutil
import empro.toolkit.analysis as analysis

def main():
	path=r"C:/Users/simucstvsl/ADSCourse/TutorialTemplate/TutorialTemplate"
	lib=r"TutorialTemplate_lib"
	subst=r"TutorialTemplate_lib/substrate1.subst"
	substlib=r"TutorialTemplate_lib"
	substname=r"substrate1"
	ltdSubst=r"simulation/TutorialTemplate_lib/%Layout1/rfpro1/extra/0/proj.ltd"
	cell=r"Layout1"
	layout=r"layout1"
	sipiSetup=r"rfpro1"
	libS3D=r"simulation/TutorialTemplate_lib/%Layout1/rfpro1/extra/0/proj_libS3D.xml"
	varDictionary={}
	exprDictionary={}
	analysis.loadDesign(path=path, lib=lib, subst=subst, substlib=substlib, substname=substname, ltd_subst=ltdSubst, cell=cell, layout_view=layout, sipi_view=sipiSetup, libS3D=libS3D, var_dict=varDictionary, expr_dict=exprDictionary)
	shutil.move(r"C:\Users\simucstvsl\ADSCourse\TutorialTemplate\TutorialTemplate\_rfproBoot000.py", r"C:\Users\simucstvsl\ADSCourse\TutorialTemplate\TutorialTemplate\_rfproBoot000.pyo")
