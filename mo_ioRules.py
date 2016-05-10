# -*- coding:utf-8 -*-
'''
Created on 2016.05.10

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
import os
#import sys
#sys.path.insert(0, 'C:/Users/David/Documents/GitHub/MS_MayaOil')
#import mMaya.mGeneral as mgnr


def pathSep():
	"""
	path separator
	"""
	sep = os.altsep
	
	return sep


def getDirRules():
	"""
	"""
	ruleDict = {}
	for rule in cmds.workspace(q= 1, frl= 1):
		ruleDict[rule] = cmds.workspace(rule, q= 1, fre= 1)

	return ruleDict


def rule_scenePath():
	"""
	"""
	
	return None


def rule_moGeoCache(rootNode):
	"""
	"""
	geoCache_root = getDirRules()['moGeoCache']
	geoCache_name = rootNode.replace(':', '-')
	geoCache_path = pathSep().join([ geoCache_root, _snx, geoCache_name ])
	geoCache_file = geoCache_name + '@'

	return geoCache_path, geoCache_file
