# -*- coding:utf-8 -*-
'''
Created on 2016.05.10

@author: davidpower
'''
import re
import logging
logger = logging.getLogger('MayaOil.moGeocache.Rules')

import moSceneInfo


def _getSceneInfo():
	"""
	"""
	return moSceneInfo.SceneInfo()


def rWorkingNS():
	"""
	"""
	return ':moGeoCache'


def rViskeyNS():
	"""
	"""
	return ':moGeoCacheViskey'


def rAssetNS(node):
	"""
	"""
	return node.split(':')[0]


def rAssetName(nodeNS):
	"""
	Return basename and id string, if nodeNS ends with digi
	"""
	return nodeNS.split('_')[0] + re.sub('.*?([0-9]*)$', r'\1', nodeNS)


def rPlaybackRange():
	"""
	"""
	sInfo = _getSceneInfo()

	return (sInfo.palybackStart, sInfo.palybackEnd)


def rFrameRate():
	"""
	"""
	sInfo = _getSceneInfo()

	return sInfo.timeUnit


def rGeoCacheDir(assetName, sceneName= None):
	"""
	"""
	sInfo = _getSceneInfo()

	rootPath = sInfo.workspaceRoot + sInfo.dirRule['moGeoCache']
	if sceneName is None:
		sceneName = sInfo.sceneSplitExt
	geoCache_path = sInfo.sep.join([ rootPath, assetName, sceneName ])

	return geoCache_path


def rXMLFileName(assetName, workingNS, anim_shape):
	"""
	"""
	return '_'.join([ assetName, workingNS, anim_shape ])


def rGeoListFilePath(geoCacheDir, assetName):
	"""
	"""
	sInfo = _getSceneInfo()
	filePath = geoCacheDir + sInfo.sep + assetName + '_geoList.txt'
	sInfo.makeDir(filePath)
	
	return filePath


def rXMLFilePath(geoCacheDir, xmlFileName):
	"""
	"""
	sInfo = _getSceneInfo()

	return geoCacheDir + sInfo.sep + xmlFileName + '.xml'


def rViskeyFilePath(geoCacheDir, assetName):
	"""
	"""
	sInfo = _getSceneInfo()
	filePath = geoCacheDir + sInfo.sep + assetName + '_viskey.ma'
	sInfo.makeDir(filePath)

	return filePath


def rTimeInfoFilePath(geoCacheDir, assetName):
	"""
	"""
	sInfo = _getSceneInfo()
	filePath = geoCacheDir + sInfo.sep + assetName + '_timeInfo.txt'
	sInfo.makeDir(filePath)

	return filePath
