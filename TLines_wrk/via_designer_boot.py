# -*- coding: utf-8 -*-

# Copyright Keysight Technologies 2017 - 2020

def main():
	import os, sys
	varDictionary={}
	exprDictionary={}
	ADS_HPEESOF_DIR=r"C:\Program Files\Keysight\ADS2022"
	libName=r"TLines_lib"
	substName=r"tech"
	workspacePath=r"C:\Users\simucstvsl\Documents\ADS_Course\TLines_wrk"
	libdefs=r"lib.defs"
	envEMPROHOME=r"C:\Program Files\Keysight\ADS2022\fem\2022.00/Win32_64/bin"
	verbose=False
	sys.path.append(os.path.join(envEMPROHOME))
	import empro.toolkit.via_designer as via_designer

	via_designer.mainGui.main(varDictionary, exprDictionary, ADS_HPEESOF_DIR, libName, substName, workspacePath=workspacePath, libdefs=libdefs, verbose=verbose)

if __name__=="__main__":
	main()
