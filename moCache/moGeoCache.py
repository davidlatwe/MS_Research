# -*- coding:utf-8 -*-
'''
Created on 2016.04.28

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
import moCache.moGeoCacheRules as moRules; reload(moRules)
import moCache.moGeoCacheMethod as moMethod; reload(moMethod)
import logging

logger = logging.getLogger('MayaOil.moGeocache.Main')


def _getRootNode(assetName_override= None):

	rootNode_List = moMethod.mProcQueue()
	if assetName_override and len(rootNode_List) > 1:
		rootNode_List = [rootNode_List[0]]
		logger.warning('AssetName has override, only the first rootNode will be processed.')

	return rootNode_List


def getAssetList():

	assetList = []
	rootNode_List = _getRootNode()
	for rootNode in rootNode_List:
		assetName = moRules.rAssetName(moRules.rAssetNS(rootNode))
		assetList.append(assetName)
	if not assetList:
		logger.error('assetList is empty as your soul.')

	return assetList


def getGeoCacheDir(assetName, sceneName):

	return moRules.rGeoCacheDir(assetName, sceneName)


def exportGeoCache(subdivLevel= None, isPartial= None, assetName_override= None, sceneName_override= None):
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
	rootNode_List = _getRootNode(assetName_override)
	partial_Dict = {}.fromkeys(rootNode_List, [])

	# partial mode
	if isPartial:
		# get partial
		partial_Dict = moMethod.mPartialQueue(partial_Dict)

		'''partial check
		'''
		logger.debug('GeoCache export in PARTIAL Mode.')
		logger.debug('**********************************')
		for rootNode in partial_Dict.keys():
			logger.debug('[' + rootNode + '] :')
			for dag in partial_Dict[rootNode]:
				logger.debug(dag)
		logger.debug('**********************************')

	# remove mGC namespace
	moMethod.mCleanWorkingNS(workingNS)
	# remove mGCVisKey namespace
	moMethod.mCleanWorkingNS(viskeyNS)

	logger.info('GeoCache' + (' PARTIAL' if isPartial else '') + ' export start.')
	logger.info('export queue: ' + str(len(rootNode_List)))

	for rootNode in rootNode_List:
		if isPartial and not partial_Dict[rootNode]:
			logger.info('No partial selection under [' + rootNode + '] .')
			continue

		logger.info('[' + rootNode + ']' + (' PARTIAL' if isPartial else '') + ' geoCaching.')

		''' vars
		'''
		assetNS = moRules.rAssetNS(rootNode)
		assetName = moRules.rAssetName(assetNS) if not assetName_override else assetName_override
		geoCacheDir = getGeoCacheDir(assetName, sceneName_override)
		geoFileType = moRules.rGeoFileType()
		excludeList = moMethod.mGetSmoothExcludeList()

		logger.info('AssetName: [' + assetName + ']')

		# FILTER OUT <intermediate objects> & <constant hidden objects>
		filterResult = moMethod.mFilterOut(rootNode)
		anim_meshes = filterResult[0]
		anim_viskey = filterResult[1]

		if isPartial:
			anim_viskey = [dag for dag in anim_viskey if dag.split('|')[-1].split(':')[-1] in partial_Dict[rootNode]]
			anim_meshes = [dag for dag in anim_meshes if dag.split('|')[-1].split(':')[-1] in partial_Dict[rootNode]]

		''' visibility
		'''
		if anim_viskey:
			# Add and Set namespace
			logger.info('viskeyNS: <' + viskeyNS + '> Set.')
			moMethod.mSetupWorkingNS(viskeyNS)
			# bake visKey
			moMethod.mBakeViskey(anim_viskey, playbackRange)
			# collect all visibility animation node
			visAniNodeList = moMethod.mDuplicateViskey(anim_viskey)
			# export visKey
			for visAniNode in visAniNodeList:
				cmds.select(visAniNode, r= 1)
				keyFile = moRules.rViskeyFilePath(geoCacheDir, assetName, visAniNode)
				moMethod.mExportViskey(keyFile)
			# remove mGCVisKey namespace
			logger.info('viskeyNS: <' + viskeyNS + '> Del.')
			moMethod.mCleanWorkingNS(viskeyNS)
		else:
			logger.warning('No visibility key.')
		
		''' geoCache
		'''	
		if anim_meshes:
			# Add and Set namespace
			logger.info('workingNS: <' + workingNS + '> Set.')
			moMethod.mSetupWorkingNS(workingNS)
			# polyUnite
			ves_grp = moMethod.mPolyUniteMesh(anim_meshes)
			# subdiv before export
			if subdivLevel:
				for ves in cmds.listRelatives(ves_grp, c= 1):
					if ves.split(':')[-1] not in excludeList:
						moMethod.mSmoothMesh(ves, subdivLevel)
			# write out transform node's name
			for ves in cmds.listRelatives(ves_grp, c= 1):
				vesShape = cmds.listRelatives(ves, s= 1)[0]
				geoListFile = moRules.rGeoListFilePath(geoCacheDir, assetName, ves, vesShape, geoFileType)
				moMethod.mSaveGeoList(geoListFile)
			# export GeoCache
			cmds.select(ves_grp, r= 1, hi= 1)
			moMethod.mExportGeoCache(geoCacheDir, assetName)
			# remove mGC namespace
			logger.info('workingNS: <' + workingNS + '> Del.')
			moMethod.mCleanWorkingNS(workingNS)
		else:
			logger.warning('No mesh to cache.')

		# note down frameRate and playback range
		if isPartial:
			logger.warning('In PARTIAL mode, No TimeInfo export.')
		else:
			timeInfoFile = moRules.rTimeInfoFilePath(geoCacheDir, assetName)
			moMethod.mExportTimeInfo(timeInfoFile, timeUnit, playbackRange)
			logger.info('TimeInfo exported.')

		logger.info('[' + rootNode + '] geoCached.')
		logger.info(geoCacheDir)

	logger.info('GeoCache export completed.')

 
def importGeoCache(sceneName, isPartial= None, assetName_override= None, ignorDuplicateName= None, conflictList= None):
	"""
	輸入 geoCache
	"""
	logger.info('GeoCache import init.')

	# namespace during action
	workingNS = moRules.rWorkingNS()
	viskeyNS = moRules.rViskeyNS()

	# get list of items to process
	rootNode_List = _getRootNode(assetName_override)
	partial_Dict = {}.fromkeys(rootNode_List, [])

	# partial mode
	if isPartial:
		# get partial
		partial_Dict = moMethod.mPartialQueue(partial_Dict)

		'''partial check
		'''
		logger.warning('GeoCache import in PARTIAL Mode.')
		logger.debug('**********************************')
		for rootNode in partial_Dict.keys():
			logger.debug('[' + rootNode + '] :')
			for dag in partial_Dict[rootNode]:
				logger.debug(dag)
		logger.debug('**********************************')

	logger.info('GeoCache' + (' PARTIAL' if isPartial else '') + ' import start.')
	logger.info('import queue: ' + str(len(rootNode_List)))

	for rootNode in rootNode_List:
		if isPartial and not partial_Dict[rootNode]:
			logger.debug('No partial selection under [' + rootNode + '] .')
			continue

		logger.info('[' + rootNode + ']' + (' PARTIAL' if isPartial else '') + ' importing.')

		# loop vars
		workRoot = moRules.rWorkspaceRoot()
		assetNS = moRules.rAssetNS(rootNode)
		assetName = moRules.rAssetName(assetNS) if not assetName_override else assetName_override
		geoCacheDir = getGeoCacheDir(assetName, sceneName)
		geoFileType = moRules.rGeoFileType()
		conflictList = [] if conflictList is None else conflictList

		if not cmds.file(geoCacheDir, q= 1, ex= 1):
			logger.warning('[' + rootNode + '] geoCacheDir not exists -> ' + geoCacheDir)
			continue

		# get transform list from motxt file
		anim_geoDict = moMethod.mLoadGeoList(geoCacheDir, workingNS, geoFileType)
		if anim_geoDict:
			anim_transList = anim_geoDict.keys()
			anim_transList.sort()
			if isPartial:
				anim_transList = [ dag for dag in anim_transList if dag in partial_Dict[rootNode] ]
			# import GeoCache
			for anim_trans in anim_transList:
				anim_shape = anim_geoDict[anim_trans]
				xmlFile = moRules.rXMLFilePath(geoCacheDir, moRules.rXMLFileName(assetName, workingNS, anim_shape))
				if cmds.file(xmlFile, q= 1, ex= 1):
					logger.info('[' + rootNode + '] XML Loading...  ' + xmlFile.split(workRoot)[-1])
					moMethod.mImportGeoCache(xmlFile, assetNS, anim_trans, conflictList, ignorDuplicateName)
				else:
					logger.warning('[' + rootNode + '] XML not exists -> ' + xmlFile)
		else:
			logger.warning('[' + rootNode + '] No geoList file to follow.')

		# get viskey from ma file
		visAniNodeList = moMethod.mLoadVisKeyList(geoCacheDir, '.ma')
		if visAniNodeList:
			if isPartial:
				visAniNodeList = [ dag for dag in visAniNodeList if dag in partial_Dict[rootNode] ]
			else:
				logger.info('viskeyNS: <' + viskeyNS + '> Del.')
				# remove mGCVisKey namespace
				moMethod.mCleanWorkingNS(viskeyNS)
			for visAniNode in visAniNodeList:
				keyFile = moRules.rViskeyFilePath(geoCacheDir, assetName, visAniNode)
				if cmds.file(keyFile, q= 1, ex= 1):
					# import viskey and keep mGCVisKey namespace in viskey
					moMethod.mImportViskey(keyFile, assetNS, viskeyNS.split(':')[-1] + ':' + visAniNode)
		else:
			logger.warning('[' + rootNode + '] No visibility key file to import.')

		# go set frameRate and playback range
		if isPartial:
			logger.warning('In PARTIAL mode, No TimeInfo import.')
		else:
			timeInfoFile = moRules.rTimeInfoFilePath(geoCacheDir, assetName)
			if cmds.file(timeInfoFile, q= 1, ex= 1):
				moMethod.mImportTimeInfo(timeInfoFile)
				logger.info('TimeInfo imported.')
			else:
				logger.warning('[' + rootNode + '] TimeInfo not exists.')

		logger.info('[' + rootNode + ']' + (' PARTIAL' if isPartial else '') + ' imported.')

	logger.info('GeoCache' + (' PARTIAL' if isPartial else '') + ' import completed.')
