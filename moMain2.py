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
import os

import moCache.moGeoCache as moGeoCache
reload(moGeoCache)

projPath = 'O:/201603_SongOfKnights/Maya'
mel.eval('setProject \"' + projPath + '\"')


maFileList = [#'c04/assassin_c04_geoCache_v01.ma',
			  #'c05/assassin_c05_geoCache_v01.ma',
			  #'c06/assassin_c06_geoCache_v01.ma',
			  #'c07/assassin_c07_geoCache_v01.ma',
			  #'c08/assassin_c08_geoCache_v01.ma',
			  #'c09/assassin_c09_geoCache_v01.ma',
			  #'c10/assassin_c10_geoCache_v01.ma',
			  'c12/assassin_c12_geoCache_v01.ma',
			  'c14/assassin_c14_geoCache_v01.ma',
			  'c15/assassin_c15_geoCache_v01.ma'
			  ]

cacheList = os.listdir('O:/201603_SongOfKnights/Maya/cache/moGeoCache')

for maFile in maFileList:

	cacheName = ''
	for cache in cacheList:
		if maFile.split('/')[0] == cache.split('_')[1] and cache != 'SOK_c14_anim_v03':
			cacheName = cache
			break
	if cacheName:
		cmds.file('O:/201603_SongOfKnights/Maya/scenes/geoCache/' + maFile, o= 1, f= 1)

		cmds.select('assassin_shdaing_master:geo_grp')

		moGeoCache.importGeoCache(cacheName)

		cmds.file(s= 1)