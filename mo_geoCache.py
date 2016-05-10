# -*- coding:utf-8 -*-
'''
Created on 2016.04.28

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
from xml.dom import minidom
import os
import sys
sys.path.insert(0, 'C:/Users/David/Documents/GitHub/MS_MayaOil')
import mMaya.mOutliner as moln
import mMaya.mGeneral as mgnr
import mo_ioRules as ioRules



def _exportList():
	"""
	傳回物件清單，可建立不同入列規則來產生不同範圍的物件清單
	"""
	expList = []
	# get selection's root transform node
	expList = moln.findRoot('transform')
	# direct using selection
	#expList = cmds.ls(sl= 1)
	# non-gui mode

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
	itrm_meshes = _set(moln.findIMObj(rootNode))
	# meshes without intermediate objects
	anim_meshes = _set(cmds.listRelatives(rootNode, ad= 1, f= 1, typ= 'mesh')) - itrm_meshes

	''' # FILTER OUT # <constant hidden objects> '''
	for obj in moln.findHidden(rootNode):
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


def _doGeoCache(rootName):
	"""
	設定 geoCache 參數並執行
	"""
	# doCreateGeometryCache( int $version, string $args[] )
	# C:/Program Files/Autodesk/Maya2016/scripts/others/doCreateGeometryCache.mel
	version = 6
	rule = ioRules.rule_moGeoCache(rootName)

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
		cacheDir = rule[0]
		# 0/1, whether to create a cache per geometry
		perGeo = 0
		# name of cache file. An empty string can be used to specify that an auto-generated name is acceptable.
		cacheName = rule[1]
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
	mgnr.namespaceDel(mGC_nameSpace)

	''' start procedure '''
	for rootNode in rootNode_List:
		# anim_meshes : meshes need to process
		# anim_viskey : meshes have visible animation
		anim_meshes, anim_viskey = _filterOut(rootNode)

		''' Add and Set namespace '''
		mgnr.namespaceSet(mGC_nameSpace)
		
		''' polyUnite '''
		# create a group for polyUnited meshes
		ves_top = cmds.group(em= 1, n= rootNode.split(':')[-1])
		# convert meshes to polyUnited
		for child in anim_meshes:
			child_basename = child.split(':')[-1]
			ves = cmds.polyCube(n= child_basename, ch= 0)[0]
			namespace_source = ':'.join(rootNode.split(':')[:-1])
			child_source = namespace_source + ':' + child_basename
			cmds.parent(ves, ves_top)
			pUnite = 'polyUnite_' + child_basename
			pUnite = cmds.createNode('polyUnite', n= pUnite)
			cmds.connectAttr(child_source + '.worldMatrix', pUnite + '.inputMat[0]')
			cmds.connectAttr(child_source + '.worldMesh', pUnite + '.inputPoly[0]')
			cmds.connectAttr(pUnite + '.output', ves + '.inMesh')

		''' GeoCache '''
		cmds.select(ves_top, r= 1, hi= 1)
		_doGeoCache(rootNode)

		''' remove mGC namespace '''
		mgnr.namespaceDel(mGC_nameSpace)


def mo_importGeoCache():
	"""
	輸入 geoCache
	"""
	# 將 namespace 或 原本名稱存在另外一份文字或JSON檔案裡?
	Channels = minidom.parse(xmlFile).getElementsByTagName('Channels')[0]
	for ChannelName in Channels.childNodes:
	    if ChannelName.nodeType == ChannelName.ELEMENT_NODE:
	        print ChannelName.getAttribute('ChannelName')