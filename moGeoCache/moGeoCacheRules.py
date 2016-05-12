# -*- coding:utf-8 -*-
'''
Created on 2016.05.10

@author: davidpower
'''
import moSceneInfo



def _getSceneInfo():
	"""
	"""
	return moSceneInfo.SceneInfo()


def rule_moGeoCache(assetName, sceneName= None):
	"""
	"""
	sInfo = _getSceneInfo()

	rootPath = sInfo.workspaceRoot + sInfo.dirRule['moGeoCache']
	if sceneName is None:
		sceneName = sInfo.sceneSplitExt
	geoCache_path = sInfo.sep.join([ rootPath, sceneName, assetName ])

	return geoCache_path
