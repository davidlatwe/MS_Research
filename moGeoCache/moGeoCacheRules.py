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


def rWorkingNamespace():
	"""
	"""
	return ':mGeoCache'


def rAssetNamespace(node):
	"""
	"""
	return node.split(':')[0]


def rViskeyNamespace():
	"""
	"""
	return ':geoViskey'


def rAssetName(nodeNS):
	"""
	"""
	return nodeNS.split('_')[0]


def rGeoCacheDir(assetName, sceneName= None):
	"""
	"""
	sInfo = _getSceneInfo()

	rootPath = sInfo.workspaceRoot + sInfo.dirRule['moGeoCache']
	if sceneName is None:
		sceneName = sInfo.sceneSplitExt
	geoCache_path = sInfo.sep.join([ rootPath, sceneName, assetName ])

	return geoCache_path


def rTransNameFilePath(geoCacheDir, assetName):
	"""
	"""
	sInfo = _getSceneInfo()

	return geoCacheDir + sInfo.sep + assetName + '_trans.txt'


def rXMLFilePath(geoCacheDir, assetName):
	"""
	"""
	sInfo = _getSceneInfo()

	return geoCacheDir + sInfo.sep + assetName + '.xml'


def rViskeyFilePath(geoCacheDir, assetName):
	"""
	"""
	sInfo = _getSceneInfo()

	return geoCacheDir + sInfo.sep + assetName + '_viskey.ma'

