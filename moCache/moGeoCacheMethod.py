# -*- coding:utf-8 -*-
'''
Created on 2016.05.12

@author: davidpower
'''
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import mMaya.mOutliner as mOutliner; reload(mOutliner)
import mMaya.mGeneral as mGeneral; reload(mGeneral)
import os
import logging

logger = logging.getLogger('MayaOil.moGeocache.Method')


def mCleanWorkingNS(workingNS):
	"""
	"""
	mGeneral.namespaceDel(workingNS)


def mSetupWorkingNS(workingNS):
	"""
	"""
	mGeneral.namespaceSet(workingNS)


def mProcQueue():
	"""
	傳回物件清單，可建立不同入列規則來產生不同範圍的物件清單
	"""
	expList = []

	''' list out objs '''
	# << get selection's root transform node >>
	expList = mOutliner.findRoot('transform')
	expList.sort()

	return expList


def mPartialQueue(partial_Dict):
	"""
	"""
	selection = cmds.ls(sl= 1, l= 1)
	for rootNode in partial_Dict.keys():
		for dag in selection:
			if dag.startswith('|' + rootNode):
				partial_Dict[rootNode].append(dag.split('|')[-1].split(':')[-1])
				dagShape = cmds.listRelatives(dag, s= 1, ni= 1)
				if dagShape:
					partial_Dict[rootNode].append(dagShape[0].split(':')[-1])

	return partial_Dict


def mFilterOut(rootNode):
	"""
	過濾不必要的物件
	"""
	# meshes need to process
	anim_meshes = []
	# meshes have visible animation
	anim_viskey = []

	def _set(mylist):
		# 先檢查 list 是否為空的，再轉 set
		return set(mylist) if mylist else None

	''' # FILTER OUT # <intermediate objects> '''
	# intermediate objects
	itrm_meshes = _set(mOutliner.findIMObj(rootNode))
	# meshes without intermediate objects
	anim_meshes = _set(cmds.listRelatives(rootNode, ad= 1, f= 1, typ= 'mesh')) - itrm_meshes

	''' # FILTER OUT # <constant hidden objects> '''
	anim_dags = list(anim_meshes)
	for mesh in anim_meshes:
		anim_dags.append(cmds.listRelatives(mesh, p= 1, f= 1)[0])
	
	for obj in cmds.listRelatives(rootNode, ad= 1, f= 1):
		objShouldRemove = False
		if cmds.attributeQuery('visibility', ex= 1, node = obj):
			# check if visibility has being connected to something like animCurve, expression or drivenKey
			if not cmds.listConnections(obj + '.v'):
				if not cmds.getAttr(obj + '.v'):
					# constant hidden objects
					objShouldRemove = True
					logger.debug('No visibility key -x [' + obj.split('|')[-1] + ']')
			else:
				# do something if has key, expression or drivenKey connected to visibility
				drivers = cmds.setDrivenKeyframe(obj + '.v', q= 1, dr= 1)
				if drivers[0] == 'No drivers.':
					# has key or expression
					doAppend = False
					if cmds.objectType(obj) == 'transform' and cmds.listRelatives(obj, s= 1):
						if cmds.objectType(cmds.listRelatives(obj, s= 1, f= 1)[0]) == 'mesh':
							doAppend = True
					if cmds.objectType(obj) == 'mesh':
						doAppend = True
					if doAppend:
						anim_viskey.append(obj)
						logger.warning('Visibility key detected -> [' + obj.split('|')[-1] + ']')
					else:
						logger.debug('Visibility key NOT in mesh -> [' + obj.split('|')[-1] + ']')
				else:
					# is a driven obj
					driverHasAni = 0
					for driver in drivers:
						if cmds.listConnections(driver, s= 1, d= 0):
							# one of drivers has key or expression
							doAppend = False
							if cmds.objectType(obj) == 'transform' and cmds.listRelatives(obj, s= 1):
								if cmds.objectType(cmds.listRelatives(obj, s= 1, f= 1)[0]) == 'mesh':
									doAppend = True
							if cmds.objectType(obj) == 'mesh':
								doAppend = True
							if doAppend:
								anim_viskey.append(obj)
								driverHasAni = 1
								logger.warning('Visibility drivenKey detected -> [' + obj.split('|')[-1] + ']')
								break
					# driver has no animation, remove obj
					if not driverHasAni:
						if not cmds.getAttr(obj + '.v'):
							# constant hidden objects
							objShouldRemove = True
							logger.debug('No visibility drivenKey -x [' + obj.split('|')[-1] + ']')

			if objShouldRemove:
				# no visibility animation, check if transform obj has mesh or other child
				if cmds.objectType(obj) == 'transform':
					hiddenChild = _set(cmds.listRelatives(obj, ad= 1, f= 1))
					if hiddenChild:
						# remove hidden meshes
						anim_meshes = anim_meshes - hiddenChild
				if cmds.objectType(obj) == 'mesh':
					# remove hidden mesh
					if obj in anim_meshes:
						anim_meshes.remove(obj)

	return anim_meshes, anim_viskey


