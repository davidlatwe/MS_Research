# -*- coding:utf-8 -*-
'''
Created on 2016.05.12

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
import mMaya.mOutliner as mOutliner
import mMaya.mGeneral as mGeneral
import xml.dom.minidom as minidom



def _chopNS(objName):
		"""
		remove top namespace and keep the rest
		"""
		return ':'.join(objName.split(':')[1:])


def mProcQueue():
	"""
	傳回物件清單，可建立不同入列規則來產生不同範圍的物件清單
	"""
	expListTmp = []

	''' list out objs '''
	#<< get selection's root transform node >>
	expListTmp = mOutliner.findRoot('transform')
	#<< direct using selection >>
	#expListTmp = cmds.ls(sl= 1)
	#<< non-gui mode >>
	#pass

	''' check if obj in a namespace '''
	expList = expListTmp
	for obj in expListTmp:
		if len(obj.split(':')) > 2:
			if not obj.split(':')[1]:
				expList.remove(obj)

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


def mBakeViskey(anim_viskey):
	"""
	"""
	timeRange = (cmds.playbackOptions(q= 1, min= 1), cmds.playbackOptions(q= 1, max= 1))
	cmds.bakeResults(anim_viskey, at= '.v', t= timeRange, sm= 1, s= 0)


def mDuplicateViskey(anim_viskey):
	"""
	"""
	visAniNodeList = []
	for visNode in anim_viskey:
		aniNode = cmds.listConnections(visNode + '.visibility')[0]
		visAniNode = _chopNS(visNode)
		visAniNodeList.append(cmds.duplicate(aniNode, n= visAniNode)[0])

	return visAniNodeList


def mPolyUniteMesh(anim_meshes):
	"""
	"""
	# create a group for geoCaching carrier
	ves_grp = cmds.group(em= 1, n= 'polyUniteVesGrp')
	# convert meshes by polyUnite node into geoCaching carrier
	for animShpae in anim_meshes:
		# get transform node's name without namespace
		animTrans = _chopNS(cmds.listRelatives(animShpae, p= 1)[0])
		# create a polyCube as a carrier for geoCaching and match name 
		vesTrans = cmds.polyCube(n= animTrans, ch= 0)[0]
		# rename polyCube's shape node to match name
		vesShape = cmds.rename(cmds.listRelatives(vesTrans, s= 1)[0], _chopNS(animShpae))
		# put in to the geoCaching carrier's group
		cmds.parent(vesTrans, ves_grp)
		# create polyUnite node
		pUnite = cmds.createNode('polyUnite', n= 'polyUnite_' + animTrans)
		# carrier load up
		cmds.connectAttr(animShpae + '.worldMatrix', pUnite + '.inputMat[0]')
		cmds.connectAttr(animShpae + '.worldMesh', pUnite + '.inputPoly[0]')
		cmds.connectAttr(pUnite + '.output', vesShape + '.inMesh')

	return ves_grp


def mSmoothMesh(ves_grp):
	"""
	"""
	for ves in cmds.listRelatives(ves_grp, c= 1):
		cmds.polySmooth(ves, mth= 0, sdt= 2, ovb= 1, ofb= 3, ofc= 0, ost= 1,
								ocr= 0, dv= 1, bnr= 1 ,c= 1, kb= 1, ksb= 1,
								khe= 0, kt= 1, kmb= 1, suv= 1, peh= 0, sl= 1,
								dpe= 1, ps= 0.1, ro= 1, ch= 0)


def mSaveTransformName(ves_grp, transFile):
	"""
	"""
	with open(transFile, 'w') as transTxt:
		for ves in cmds.listRelatives(ves_grp, c= 1):
			transTxt.write(_chopNS(ves) + '\n')


def mXMLMeshList(xmlFile, assetNS):
	"""
	"""
	# meshes need to process
	anim_meshes = []

	Channels = minidom.parse(xmlFile).getElementsByTagName('Channels')[0]
	for ChannelName in Channels.childNodes:
		if ChannelName.nodeType == ChannelName.ELEMENT_NODE:
			meshName = assetNS + ':' + _chopNS(ChannelName.getAttribute('ChannelName'))
			anim_meshes.append(meshName)

	return anim_meshes


def mTXTTransList(transFile, rootNode):
	"""
	"""
	# transform nodes need to select
	anim_trans = []
	target_trans = cmds.listRelatives(rootNode, ad= 1, f= 1, typ= 'transform')

	transTxt = open(transFile, 'r')
	for trans in transTxt:
		for target in target_trans:
			if target.endswith(trans.strip()) and not 'LP_geo_grp' in target:
				anim_trans.append(target)
				break

	return list(set(anim_trans))



def mImportViskey(keyFile, assetNS, viskeyNS, workingNS):
	"""
	"""
	viskeyNS = assetNS + viskeyNS
	cmds.file(keyFile, i= 1, typ= 'mayaAscii', iv= 1, ra= 1, ns= viskeyNS)
	visAniNodeList = cmds.namespaceInfo(viskeyNS + workingNS, lod= 1)
	for visAniNode in visAniNodeList:
		visAniMesh = assetNS + ':' + visAniNode.split(viskeyNS + workingNS)[1]
		try:
			cmds.connectAttr(visAniNode + '.output', visAniMesh + '.visibility')
		except:
			print 'viskey import Faild:  ' + visAniNode


def mCleanWorkingNS(workingNS):
	"""
	"""
	mGeneral.namespaceDel(workingNS)


def mSetupWorkingNS(workingNS):
	"""
	"""
	mGeneral.namespaceSet(workingNS)