# -*- coding:utf-8 -*-
'''
Created on 2016.05.10

@author: davidpower
'''
import os
import maya.cmds as cmds
import maya.mel as mel
import mMaya.mGeneral as mGeneral; reload(mGeneral)


class SceneInfo(object):

	def __init__(self):

		''' os '''
		self.sep = self.pathSep()

		''' maya basic '''
		# project root
		self.workspaceRoot = cmds.workspace(q= 1, rd= 1)
		# project folder path dict
		self.dirRule = self.getDirRules()
		# scene full path
		self.sceneFullPath = mGeneral.sceneName(shn= 0, ext= 1)
		# scene name with ext
		self.sceneFullName = mGeneral.sceneName(ext= 1)
		# scene name without ext
		self.sceneSplitExt = mGeneral.sceneName()

		''' scene data '''
		# project abbreviation
		self.prjAbbr = ''
		# scene file version
		self.ver = ''
		# the one who last saved this scene
		self.artist = ''
		# cut list
		self.cutId = []
		# camera list
		self.cam = []
		# palybackRange
		self.palybackStart = cmds.playbackOptions(q= 1, min= 1)
		self.palybackEnd = cmds.playbackOptions(q= 1, max= 1)
		# frameRate
		self.fps = mel.eval('currentTimeUnitToFPS')
		self.timeUnit = cmds.currentUnit(q= 1, t= 1)



	def getDirRules(self):
		"""
		"""
		ruleDict = {}
		for rule in cmds.workspace(q= 1, frl= 1):
			ruleDict[rule] = cmds.workspace(rule, q= 1, fre= 1)

		return ruleDict


	def pathSep(self):
		"""
		path separator 待跨平台測試
		"""
		sep = os.altsep
		
		return sep


	def makeDir(self, filePath, isFile= None):
		"""
		create folder if not exists
		"""
		if isFile is not None:
			filePath = os.path.dirname(filePath)

		if not os.path.exists(filePath):
			os.makedirs(filePath)
