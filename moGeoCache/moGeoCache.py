# -*- coding:utf-8 -*-
'''
Created on 2016.04.28

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
import moGeoCache.moGeoCacheRules as moRules
import moGeoCache.moGeoCacheMethod as moMethod



def doExportViskey(geoCacheDir, assetName):
	"""
	輸出 visible key
	"""
	# do export
	keyFile = moRules.rViskeyFilePath(geoCacheDir, assetName)
	cmds.file(keyFile, f= 1, op= "v=0;", typ= "mayaAscii", es= 1)


def doGeoCache(geoCacheDir, assetName):
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
		perGeo = 0
		# name of cache file. An empty string can be used to specify that an auto-generated name is acceptable.
		cacheName = assetName
		# 0/1, whether the specified cache name is to be used as a prefix
		usePrefix = 0
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
	#print evalCmd
	mel.eval(evalCmd)


def exportGeoCache():
	"""
	輸出 geoCache
	"""
	# get list of items to process
	rootNode_List = moMethod.mProcQueue()
	# namespace during action
	workingNS = moRules.rWorkingNamespace()
	# remove mGC namespace
	moMethod.mCleanWorkingNS(workingNS)

	for rootNode in rootNode_List:
		# FILTER OUT <intermediate objects> & <constant hidden objects>
		tmpResult = moMethod.mFilterOut(rootNode)
		# loop vars
		anim_meshes = tmpResult[0]
		anim_viskey = tmpResult[1]
		assetNamespace = moRules.rAssetNamespace(rootNode)
		assetName = moRules.rAssetName(assetNamespace)
		geoCacheDir = moRules.rGeoCacheDir(assetName)
		
		# Add and Set namespace
		moMethod.mSetupWorkingNS(workingNS)

		if anim_viskey and False:
			# collect all visibility animation node
			visAniNodeList = moMethod.mDuplicateViskey(anim_viskey)
			# export visKey
			cmds.select(visAniNodeList, r= 1)
			doExportViskey(geoCacheDir, assetName)

		if anim_meshes:
			# polyUnite
			ves_grp = moMethod.mPolyUniteMesh(anim_meshes)
			# smooth 1 level before export
			moMethod.mSmoothMesh(ves_grp)
			# write out transform node's name
			transFile = moRules.rTransNameFilePath(geoCacheDir, assetName)
			moMethod.mSaveTransformName(ves_grp, transFile)
			# export GeoCache
			cmds.select(ves_grp, r= 1, hi= 1)
			doGeoCache(geoCacheDir, assetName)

		# remove mGC namespace
		moMethod.mCleanWorkingNS(workingNS)


def importGeoCache(sceneName):
	"""
	輸入 geoCache
	"""
	# get list of items to process
	rootNode_List = moMethod.mProcQueue()

	for rootNode in rootNode_List:
		# loop vars
		assetNamespace = moRules.rAssetNamespace(rootNode)
		assetName = moRules.rAssetName(assetNamespace)
		geoCacheDir = moRules.rGeoCacheDir(assetName, sceneName)
		xmlFile = moRules.rXMLFilePath(geoCacheDir, assetName)
		transFile = moRules.rTransNameFilePath(geoCacheDir, assetName)

		if cmds.file(xmlFile, q= 1, ex= 1) and cmds.file(transFile, q= 1, ex= 1):
			# get transform list from txt file
			anim_trans = moMethod.mTXTTransList(transFile, rootNode)
			# import GeoCache
			cmds.select(anim_trans, r= 1)
			mel.eval('source doImportCacheArgList')
			mel.eval('if(catch(`deleteCacheFile 3 { "keep", "", "geometry" }`)){print "// moGeoCache: No caches.";}')
			mel.eval('importCacheFile "' + xmlFile + '" "Best Guess"')
		# get viskey from ma file
		keyFile = moRules.rViskeyFilePath(geoCacheDir, assetName)
		if cmds.file(keyFile, q= 1, ex= 1) and False:
			viskeyNamespace = moRules.rViskeyNamespace()
			# import viskey
			moMethod.mImportViskey(keyFile, assetNamespace, viskeyNamespace)



if __name__ == '__main__':
	reload(moRules)
	reload(moMethod)
	exportGeoCache()
	#importGeoCache('SOK_c01_anim_v01')