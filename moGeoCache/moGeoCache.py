# -*- coding:utf-8 -*-
'''
Created on 2016.04.28

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
import moGeoCache.moGeoCacheRules as moRules
import moGeoCache.moGeoCacheMethod as moMethod



def exportGeoCache(smooth):
	"""
	輸出 geoCache
	"""
	# namespace during action
	workingNS = moRules.rWorkingNamespace()
	# get playback range
	playbackRange = moRules.rPlaybackRange()
	# get frame rate
	timeUnit = moRules.rFrameRate()

	# get list of items to process
	rootNode_List = moMethod.mProcQueue()
	# remove mGC namespace
	moMethod.mCleanWorkingNS(workingNS)

	for rootNode in rootNode_List:
		# FILTER OUT <intermediate objects> & <constant hidden objects>
		tmpResult = moMethod.mFilterOut(rootNode)
		# loop vars
		anim_meshes = tmpResult[0]
		anim_viskey = tmpResult[1]
		assetNS = moRules.rAssetNamespace(rootNode)
		assetName = moRules.rAssetName(assetNS)
		geoCacheDir = moRules.rGeoCacheDir(assetName)
		
		# Add and Set namespace
		moMethod.mSetupWorkingNS(workingNS)

		if anim_viskey:
			# bake visKey
			moMethod.mBakeViskey(anim_viskey, playbackRange)
			# collect all visibility animation node
			visAniNodeList = moMethod.mDuplicateViskey(anim_viskey)
			# export visKey
			cmds.select(visAniNodeList, r= 1)
			keyFile = moRules.rViskeyFilePath(geoCacheDir, assetName)
			moMethod.mExportViskey(keyFile)

		if anim_meshes:
			# polyUnite
			ves_grp = moMethod.mPolyUniteMesh(anim_meshes)
			# subDiv before export
			if smooth:
				moMethod.mSmoothMesh(ves_grp)
			# write out transform node's name
			transFile = moRules.rTransNameFilePath(geoCacheDir, assetName)
			moMethod.mSaveTransformName(ves_grp, transFile)
			# export GeoCache
			cmds.select(ves_grp, r= 1, hi= 1)
			moMethod.mExportGeoCache(geoCacheDir, assetName)

		# remove mGC namespace
		moMethod.mCleanWorkingNS(workingNS)

		# note down frameRate and playback range
		timeInfoFile = moRules.rTimeInfoFilePath(geoCacheDir, assetName)
		moMethod.mExportTimeInfo(timeInfoFile, timeUnit, playbackRange)


def importGeoCache(sceneName):
	"""
	輸入 geoCache
	"""
	# get list of items to process
	rootNode_List = moMethod.mProcQueue()

	for rootNode in rootNode_List:
		# loop vars
		assetNS = moRules.rAssetNamespace(rootNode)
		assetName = moRules.rAssetName(assetNS)
		geoCacheDir = moRules.rGeoCacheDir(assetName, sceneName)
		xmlFile = moRules.rXMLFilePath(geoCacheDir, assetName)
		transFile = moRules.rTransNameFilePath(geoCacheDir, assetName)

		if cmds.file(xmlFile, q= 1, ex= 1) and cmds.file(transFile, q= 1, ex= 1):
			# get transform list from txt file
			anim_trans = moMethod.mTXTTransList(transFile, rootNode)
			# import GeoCache
			cmds.select(anim_trans, r= 1)
			moMethod.mImportGeoCache(xmlFile)

		# get viskey from ma file
		keyFile = moRules.rViskeyFilePath(geoCacheDir, assetName)
		if cmds.file(keyFile, q= 1, ex= 1):
			viskeyNS = moRules.rViskeyNamespace()
			workingNS = moRules.rWorkingNamespace()
			# import viskey
			moMethod.mImportViskey(keyFile, assetNS, viskeyNS, workingNS)

		# go set frameRate and playback range
		timeInfoFile = moRules.rTimeInfoFilePath(geoCacheDir, assetName)
		if cmds.file(timeInfoFile, q= 1, ex= 1):
			moMethod.mImportTimeInfo(timeInfoFile)



if __name__ == '__main__':
	reload(moRules)
	reload(moMethod)
	#exportGeoCache(1)
	#importGeoCache('SOK_c01_anim_v01')