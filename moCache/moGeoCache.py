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
	"""
	找出選取內容的根物件，如果 assetName_override 為 True ，
	則只回傳根物件 List 裡的最後一個根物件
	"""
	rootNode_List = moMethod.mProcQueue()
	if assetName_override and len(rootNode_List) > 1:
		rootNode_List = [rootNode_List[-1]]
		logger.warning('AssetName has override, only the last rootNode will be pass.')

	return rootNode_List


def getAssetList():
	"""
	從根物件的 transformNode 名稱取出 assetName
	** 目前尚無法處理含有重複 asset 的狀況
	"""
	assetList = []
	rootNode_List = _getRootNode()
	for rootNode in rootNode_List:
		assetName = moRules.rAssetName(moRules.rAssetNS(rootNode))
		assetList.append(assetName)
	if not assetList:
		logger.info('assetList is empty as your soul.')

	return assetList


def getGeoCacheDir(assetName, mode, sceneName):
	"""
	取得該 asset 的 GeoCache 存放路徑，並依 mode 來判斷是否需要在路徑不存在時建立資料夾
	"""
	return moRules.rGeoCacheDir(assetName, mode, sceneName)


def exportGeoCache(subdivLevel= None, isPartial= None, isStatic= None, assetName_override= None, sceneName_override= None):
	"""
	輸出 geoCache
	@param  subdivLevel - 模型在 cache 之前需要被 subdivide smooth 的次數
	@param    isPartial - 局部輸出模式 (只輸出所選，不輸出 asset 根物件底下的所有子物件)
	@param     isStatic - 靜態物件輸出
	@param  assetName_override - 輸出過程用此取代該 物件 原本的 assetName
	@param  sceneName_override - 輸出過程用此取代該 場景 原本的 sceneName
	"""
	logger.info('GeoCache export init.')

	# namespace during action
	workingNS = moRules.rWorkingNS()
	viskeyNS = moRules.rViskeyNS()
	rigkeyNS = moRules.rRigkeyNS()
	nodeOutNS = moRules.rNodeOutNS()
	# get playback range
	playbackRange_keep = moRules.rPlaybackRange()
	isStatic = True if isStatic else False
	# 若為靜態輸出模式，變更 playbackRange 為兩個 frame 的長度
	if isStatic:
		timelineInfo = moMethod.mSetStaticRange()
	else:
		moMethod.mRangePushBack()
	playbackRange = moRules.rPlaybackRange()
	# get frame rate
	timeUnit = moRules.rFrameRate()

	# get list of items to process
	rootNode_List = _getRootNode(assetName_override)
	partial_Dict = {}.fromkeys(rootNode_List, [])

	# partial mode
	if isPartial:
		# 取得局部選取範圍的物件清單並建立成字典
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

	# 正式開始前，先檢查並清除待會作業要使用的 Namespace
	# remove mGC namespace
	moMethod.mCleanWorkingNS(workingNS)
	# remove mGCVisKey namespace
	moMethod.mCleanWorkingNS(viskeyNS)
	# remove mGCRigKey namespace
	moMethod.mCleanWorkingNS(rigkeyNS)

	logger.info('GeoCache' + (' PARTIAL' if isPartial else '') + ' export start.')
	logger.info('export queue: ' + str(len(rootNode_List)))

	# 作業開始，依序處理各個 asset
	for rootNode in rootNode_List:
		if isPartial and not partial_Dict[rootNode]:
			logger.info('No partial selection under [' + rootNode + '] .')
			continue

		logger.info('[' + rootNode + ']' + (' PARTIAL' if isPartial else '') + ' geoCaching.')

		''' vars
		'''
		assetNS = moRules.rAssetNS(rootNode)
		assetName = moRules.rAssetName(assetNS) if not assetName_override else assetName_override
		geoCacheDir = getGeoCacheDir(assetName, 1, sceneName_override)
		geoFileType = moRules.rGeoFileType()
		smoothExclusive, smoothMask = moMethod.mGetSmoothMask(assetName)
		rigCtrlList = moMethod.mGetRigCtrlExportList(assetName)
		outNodeDict = moMethod.mGetNodeOutputList(assetName)

		logger.info('AssetName: [' + assetName + ']')

		# 物件過濾
		# FILTER OUT <intermediate objects> & <constant hidden objects>
		filterResult = moMethod.mFilterOut(rootNode)
		anim_meshes = filterResult[0]
		anim_viskey = filterResult[1]

		if isPartial:
			# 檢查過濾出來的物件是否在局部選取範圍中，並更新過濾清單
			anim_viskey = [dag for dag in anim_viskey if dag.split('|')[-1].split(':')[-1] in partial_Dict[rootNode]]
			anim_meshes = [dag for dag in anim_meshes if dag.split('|')[-1].split(':')[-1] in partial_Dict[rootNode]]
		
		''' visibility
		'''
		if anim_viskey:
			# open undo chunk, for later undo from visKey bake 
			cmds.undoInfo(ock= 1)
			# Add and Set namespace
			logger.info('viskeyNS: <' + viskeyNS + '> Set.')
			moMethod.mSetupWorkingNS(viskeyNS)
			# bake visKey
			moMethod.mBakeViskey(anim_viskey, playbackRange)
			# duplicate and collect all baked visibility animation node
			visAniNodeList = moMethod.mDuplicateViskey(anim_viskey)
			# export visKey
			for visAniNode in visAniNodeList:
				cmds.select(visAniNode, r= 1)
				keyFile = moRules.rViskeyFilePath(geoCacheDir, assetName, anim_viskey[visAniNodeList.index(visAniNode)])
				moMethod.mExportViskey(keyFile)
			# remove mGCVisKey namespace
			logger.info('viskeyNS: <' + viskeyNS + '> Del.')
			moMethod.mCleanWorkingNS(viskeyNS)
			# close undo chunk, and undo
			cmds.undoInfo(cck= 1)
			cmds.undo()
		else:
			logger.warning('No visibility key.')

		''' nodeOutput
		'''
		if outNodeDict and not isPartial:
			# open undo chunk, for later undo from visKey bake 
			cmds.undoInfo(ock= 1)
			# Add and Set namespace
			logger.info('nodeOutNS: <' + nodeOutNS + '> Set.')
			moMethod.mSetupWorkingNS(nodeOutNS)
			# bake outKey
			moMethod.mBakeOutkey(outNodeDict, playbackRange, assetNS)
			# collect all visibility animation node
			outAniNodeDict = moMethod.mDuplicateOutkey(outNodeDict, assetNS)
			# export outKey
			for outAniNode in outAniNodeDict:
				cmds.select(outAniNode, r= 1)
				keyFile = moRules.rOutkeyFilePath(geoCacheDir, assetName, outAniNode)
				moMethod.mExportOutkey(keyFile, outAniNode, outAniNodeDict[outAniNode])
			# remove mGCVisKey namespace
			logger.info('nodeOutNS: <' + nodeOutNS + '> Del.')
			moMethod.mCleanWorkingNS(nodeOutNS)
			# close undo chunk, and undo
			cmds.undoInfo(cck= 1)
			cmds.undo()
		else:
			logger.warning('No nodeOutput key.')

		''' rigging ctrls
		'''
		if rigCtrlList and not isPartial:
			# open undo chunk, for later undo from rigging ctrls bake 
			cmds.undoInfo(ock= 1)
			# Add and Set namespace
			logger.info('rigkeyNS: <' + rigkeyNS + '> Set.')
			moMethod.mSetupWorkingNS(rigkeyNS)
			# duplicate ctrls
			cmds.select(rigCtrlList, r= 1)
			rigCtrlList = moMethod.mDuplicateSelectedOnly(1)
			# bake rigging ctrls
			moMethod.mBakeRigkey(rigCtrlList, playbackRange)
			# export baked rigging ctrls
			cmds.select(rigCtrlList, r= 1)
			rigFile = moRules.rRigkeyFilePath(geoCacheDir, assetName)
			moMethod.mExportRigkey(rigFile)
			# remove mGCVisKey namespace
			logger.info('rigkeyNS: <' + rigkeyNS + '> Del.')
			moMethod.mCleanWorkingNS(rigkeyNS)
			# close undo chunk, and undo
			cmds.undoInfo(cck= 1)
			cmds.undo()
		else:
			logger.warning('No rigging controls to export.')
		
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
					if ((ves.split(':')[-1] in smoothMask) + smoothExclusive) % 2:
						moMethod.mSmoothMesh(ves, subdivLevel)
			# write out transform node's name
			for ves in cmds.listRelatives(ves_grp, c= 1):
				vesShape = cmds.listRelatives(ves, s= 1)[0]
				geoListFile = moRules.rGeoListFilePath(geoCacheDir, assetName, ves, vesShape, geoFileType)
				moMethod.mSaveGeoList(geoListFile)
			# export GeoCache
			logger.info('Asset [' + assetName + '] ready to start caching.')
			cmds.select(ves_grp, r= 1, hi= 1)
			moMethod.mExportGeoCache(geoCacheDir, assetName)
			logger.info('Asset [' + assetName + '] caching process is done.')
			# remove mGC namespace
			logger.info('workingNS: <' + workingNS + '> Del.')
			moMethod.mCleanWorkingNS(workingNS)
		else:
			logger.warning('No mesh to cache.')

		# note down frameRate and playback range
		timeInfoFile = moRules.rTimeInfoFilePath(geoCacheDir, assetName)
		moMethod.mExportTimeInfo(timeInfoFile, timeUnit, playbackRange_keep, isStatic)
		logger.info('TimeInfo exported.')

		logger.info('[' + rootNode + '] geoCached.')
		logger.info(geoCacheDir)

	if isStatic:
		moMethod.mSetStaticRange(timelineInfo)
	else:
		moMethod.mRangePushBack(1)

	logger.info('GeoCache export completed.')

 