def mDuplicateSelectedOnly(doConstrain= None):
	"""
	"""
	targetList = pm.ls(sl= 1)
	desGrp = pm.group(n= 'mDuplicateSelectedOnly', w= 1, em= 1)
	newDags = []
	for target in targetList:
		par = pm.duplicate(target, po=1)[0]
		pm.parent(par, desGrp)
		par.rename(target)
		shp = pm.duplicate(target.getShape(), addShape=True)[0]
		shp.setParent(par, s= 1)
		new = par.getChildren()[0]
		pm.parent(new, desGrp)
		n = par.name()
		pm.delete(par)
		new.rename(n)
		# currently return string type for cmds cmd
		newDags.append(new.name())
		if doConstrain:
			pm.parentConstraint(target, new, mo= 1)

	return newDags


def mBakeViskey(anim_viskey, playbackRange):
	"""
	"""
	cmds.bakeResults(anim_viskey, at= '.v', t= playbackRange, sm= 1, s= 0)


def mBakeRigkey(rigCtrlList, playbackRange):
	"""
	"""
	cmds.bakeResults(rigCtrlList, at= ['.t', '.r', '.s'], t= playbackRange, sm= 1, s= 0)
	for ctrl in rigCtrlList:
		findPC = cmds.listRelatives(ctrl, c= 1, typ= 'parentConstraint')
		if findPC:
			for pc in findPC:
				cmds.delete(pc)


def mDuplicateViskey(anim_viskey):
	"""
	"""
	visAniNodeList = []
	for visNode in anim_viskey:
		aniNode = cmds.listConnections(visNode + '.visibility')[0]
		visAniNodeList.append(cmds.duplicate(aniNode, n= visNode)[0])

	return visAniNodeList


def mPolyUniteMesh(anim_meshes):
	"""
	"""
	# create a group for geoCaching carrier
	ves_grp = cmds.group(em= 1, n= 'polyUniteVesGrp')
	# convert meshes by polyUnite node into geoCaching carrier
	for animShpae in anim_meshes:
		# get transform node's name without namespace
		animTrans = cmds.listRelatives(animShpae, p= 1)[0].split(':')[-1]
		# create a polyCube as a carrier for geoCaching and match name 
		vesTrans = cmds.polyCube(n= animTrans, ch= 0)[0]
		# rename polyCube's shape node to match name
		vesShape = cmds.rename(cmds.listRelatives(vesTrans, s= 1)[0], animShpae)
		# put in to the geoCaching carrier's group
		cmds.parent(vesTrans, ves_grp)
		# create polyUnite node
		pUnite = cmds.createNode('polyUnite', n= 'polyUnite_' + animTrans)
		# carrier load up
		cmds.connectAttr(animShpae + '.worldMatrix', pUnite + '.inputMat[0]')
		cmds.connectAttr(animShpae + '.worldMesh', pUnite + '.inputPoly[0]')
		cmds.connectAttr(pUnite + '.output', vesShape + '.inMesh')

	return ves_grp


def mSmoothMesh(ves, subdivLevel):
	"""
	"""
	cmds.polySmooth(ves, mth= 0, sdt= 2, ovb= 1, ofb= 3, ofc= 0, ost= 1,
							ocr= 0, dv= subdivLevel, bnr= 1 ,c= 1, kb= 1, ksb= 1,
							khe= 0, kt= 1, kmb= 1, suv= 1, peh= 0, sl= 1,
							dpe= 1, ps= 0.1, ro= 1, ch= 0)


def mSaveGeoList(geoListFile):
	"""
	write out an empty file, we only need file name
	"""
	with open(geoListFile, 'w') as geomoTxt:
		pass


def mLoadGeoList(geoCacheDir, workingNS, geoFileType):
	"""
	"""
	anim_geoDict = {}

	workingNS = workingNS.split(':')[-1]
	logger.debug(geoCacheDir)
	for geoFile in os.listdir(geoCacheDir):
		if geoFile.endswith(geoFileType):
			geo = geoFile.split(workingNS + '_')[-1].split(geoFileType)[0]
			geo_trans = geo.split('@')[1]
			geo_shape = geo.split('@')[0]
			anim_geoDict[geo_trans] = geo_shape

	return anim_geoDict


