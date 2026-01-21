# -*- coding: utf-8 -*-

import empro.toolkit.adv as adv

def main():
	path=r"C:/Users/simucstvsl/Documents/ADS_Course/TRX_Project_wrk"
	lib=r"TRX_Project_lib"
	subst=r"TRX_Project_lib/substrate1.subst"
	substlib=r"TRX_Project_lib"
	substname=r"substrate1"
	cell=r"Wilkinson_Layout"
	view=r"layout"
	libS3D=r"simulation/TRX_Project_lib/%Wilkinson_%Layout/_3%D%Viewer/extra/0/proj_libS3D.xml"
	varDictionary={}
	exprDictionary={}
	adv.loadDesign(path=path, lib=lib, subst=subst, substlib=substlib, substname=substname, cell=cell, view=view, libS3D=libS3D, var_dict=varDictionary, expr_dict=exprDictionary)
