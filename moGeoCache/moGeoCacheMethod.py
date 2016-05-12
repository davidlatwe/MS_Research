# -*- coding:utf-8 -*-
'''
Created on 2016.05.12

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
import mMaya.mOutliner as mOutliner


def exportList():
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


def filterOut(rootNode):
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