def importGeoCache(sceneName, isPartial= None, assetName_override= None, ignorDuplicateName= None, conflictList= None, didWrap= None):
	"""
	輸入 geoCache
	@param    sceneName - geoCache 來源的場景名稱
	@param    isPartial - 局部輸入模式 (只輸入所選，不輸入 asset 根物件底下的所有子物件)
	@param  assetName_override - 輸出過程用此取代該 物件 原本的 assetName
	@param  ignorDuplicateName - 忽略相同物件名稱的衝突，輸入相同的 geoCache
	@param        conflictList - 物件路徑與名稱只要包含此陣列參數內的字串就跳過輸入
	@param             didWrap - 此為輸入程序內部進行 wrap 遞迴時所用，紀錄已經處理過的 wrap 物件，以避免無限遞迴
	"""
	logger.info('GeoCache import init.')

	# namespace during action
	workingNS = moRules.rWorkingNS()
	viskeyNS = moRules.rViskeyNS()
	rigkeyNS = moRules.rRigkeyNS()
	nodeOutNS = moRules.rNodeOutNS()

	# get list of items to process
	rootNode_List = _getRootNode(assetName_override)
	partial_Dict = {}.fromkeys(rootNode_List, [])

	# partial mode
	if isPartial:
		# 取得局部選取範圍的物件清單並建立成字典
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

	# 作業開始，依序處理各個 asset
	for rootNode in rootNode_List:
		if isPartial and not partial_Dict[rootNode]:
			logger.debug('No partial selection under [' + rootNode + '] .')
			continue

		logger.info('[' + rootNode + ']' + (' PARTIAL' if isPartial else '') + ' importing.')

		# loop vars
		workRoot = moRules.rWorkspaceRoot()
		assetNS = moRules.rAssetNS(rootNode)
		assetName = moRules.rAssetName(assetNS) if not assetName_override else assetName_override
		geoCacheDir = getGeoCacheDir(assetName, 0, sceneName)
		geoFileType = moRules.rGeoFileType()
		conflictList = [] if conflictList is None else conflictList
		staticInfo = []

		if not cmds.file(geoCacheDir, q= 1, ex= 1):
			logger.warning('[' + rootNode + '] geoCacheDir not exists -> ' + geoCacheDir)
			continue

		# go set frameRate and playback range
		timeInfoFile = moRules.rTimeInfoFilePath(geoCacheDir, assetName)
		if cmds.file(timeInfoFile, q= 1, ex= 1):
			staticInfo = moMethod.mImportTimeInfo(timeInfoFile)
			logger.info('TimeInfo imported.')
		else:
			logger.warning('[' + rootNode + '] TimeInfo not exists.')

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
					moMethod.mImportGeoCache(xmlFile, assetNS, anim_trans, conflictList, ignorDuplicateName, staticInfo)
				else:
					logger.warning('[' + rootNode + '] XML not exists -> ' + xmlFile)
		else:
			logger.warning('[' + rootNode + '] No geoList file to follow.')


		# get outkey from ma file
		outAniNodeList = moMethod.mLoadOutKeyList(geoCacheDir, '_input.json')
		if not isPartial:
			if outAniNodeList:
				logger.info('nodeOutNS: <' + nodeOutNS + '> Del.')
				# remove mGCVisKey namespace
				moMethod.mCleanWorkingNS(':' + assetName + nodeOutNS)
				logger.info('[' + rootNode + ']' + ' importing nodeOut key.')
				for outAniNode in outAniNodeList:
					keyFile = moRules.rOutkeyFilePath(geoCacheDir, assetName, outAniNode)
					if cmds.file(keyFile, q= 1, ex= 1):
						# import viskey and keep mGCVisKey namespace in viskey
						moMethod.mImportOutkey(keyFile, assetNS, assetName, assetName + nodeOutNS + ':' + outAniNode)
			else:
				logger.warning('[' + rootNode + '] No nodeOut key file to import.')
		else:
			pass

		# get viskey from ma file
		visAniNodeList = moMethod.mLoadVisKeyList(geoCacheDir, '_visKeys.ma')
		if visAniNodeList:
			if isPartial:
				visAniNodeList = [ dag for dag in visAniNodeList if dag in partial_Dict[rootNode] ]
			else:
				logger.info('viskeyNS: <' + viskeyNS + '> Del.')
				# remove mGCVisKey namespace
				moMethod.mCleanWorkingNS(':' + assetName + viskeyNS)

		if visAniNodeList:
			logger.info('[' + rootNode + ']' + (' PARTIAL' if isPartial else '') + ' importing visibility key.')
			for visAniNode in visAniNodeList:
				keyFile = moRules.rViskeyFilePath(geoCacheDir, assetName, visAniNode)
				if cmds.file(keyFile, q= 1, ex= 1):
					# import viskey and keep mGCVisKey namespace in viskey
					moMethod.mImportViskey(keyFile, assetNS, assetName, assetName + viskeyNS + ':' + visAniNode)
		else:
			logger.warning('[' + rootNode + '] No visibility key file to import.')

		# get rigging ctrls from ma file
		rigFile = moRules.rRigkeyFilePath(geoCacheDir, assetName)
		if cmds.file(rigFile, q= 1, ex= 1):
			# remove mGCRigKey namespace
			moMethod.mCleanWorkingNS(':' + assetName + rigkeyNS)
			# import rigging ctrls
			moMethod.mImportRigkey(rigFile)
		else:
			logger.warning('[' + rootNode + '] No rigging controls to import.')

		logger.info('[' + rootNode + ']' + (' PARTIAL' if isPartial else '') + ' imported.')

		# check wrap
		didWrap = [] if didWrap is None else didWrap
		wrapDict = moMethod.mGetWrappingList(assetName)
		if not isPartial and wrapDict:
			logger.info('[' + rootNode + ']' + ' has wrap set.')
			wBatchDict = {}
			willWrap = []
			# collect all wrapSet in this batch
			current = cmds.currentTime(q= 1)
			# 為了正確的執行 wrap, 將影格切到最有可能是 T Pose 的第 0 格
			cmds.currentTime(0)
			for wSet in wrapDict:
				if wSet not in didWrap:
					# convert name
					wSource = wrapDict[wSet]['source']
					wTarget = wrapDict[wSet]['target']
					wSource, wTarget = moMethod.mFindWrapObjsName(wSource, wTarget, assetNS, conflictList)
					if wSource and wTarget:
						# check if wrap source has cached or wrapped in last iter
						if moMethod.mWrapSourceHasCached(wSource):
							wBatchDict[wSource] = wTarget
							willWrap.append(wSet)
							logger.info('[' + rootNode + '] WrapSet <' + wSet + '> Source has cache, do wrap.')
							# 如果 wrap 的 source 物件或其父群組物件的狀態為隱藏，就會在 export 過程中被忽略
							# 最好將需要 wrap 的物件分類到明顯的群組管理其顯示狀態
							moMethod.mDoWrap(wSource, wTarget)
					else:
						logger.warning('[' + rootNode + '] WrapSet <' + wSet + '> Name refind failed.')
			cmds.currentTime(current)
			# 執行 Wrap 之後，進行自體 geoCache 輸出與輸入，將 wrap 變形器 cache 起來並刪除 wrap 變形器
			if wBatchDict:
				wTargetBat = [t for wt in wBatchDict.values() for t in wt]
				logger.info('[' + rootNode + ']' + ' Starting cache wrapped object.')
				cmds.select(wTargetBat, r= 1)
				exportGeoCache(isPartial= True, assetName_override= assetName_override)
				logger.info('[' + rootNode + ']' + ' Removing cached source.')
				moMethod.mRemoveWrap(wBatchDict.keys(), wTargetBat)
				logger.info('[' + rootNode + ']' + ' Starting import cached wrap source.')
				sName = moRules.rCurrentSceneName()
				cmds.select(wTargetBat, r= 1)
				importGeoCache(sName, True, assetName_override, ignorDuplicateName, conflictList, willWrap)

	logger.info('GeoCache' + (' PARTIAL' if isPartial else '') + ' import completed.')
