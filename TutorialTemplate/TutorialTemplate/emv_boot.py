# -*- coding: utf-8 -*-

import empro.toolkit.adv as adv

def main():
	path=r"C:/Users/simucstvsl/ADSCourse/TutorialTemplate/TutorialTemplate"
	lib=r"TutorialTemplate_lib"
	subst=r"TutorialTemplate_lib/fr4custom.subst"
	substlib=r"TutorialTemplate_lib"
	substname=r"fr4custom"
	cell=r"Stripline"
	view=r"layout"
	libS3D=r"simulation/TutorialTemplate_lib/%Stripline/_3%D%Viewer/extra/0/proj_libS3D.xml"
	varDictionary={}
	exprDictionary={}
	adv.loadDesign(path=path, lib=lib, subst=subst, substlib=substlib, substname=substname, cell=cell, view=view, libS3D=libS3D, var_dict=varDictionary, expr_dict=exprDictionary)
