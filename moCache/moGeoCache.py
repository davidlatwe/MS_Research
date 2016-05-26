# -*- coding:utf-8 -*-
'''
Created on 2016.04.28

@author: davidpower
'''
import logging
logger = logging.getLogger('MayaOil.moGeocache.Main')

import maya.cmds as cmds
import maya.mel as mel
import moCache.moGeoCacheRules as moRules
import moCache.moGeoCacheMethod as moMethod
reload(moRules)
reload(moMethod)


def exportGeoCache(smooth):
	"""
	輸出 geoCache
	"""
	logger.info('GeoCache export init.')

	# namespace during action
	workingNS = moRules.rWorkingNS()
	viskeyNS = moRules.rViskeyNS()
	# get playback range
	playbackRange = moRules.rPlaybackRange()
	# get frame rate
	timeUnit = moRules.rFrameRate()

	# get list of items to process
	rootNode_List = moMethod.mProcQueue()
	# remove mGC namespace
	moMethod.mCleanWorkingNS(workingNS)
	# remove mGCVisKey namespace
	moMethod.mCleanWorkingNS(viskeyNS)

	logger.info('GeoCache export start.')
	logger.info('export queue: ' + str(len(rootNode_List)))

	for rootNode in rootNode_List:
		logger.info('[' + rootNode + '] geoCaching.')

		# FILTER OUT <intermediate objects> & <constant hidden objects>
		filterResult = moMethod.mFilterOut(rootNode)
		# loop vars
		anim_meshes = filterResult[0]
		anim_viskey = filterResult[1]
		assetNS = moRules.rAssetNS(rootNode)
		assetName = moRules.rAssetName(assetNS)
		geoCacheDir = moRules.rGeoCacheDir(assetName)
		excludeList = moMethod.mGetSmoothExcludeList()

		if anim_viskey:
			# Add and Set namespace
			logger.info('viskeyNS: <' + viskeyNS + '> Set.')
			moMethod.mSetupWorkingNS(viskeyNS)
			# bake visKey
			moMethod.mBakeViskey(anim_viskey, playbackRange)
			# collect all visibility animation node
			visAniNodeList = moMethod.mDuplicateViskey(anim_viskey)
			# export visKey
			cmds.select(visAniNodeList, r= 1)
			keyFile = moRules.rViskeyFilePath(geoCacheDir, assetName)
			moMethod.mExportViskey(keyFile)
			# remove mGCVisKey namespace
			logger.info('viskeyNS: <' + viskeyNS + '> Del.')
			moMethod.mCleanWorkingNS(viskeyNS)
		else:
			logger.info('No visibility key.')

		if anim_meshes:
			# Add and Set namespace
			logger.info('workingNS: <' + workingNS + '> Set.')
			moMethod.mSetupWorkingNS(workingNS)
			# polyUnite
			ves_grp = moMethod.mPolyUniteMesh(anim_meshes)
			# subDiv before export
			if smooth:
				moMethod.mSmoothMesh(ves_grp, excludeList)
			# write out transform node's name
			geoListFile = moRules.rGeoListFilePath(geoCacheDir, assetName)
			moMethod.mSaveGeoList(ves_grp, geoListFile)
			# export GeoCache
			cmds.select(ves_grp, r= 1, hi= 1)
			moMethod.mExportGeoCache(geoCacheDir, assetName)
			# remove mGC namespace
			logger.info('workingNS: <' + workingNS + '> Del.')
			moMethod.mCleanWorkingNS(workingNS)
		else:
			logger.info('No mesh to cache.')

		# note down frameRate and playback range
		timeInfoFile = moRules.rTimeInfoFilePath(geoCacheDir, assetName)
		moMethod.mExportTimeInfo(timeInfoFile, timeUnit, playbackRange)
		logger.info('TimeInfo exported.')

		logger.info('[' + rootNode + '] geoCached.')

	logger.info('GeoCache export completed.')


def importGeoCache(sceneName):
	"""
	輸入 geoCache
	"""
	# namespace during action
	workingNS = moRules.rWorkingNS()
	viskeyNS = moRules.rViskeyNS()

	# get list of items to process
	rootNode_List = moMethod.mProcQueue()

	for rootNode in rootNode_List:
		# loop vars
		assetNS = moRules.rAssetNS(rootNode)
		assetName = moRules.rAssetName(assetNS)
		geoCacheDir = moRules.rGeoCacheDir(assetName, sceneName)
		conflictList = moMethod.mGetGeoCacheConflictList()

		# get transform list from txt file
		geoListFile = moRules.rGeoListFilePath(geoCacheDir, assetName)
		if cmds.file(geoListFile, q= 1, ex= 1):
			anim_geoList = moMethod.mLoadGeoList(geoListFile, rootNode)
			# import GeoCache
			for anim_trans in anim_geoList.keys():
				anim_shape = anim_geoList[anim_trans]
				xmlFile = moRules.rXMLFilePath(geoCacheDir, moRules.rXMLFileName(assetName, workingNS, anim_shape))
				logger.debug(xmlFile)
				if cmds.file(xmlFile, q= 1, ex= 1):
					moMethod.mImportGeoCache(xmlFile, assetNS, anim_trans, conflictList)

		# get viskey from ma file
		keyFile = moRules.rViskeyFilePath(geoCacheDir, assetName)
		if cmds.file(keyFile, q= 1, ex= 1):
			# remove mGCVisKey namespace
			moMethod.mCleanWorkingNS(viskeyNS)
			# import viskey and keep mGCVisKey namespace in viskey
			moMethod.mImportViskey(keyFile, assetNS, viskeyNS)

		# go set frameRate and playback range
		timeInfoFile = moRules.rTimeInfoFilePath(geoCacheDir, assetName)
		if cmds.file(timeInfoFile, q= 1, ex= 1):
			moMethod.mImportTimeInfo(timeInfoFile)



if __name__ == '__main__':
	reload(moRules)
	reload(moMethod)
	#exportGeoCache(1)
	#importGeoCache('SOK_c01_anim_v01')