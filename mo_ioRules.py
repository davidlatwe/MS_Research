# -*- coding:utf-8 -*-
'''
Created on 2016.05.10

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
import os
import mo_SceneInfo



def _getSceneInfo():
	"""
	"""
	return mo_SceneInfo.SceneInfo()


def pathSep():
	"""
	path separator
	"""
	sep = os.altsep
	
	return sep


def rule_scenePath():
	"""
	"""
	
	return None


def rule_moGeoCache(assetName, sceneName= None):
	"""
	"""
	sInfo = _getSceneInfo()

	rootPath = sInfo.wksRoot + sInfo.dirRule['moGeoCache']
	if sceneName is None:
		sceneName = sInfo.scenSip
	geoCache_path = pathSep().join([ rootPath, sceneName, assetName ])

	return geoCache_path
