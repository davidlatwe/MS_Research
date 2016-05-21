# -*- coding:utf-8 -*-
'''
Created on 2016.05.18

@author: davidpower
'''
import logging
logger = logging.getLogger('MayaOil')
logger.setLevel(logging.WARNING)

logger.info('start')

import maya.standalone as standalone
standalone.initialize()

import maya.cmds as cmds
import maya.mel as mel

import moCache.moGeoCache as moGeoCache
reload(moGeoCache)

projPath = 'O:/201603_SongOfKnights/Maya'
mel.eval('setProject \"' + projPath + '\"')


maFileList = ['c01/SOK_c01_anim_v02.ma',
			  'c04/SOK_c04_anim_v02.ma',
			  'c05/SOK_c05_anim_v01.ma',
			  'c06/SOK_c06_anim_v02.ma',
			  #'c07/SOK_c07_anim_v02.ma',
			  'c08/SOK_c08_anim_v02.ma',
			  #'c09/SOK_c09_anim_v01.ma',
			  'c10/SOK_c10_anim_v01.ma',
			  #'c12/SOK_c12_anim_v01.ma',
			  'c14/SOK_c14_anim_v04.ma',
			  'c15/SOK_c15_anim_v03.ma'
			  ]

for maFile in maFileList:

	cmds.file('O:/201603_SongOfKnights/Maya/scenes/anim/' + maFile, o= 1, f= 1)

	cmds.select('*:assassin_master_grp')
	moGeoCache.exportGeoCache(1)
	#moGeoCache.importGeoCache('SOK_c01_anim_v01')