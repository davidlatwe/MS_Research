# -*- coding:utf-8 -*-
'''
Created on 2016.05.12

@author: davidpower
'''
import logging
logger = logging.getLogger('MayaOil.moGeocache.Method')

import maya.cmds as cmds
import maya.mel as mel
import mMaya.mOutliner as mOutliner
import mMaya.mGeneral as mGeneral


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
	for obj in cmds.listRelatives(rootNode, ad= 1, f= 1):
		objShouldRemove = False
		if cmds.attributeQuery('visibility', ex= 1, node = obj):
			# check if visibility has being connected to something like animCurve, expression or drivenKey
			if not cmds.listConnections(obj + '.v'):
				if not cmds.getAttr(obj + '.v'):
					objShouldRemove = True
			else:
				# do something if has key, expression or drivenKey connected to visibility
				drivers = cmds.setDrivenKeyframe(obj + '.v', q= 1, dr= 1)
				if drivers[0] == 'No drivers.':
					# has key or expression
					anim_viskey.append(obj)
				else:
					# is a driven obj
					driverHasAni = 0
					for driver in drivers:
						if cmds.listConnections(driver, s= 1, d= 0):
							# one of drivers has key or expression
							anim_viskey.append(obj)
							driverHasAni = 1
							break
					# driver has no animation, remove obj
					if not driverHasAni:
						if not cmds.getAttr(obj + '.v'):
							objShouldRemove = True

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


def mBakeViskey(anim_viskey, playbackRange):
	"""
	"""
	cmds.bakeResults(anim_viskey, at= '.v', t= playbackRange, sm= 1, s= 0)


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
		animTrans = cmds.listRelatives(animShpae, p= 1)[0]
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


def mSmoothMesh(ves_grp, excludeList):
	"""
	"""
	for ves in cmds.listRelatives(ves_grp, c= 1):
		if ves.split(':')[-1] not in excludeList:
			cmds.polySmooth(ves, mth= 0, sdt= 2, ovb= 1, ofb= 3, ofc= 0, ost= 1,
									ocr= 0, dv= 1, bnr= 1 ,c= 1, kb= 1, ksb= 1,
									khe= 0, kt= 1, kmb= 1, suv= 1, peh= 0, sl= 1,
									dpe= 1, ps= 0.1, ro= 1, ch= 0)


def mSaveGeoList(ves_grp, geoListFile):
	"""
	"""
	with open(geoListFile, 'w') as geoTxt:
		for ves in cmds.listRelatives(ves_grp, c= 1):
			vesShape = cmds.listRelatives(ves, s= 1)[0]
			geoTxt.write(ves.split(':')[-1] + '@' + vesShape.split(':')[-1] + '\n')


def mTXTGeoList(geoListFile, rootNode):
	"""
	"""
	# transform nodes need to select
	anim_geoList = {}
	target_trans = cmds.listRelatives(rootNode, ad= 1, typ= 'transform')

	with open(geoListFile, 'r') as geoTxt:
		for geo in geoTxt:
			geo_trans = geo.strip().split('@')[0]
			geo_shape = geo.strip().split('@')[1]
			for target in target_trans:
				if target.split(':')[-1] == geo_trans and not 'LP_geo_grp' in target:
					anim_geoList[target] = geo_shape
					break

	return anim_geoList


def mExportViskey(keyFile):
	"""
	輸出 visible key
	"""
	cmds.file(keyFile, f= 1, op= "v=0;", typ= "mayaAscii", es= 1)


def mImportViskey(keyFile, assetNS, viskeyNS):
	"""
	"""
	cmds.file(keyFile, i= 1, typ= 'mayaAscii', iv= 1, mnr= 1)
	visAniNodeList = cmds.namespaceInfo(viskeyNS, lod= 1)
	for visAniNode in visAniNodeList:
		try:
			targetList = cmds.ls('*' + visAniNode.split(':')[1], r= 1, l= 1)
			visAniMesh = [target for target in targetList if target.startswith(assetNS)][0]
			cmds.connectAttr(visAniNode + '.output', visAniMesh + '.visibility')
		except:
			logger.warning('viskey target not found:  ' + visAniNode)


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
	logger.debug(evalCmd)
	mel.eval(evalCmd)


def mImportGeoCache(xmlFile, assetNS, anim_trans):
	"""
	"""
	targetList = cmds.ls('*' + anim_trans, r= 1, l= 1)
	anim_trans = [target for target in targetList if target.startswith('|' + assetNS) and not 'LP_geo_grp' in target][0]
	cmds.select(anim_trans, r= 1);logger.debug(anim_trans)
	mel.eval('source doImportCacheArgList')
	mel.eval('if(catch(`deleteCacheFile 3 { "keep", "", "geometry" }`)){warning "// moGeoCache: No caches.";}')
	#mel.eval('if(catch(`deleteCacheFile 3 {"keep", "", "geometry"}`)){python "logger.warning(\"No caches Del.\")";}')
	mel.eval('importCacheFile "' + xmlFile + '" "Best Guess"')


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
		cmds.playbackOptions(q= 1, min= float(timeInfo[1].split(':')[0]))
		cmds.playbackOptions(q= 1, max= float(timeInfo[1].split(':')[1]))


def mGetSmoothExcludeList():
	"""
	"""
	return ['R_eye_geo3',
			'R_eye_geo2',
			'L_eye_geo3',
			'L_eye_geo2',
			'R_arm_cloth_geo4'
			]