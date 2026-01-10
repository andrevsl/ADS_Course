# -*- coding: utf-8 -*-

import empro.toolkit.adv as adv

def main():
	path=r"C:/Users/simucstvsl/Documents/ADS_Course/Multilayer_Basics_wrk"
	lib=r"Multilayer_Basics_lib"
	subst=r"Multilayer_Basics_lib/tech.subst"
	substlib=r"Multilayer_Basics_lib"
	substname=r"tech"
	cell=r"cell_1"
	view=r"layout"
	libS3D=r"simulation/Multilayer_Basics_lib/cell_1/_3%D%Viewer/extra/0/proj_libS3D.xml"
	varDictionary={}
	exprDictionary={}
	adv.loadDesign(path=path, lib=lib, subst=subst, substlib=substlib, substname=substname, cell=cell, view=view, libS3D=libS3D, var_dict=varDictionary, expr_dict=exprDictionary)