def mLoadVisKeyList(geoCacheDir, mayaFileType):
	"""
	"""
	visAniNodeList = []
	for mayaFile in os.listdir(geoCacheDir):
		if mayaFile.endswith(mayaFileType):
			visAniNode = mayaFile.split('@')[1].split(mayaFileType)[0]
			visAniNodeList.append(visAniNode)

	return visAniNodeList


def mExportViskey(keyFile):
	"""
	輸出 visible key
	"""
	cmds.file(keyFile, f= 1, op= "v=0;", typ= "mayaAscii", es= 1)


def mImportViskey(keyFile, assetNS, visAniNode):
	"""
	"""
	visAniMesh = ''
	targetList = cmds.ls('*' + visAniNode.split(':')[-1], r= 1, l= 1)
	
	try:
		visAniMesh = [target for target in targetList if target.startswith('|' + assetNS)][0]
	except:
		logger.warning('viskey target not found [' + visAniNode + '] -x')
		return

	if cmds.objectType(visAniMesh) == 'mesh' and cmds.getAttr(visAniMesh + '.intermediateObject'):
		visAniMesh = cmds.listRelatives(cmds.listRelatives(visAniMesh, p= 1)[0], s= 1, ni= 1, f= 1)[0]
	
	try:
		inputAni = cmds.listConnections(visAniMesh + '.visibility', p= 1, t= 'animCurve')
		if inputAni:
			try:
				cmds.disconnectAttr(inputAni[0], visAniMesh + '.visibility')
				cmds.delete(inputAni[0].split('.')[0])
				logger.warning('viskey PARTIAL deleted. [' + inputAni[0] + ']')
			except:
				logger.warning('viskey PARTIAL delete failed. [' + inputAni[0] + ']')
		cmds.file(keyFile, i= 1, typ= 'mayaAscii', iv= 1, mnc= 1, ns= ':')
		cmds.connectAttr(visAniNode + '.output', visAniMesh + '.visibility')
		logger.info('viskey target connected. [' + visAniNode + '] -> {' + visAniMesh + '}')
	except:
		logger.warning('viskey target connection failed. [' + visAniNode + '] -x {' + visAniMesh + '}')


def mExportRigkey(rigFile):
	"""
	輸出 rigging ctrls
	"""
	cmds.file(rigFile, f= 1, op= "v=0;", typ= "mayaAscii", es= 1)


def mImportRigkey(rigFile):
	"""
	"""
	cmds.file(rigFile, i= 1, typ= 'mayaAscii', iv= 1, mnc= 1, ns= ':')


def mExportGeoCache(geoCacheDir, assetName):
	"""
	設定 geoCache 參數並執行
	"""
	# doCreateGeometryCache( int $version, string $args[] )
	# C:/Program Files/Autodesk/Maya2016/scripts/others/doCreateGeometryCache.mel
	version = 6

	def _gcArgs():
		# time range mode:
		# 		mode = 0 : use $args[1] and $args[2] as start-end
		# 		mode = 1 : use render globals
		# 		mode = 2 : use timeline
		timerangeMode = 2
		# start frame (if time range mode == 0)
		startFrame = 0
		# end frame (if time range mode == 0)
		endFrame = 0
		# cache file distribution, either "OneFile" or "OneFilePerFrame"
		cacheDistr = 'OneFilePerFrame'
		# 0/1, whether to refresh during caching
		refresh = '0'
		# directory for cache files, if "", then use project data dir
		cacheDir = geoCacheDir
		# 0/1, whether to create a cache per geometry
		perGeo = 1
		# name of cache file. An empty string can be used to specify that an auto-generated name is acceptable.
		cacheName = assetName
		# 0/1, whether the specified cache name is to be used as a prefix
		usePrefix = 1
		# action to perform: "add", "replace", "merge", "mergeDelete" or "export"
		action = 'export'
		# force save even if it overwrites existing files
		force = 1
		# simulation rate, the rate at which the cloth simulation is forced to run
		simRate = 1
		# sample mulitplier, the rate at which samples are written, as a multiple of simulation rate.
		sample = 1
		# 0/1, whether modifications should be inherited from the cache about to be replaced. Valid only when action = "replace".
		inherited = 0
		# 0/1, whether to store doubles as floats
		storeFloat = 1
		# name of cache format: "mcc", "mcx"
		cFormat = 'mcx'
		# 0/1, whether to export in local or world space
		space = 0

		return locals()

	def _qts(var):
		# surround string with double quote
		return '"' + str(var) + '"'

	# get all geoCache inputs value 
	args = [ _qts(_gcArgs()[var]) for var in _gcArgs.__code__.co_varnames ]
	# make cmd and do GeoCache
	evalCmd = 'doCreateGeometryCache ' + str(version) + ' {' + ', '.join(args) + '};'
	logger.debug('GeoCache export CMD : ' + evalCmd)
	mel.eval(evalCmd)


