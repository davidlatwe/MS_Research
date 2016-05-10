# -*- coding:utf-8 -*-
'''
Created on 2016.05.10

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
import os
import sys
sys.path.insert(0, 'C:/Users/David/Documents/GitHub/MS_MayaOil')
import mMaya.mGeneral as mgnr


class SceneKeeper(object):

	def __init__(self):

		''' maya basic '''
		# project root
		self.wksRoot = cmds.workspace(q= 1, rd= 1)
		# scene full path
		self.scenLon = mgnr.sceneName(shn= 0, ext= 1)
		# scene name with ext
		self.scenExt = mgnr.sceneName(ext= 1)
		# scene name without ext
		self.scenSht = mgnr.sceneName()

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