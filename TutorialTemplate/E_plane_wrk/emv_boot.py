# -*- coding: utf-8 -*-

import empro.toolkit.adv as adv

def main():
	path=r"C:/Users/simucstvsl/ADSCourse/TutorialTemplate/E_plane_wrk"
	lib=r"E_plane_lib"
	subst=r"E_plane_lib/dsn_E_plane.subst"
	substlib=r"E_plane_lib"
	substname=r"dsn_E_plane"
	cell=r"E_plane"
	view=r"layout"
	libS3D=r"simulation/E_plane_lib/%E_plane/_3%D%Viewer/extra/0/proj_libS3D.xml"
	varDictionary={}
	exprDictionary={}
	adv.loadDesign(path=path, lib=lib, subst=subst, substlib=substlib, substname=substname, cell=cell, view=view, libS3D=libS3D, var_dict=varDictionary, expr_dict=exprDictionary)