def mImportGeoCache(xmlFile, assetNS, anim_trans, conflictList, ignorDuplicateName):
	"""
	"""
	def importGeoProcess(dag):
		inputAni = []
		anim_relatives = cmds.listRelatives(dag, s= 1, ni= 1, f= 1)
		if anim_relatives:
			anim_shape = anim_relatives[0]
			if cmds.objectType(anim_shape) != 'mesh':
				return
			if not cmds.getAttr(anim_shape + '.v'):
				# check if shape node is hidden by visKey
				inputAni = cmds.listConnections(anim_shape + '.visibility', p= 1, t= 'animCurve')
				if inputAni:
					cmds.disconnectAttr(inputAni[0], anim_shape + '.visibility')
					cmds.setAttr(anim_shape + '.v', 1)
				else:
					return
			cmds.select(dag, r= 1)
			# delete cache
			for obj in cmds.ls(sl= 1):
				cacheDeleted = 0
				hist = cmds.listHistory(obj, pdo= 1)
				if hist:
					for histNode in hist:
						if cmds.nodeType(histNode) == 'cacheFile':
							cmds.delete(histNode)
							cacheDeleted = 1
				if not cacheDeleted:
					logger.info('No caches Del. -> ' + obj)
			# import new cache
			mel.eval('source doImportCacheArgList')
			mel.eval('importCacheFile "' + xmlFile + '" "Best Guess"')
			if inputAni:
				cmds.connectAttr(inputAni[0], anim_shape + '.visibility')
		else:
			logger.warning('This node might not contenting shape node, but source rigging file dose.')

	targetList = cmds.ls('*' + anim_trans, r= 1, l= 1, et= 'transform')
	# conflictList: if conflict string included in dag name, remove in next step
	inverseResult = [T for T in targetList for C in conflictList if not T.startswith('|' + assetNS) or C in T]
	anim_transList = list(set(targetList) - set(inverseResult))
	if len(anim_transList) == 1:
		importGeoProcess(anim_transList[0])
	elif len(anim_transList) > 1:
		logger.warning('Conflict, too many target -> ' + anim_trans)
		for trans in anim_transList:
			logger.warning('-x ' + trans)
			if ignorDuplicateName:
				logger.warning('Ignor duplicate names... ')
				importGeoProcess(trans)
	else:
		logger.warning('No target found -> ' + anim_trans)


def mExportTimeInfo(timeInfoFile, timeUnit, playbackRange):
	"""
	"""
	timeInfo = timeUnit + '\n' + str(playbackRange[0]) + ':' + str(playbackRange[1])
	with open(timeInfoFile, 'w') as timeInfoTxt:
		timeInfoTxt.write(timeInfo)


def mImportTimeInfo(timeInfoFile):
	"""
	"""
	with open(timeInfoFile, 'r') as timeInfoTxt:
		timeInfo = timeInfoTxt.read().split('\n')
		cmds.currentUnit(t= timeInfo[0])
		logger.info('TimeInfo   [Unit] ' + timeInfo[0])
		cmds.playbackOptions(min= float(timeInfo[1].split(':')[0]))
		cmds.playbackOptions(max= float(timeInfo[1].split(':')[1]))
		logger.info('TimeInfo  [Range] ' + timeInfo[1])


def mGetSmoothMask(assetName):
	"""
	"""
	meshSmoothmask = []
	setList = cmds.ls('*moGeoCacheSmoothMask', r= 1, typ= 'objectSet')
	if setList:
		for set in setList:
			if ':' not in set or (':' in set and set.startswith(assetName)):
				for obj in cmds.sets(set, q= 1, no= 1):
					meshSmoothmask.append(obj.split(':')[-1])
				break
				
	return meshSmoothmask


def mGetRigCtrlExportList(assetName):
	"""
	"""
	rigCtrlList = []
	setList = cmds.ls('*moGeoCacheRigCtrlExport', r= 1, typ= 'objectSet')
	if setList:
		for set in setList:
			if ':' not in set or (':' in set and set.startswith(assetName)):
				for obj in cmds.sets(set, q= 1, no= 1):
					rigCtrlList.append(obj)
				break
				
	return rigCtrlList
