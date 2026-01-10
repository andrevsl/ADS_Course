# -*- coding: utf-8 -*-

import empro.toolkit.adv as adv

def main():
	path=r"C:/Users/simucstvsl/Documents/ADS_Course/TLines_wrk"
	lib=r"TLines_lib"
	subst=r"TLines_lib/tech.subst"
	substlib=r"TLines_lib"
	substname=r"tech"
	cell=r"CPWG"
	view=r"layout"
	libS3D=r"simulation/TLines_lib/%C%P%W%G/_3%D%Viewer/extra/0/proj_libS3D.xml"
	varDictionary={}
	exprDictionary={}
	adv.loadDesign(path=path, lib=lib, subst=subst, substlib=substlib, substname=substname, cell=cell, view=view, libS3D=libS3D, var_dict=varDictionary, expr_dict=exprDictionary)
