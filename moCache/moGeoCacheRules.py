# -*- coding:utf-8 -*-
'''
Created on 2016.05.10

@author: davidpower
'''
import re
import logging
logger = logging.getLogger('MayaOil.moGeocache.Rules')

import moSceneInfo; reload(moSceneInfo)


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


def rGeoFileType():
	"""
	"""
	return '.motxt'


def rAssetNS(node):
	"""
	"""
	return node.split(':')[0]


def rAssetName(nodeNS):
	"""
	Return basename and id string, if nodeNS ends with digi
	"""
	#return nodeNS.split('_')[0] + re.sub('.*?([0-9]*)$', r'\1', nodeNS)
	return nodeNS.split('_')[0]


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


def rWorkspaceRoot():
	"""
	"""
	sInfo = _getSceneInfo()

	return sInfo.workspaceRoot


def rGeoCacheDir(assetName, sceneName= None):
	"""
	"""
	sInfo = _getSceneInfo()
	geoDir = ''
	try:
		geoDir = sInfo.dirRule['moGeoCache']
	except:
		logger.error('[moGeoCache] file rule missing.')

	rootPath = sInfo.workspaceRoot + geoDir
	isMakeDir = False
	if sceneName is None:
		sceneName = sInfo.sceneSplitExt
		isMakeDir = True

	geoCache_path = sInfo.sep.join([ rootPath, assetName, sceneName ])

	if isMakeDir:
		sInfo.makeDir(geoCache_path)

	return geoCache_path


def rXMLFileName(assetName, workingNS, anim_shape):
	"""
	"""
	return '_'.join([ assetName, workingNS.split(':')[1], anim_shape ])


def rGeoListFilePath(geoCacheDir, assetName, ves, vesShape, geoFileType):
	"""
	"""
	sInfo = _getSceneInfo()
	filePath = geoCacheDir + sInfo.sep + assetName + '_' + vesShape.replace(':', '_') + '@' + ves.split(':')[-1] + geoFileType
	
	return filePath


def rXMLFilePath(geoCacheDir, xmlFileName):
	"""
	"""
	sInfo = _getSceneInfo()

	return geoCacheDir + sInfo.sep + xmlFileName + '.xml'


def rViskeyFilePath(geoCacheDir, assetName, visAniNode):
	"""
	"""
	sInfo = _getSceneInfo()
	filePath = geoCacheDir + sInfo.sep + assetName + '@' + visAniNode.split(':')[-1] + '.ma'

	return filePath


def rTimeInfoFilePath(geoCacheDir, assetName):
	"""
	"""
	sInfo = _getSceneInfo()
	filePath = geoCacheDir + sInfo.sep + assetName + '_timeInfo.txt'

	return filePath
