# -*- coding:utf-8 -*-
'''
Created on 2016.04.28

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
import mMaya.mOutliner as mOutliner
import mMaya.mGeneral as mGeneral
import mo_ioRules as ioRules
import xml.dom.minidom as minidom


def _exportList():
	"""
	傳回物件清單，可建立不同入列規則來產生不同範圍的物件清單
	"""
	expListTmp = []

	''' list out objs '''
	# get selection's root transform node
	expListTmp = mOutliner.findRoot('transform')
	# direct using selection
	#expListTmp = cmds.ls(sl= 1)
	# non-gui mode

	''' check if obj in a namespace '''
	expList = expListTmp
	for obj in expListTmp:
		if len(obj.split(':')) > 2:
			if not obj.split(':')[1]:
				expList.remove(obj)

	return expList


def _filterOut(rootNode):
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
	for obj in mOutliner.findHidden(rootNode):
		# check if visibility has being connected to something like animCurve or expression
		if not cmds.listConnections(obj + '.visibility'):
			# no connection, check if transform obj has mesh child
			if cmds.objectType(obj) == 'transform':
				hiddenChild = _set(cmds.listRelatives(obj, ad= 1, f= 1))
				if hiddenChild:
					# remove hidden meshes
					anim_meshes = anim_meshes - hiddenChild
			if cmds.objectType(obj) == 'mesh':
				# remove hidden mesh
				anim_meshes.remove(obj)
		else:
			# do something if has key or expression connected to visibility
			anim_viskey.append(obj)

	return anim_meshes, anim_viskey


def _doExportViskey(assetName, exportDir):
	"""
	輸出 visible key
	"""
	# do export
	cmds.file(exportDir + '/' + assetName, f= 1, op= "v=0;", typ= "mayaAscii", es= 1)


def _doGeoCache(assetName, exportDir):
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
		cacheDir = exportDir
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
	print evalCmd
	mel.eval(evalCmd)


def _chop(objName):
		"""
		remove top namespace and keep the rest
		"""
		return ':'.join(objName.split(':')[1:])


def mo_exportGeoCache():
	"""
	輸出 geoCache
	"""

	''' vars '''
	# get list of items to export
	rootNode_List = _exportList()
	# namespace during action
	mGC_nameSpace = ':mGeoCache'

	''' remove mGC namespace '''
	mGeneral.namespaceDel(mGC_nameSpace)

	''' start procedure '''
	for rootNode in rootNode_List:
		# anim_meshes : meshes need to process
		# anim_viskey : meshes have visible animation
		anim_meshes, anim_viskey = _filterOut(rootNode)
		assetName = rootNode.split(':')[0].split('_')[0]
		exportDir = ioRules.rule_moGeoCache(assetName)

		''' Add and Set namespace '''
		mGeneral.namespaceSet(mGC_nameSpace)

		if anim_viskey:
			pass
			"""
			''' collect all visibility animation node '''
			visAniNodeList = []
			for visNode in anim_viskey:
				node = cmds.listConnections(visNode + '.visibility')[0]
				visAniNode = '__viskey__' + _chop(visNode)
				visAniNodeList.append(cmds.duplicate(node, n= visAniNode)[0])
			''' export visKey '''
			cmds.select(visAniNodeList, r= 1)
			_doExportViskey(assetName, exportDir)
			"""

		if anim_meshes:
			''' polyUnite '''
			# create a group for geoCaching carrier
			ves_top = cmds.group(em= 1, n= _chop(rootNode))
			# convert meshes by polyUnite node into geoCaching carrier
			for animShpae in anim_meshes:
				# get transform node's name without namespace
				animTrans = _chop(cmds.listRelatives(animShpae, p= 1)[0])
				# create a polyCube as a carrier for geoCaching and match name 
				vesTrans = cmds.polyCube(n= animTrans, ch= 0)[0]
				# rename polyCube's shape node to match name
				vesShape = cmds.rename(cmds.listRelatives(vesTrans, s= 1)[0], _chop(animShpae))
				# put in to the geoCaching carrier's group
				cmds.parent(vesTrans, ves_top)
				# create polyUnite node
				pUnite = cmds.createNode('polyUnite', n= 'polyUnite_' + animTrans)
				# carrier load up
				cmds.connectAttr(animShpae + '.worldMatrix', pUnite + '.inputMat[0]')
				cmds.connectAttr(animShpae + '.worldMesh', pUnite + '.inputPoly[0]')
				cmds.connectAttr(pUnite + '.output', vesShape + '.inMesh')
			''' export GeoCache '''
			cmds.select(ves_top, r= 1, hi= 1)
			_doGeoCache(assetName, exportDir)

		''' remove mGC namespace '''
		mGeneral.namespaceDel(mGC_nameSpace)


def mo_importGeoCache(sceneName):
	"""
	輸入 geoCache
	"""

	''' vars '''
	# get list of items to export
	rootNode_List = _exportList()

	''' start procedure '''
	for rootNode in rootNode_List:
		# anim_meshes : meshes need to process
		# anim_viskey : meshes have visible animation
		anim_meshes = []
		anim_viskey = []
		assetNamespace = rootNode.split(':')[0]
		assetName = assetNamespace.split('_')[0]
		importDir = ioRules.rule_moGeoCache(assetName, sceneName)

		''' get mesh list from xml file '''
		xmlFile = importDir + '/' + assetName + '.xml'
		Channels = minidom.parse(xmlFile).getElementsByTagName('Channels')[0]
		for ChannelName in Channels.childNodes:
			if ChannelName.nodeType == ChannelName.ELEMENT_NODE:
				meshName = assetNamespace + ':' + _chop(ChannelName.getAttribute('ChannelName'))
				anim_meshes.append(meshName)

		''' import GeoCache '''
		cmds.select(anim_meshes, r= 1)
		mel.eval('importCacheFile "' + xmlFile + '" "Best Guess";')

		"""
		''' import viskey '''
		keyFile = importDir + '/' + assetName + '.ma'
		viskeyNamespace = assetNamespace + ':geoViskey'
		cmds.file(keyFile, i= 1, typ= 'mayaAscii', iv= 1, ra= 1, ns= viskeyNamespace)
		visAniNodeList = cmds.namespaceInfo(viskeyNamespace, lod= 1)
		for visAniNode in visAniNodeList:
			visAniMesh = assetNamespace + ':' + visAniNode.split('__viskey__')[1]
			cmds.connectAttr(visAniNode + '.output', visAniMesh + '.visibility')
		"""



if __name__ == '__main__':
	reload(mOutliner)
	reload(mGeneral)
	reload(ioRules)
	#mo_exportGeoCache()
	mo_importGeoCache('SOK_c02_c03_anim_v04Vis')