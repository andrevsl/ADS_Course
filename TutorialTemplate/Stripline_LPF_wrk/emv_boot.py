# -*- coding: utf-8 -*-

import empro.toolkit.adv as adv

def main():
	path=r"C:/Users/simucstvsl/ADSCourse/TutorialTemplate/Stripline_LPF_wrk"
	lib=r"Stripline_LPF_lib"
	subst=r"Stripline_LPF_lib/dsn_Stripline_box.subst"
	substlib=r"Stripline_LPF_lib"
	substname=r"dsn_Stripline_box"
	cell=r"Stripline_box"
	view=r"layout"
	libS3D=r"simulation/Stripline_LPF_lib/%Stripline_box/_3%D%Viewer/extra/0/proj_libS3D.xml"
	varDictionary={}
	exprDictionary={}
	adv.loadDesign(path=path, lib=lib, subst=subst, substlib=substlib, substname=substname, cell=cell, view=view, libS3D=libS3D, var_dict=varDictionary, expr_dict=exprDictionary)
