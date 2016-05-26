# -*- coding:utf-8 -*-
'''
Created on 2016.05.18

@author: davidpower
'''
import maya.standalone as standalone
standalone.initialize()

import maya.cmds as cmds
import maya.mel as mel
import moCache.moGeoCache as moGeoCache

import os
import logging

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  
logLevel = logging.DEBUG

logger = logging.getLogger('MayaOil')
ch = logging.StreamHandler()

logger.setLevel(logLevel)
ch.setLevel(logLevel)
ch.setFormatter(formatter)







exportGeo = 0
importGeo = 1

smooth = 1

charName = ['assassin', 'BOSS', ''][0]


logger.info('start')

projPath = 'O:/201603_SongOfKnights/Maya'
mel.eval('setProject \"' + projPath + '\"')


maFileList = {#'c01/SOK_c01_anim_v02.ma':'c01/' + charName + '_c01_geoCache_v01.ma'
			  #'c02/SOK_c02_c03_anim_v02.ma':'c02/' + charName + '_c02_geoCache_v01.ma'
			  'c04/SOK_c04_anim_v02.ma':'c04/' + charName + '_c04_geoCache_v01.ma'
			  #'c05/SOK_c05_anim_v01.ma':'c05/' + charName + '_c05_geoCache_v01.ma'
			  #'c06/SOK_c06_anim_v02.ma':'c06/' + charName + '_c06_geoCache_v01.ma'
			  #'c07/SOK_c07_anim_v04.ma':'c07/' + charName + '_c07_geoCache_v01.ma'
			  #'c08/SOK_c08_anim_v03.ma':'c08/' + charName + '_c08_geoCache_v01.ma'
			  #'c09/SOK_c09_anim_v01.ma':'c09/' + charName + '_c09_geoCache_v01.ma'
			  #'c10/SOK_c10_anim_v01.ma':'c10/' + charName + '_c10_geoCache_v01.ma'
			  #'c12/SOK_c12_anim_v02.ma':'c12/' + charName + '_c12_geoCache_v01.ma'
			  #'c14/SOK_c14_anim_v04.ma':'c14/' + charName + '_c14_geoCache_v01.ma'
			  #'c15/SOK_c15_anim_v05.ma':'c15/' + charName + '_c15_geoCache_v01.ma'
			  }


charFile = ''
if charName == 'assassin':
	charFile = charName + '_shdaing_master'
else:
	charFile = charName + '_shading_master'


for maFile in maFileList.keys():

	if exportGeo:
		cmds.file(new= 1, f= 1)
		cmds.file('O:/201603_SongOfKnights/Maya/scenes/anim/' + maFile, o= 1, lar= 1, f= 1)
		cmds.playbackOptions(min= 1)
		targetList = cmds.ls(charName + '*:geo_grp', r= 1)
		if targetList:
			cmds.select(targetList, r= 1)
			logger.info('[' + os.path.basename(maFile) + '] Export Start.')
			moGeoCache.exportGeoCache(smooth)
		else:
			logger.info('[' + os.path.basename(maFile) + '] Nothing to Export.')
			continue

		logger.info('[' + os.path.basename(maFile) + '] Export Done.')
	
	if importGeo:
		cmds.file(new= 1, f= 1)
		cacheName = maFile.split('/')[1].split('.')[0]
		refFile = 'O:/201603_SongOfKnights/Maya/assets/char/' + charFile + '.ma'
		cmds.file(refFile, r= 1, type= 'mayaAscii', iv= 1, gl= 1, lrd= 'all', shd= 'renderLayersByName', mnc= 0, ns= charFile, op= 'v=0;')
		cmds.select(cmds.ls(charName + '*:geo_grp', r= 1), r= 1)
		logger.info('[' + os.path.basename(maFileList[maFile]) + '] Import Start.')
		moGeoCache.importGeoCache(cacheName)

		mel.eval('source cleanUpScene;')
		mel.eval('putenv "MAYA_TESTING_CLEANUP" "1";')
		mel.eval('scOpt_saveAndClearOptionVars(1);')
		mel.eval('scOpt_setOptionVars( {"unknownNodesOption"} );')
		mel.eval('cleanUpScene( 1 );')
		mel.eval('scOpt_saveAndClearOptionVars(0);')
		mel.eval('putenv "MAYA_TESTING_CLEANUP" "";')

		cmds.file(rename= 'O:/201603_SongOfKnights/Maya/scenes/geoCache/' + maFileList[maFile])
		cmds.file(s= 1, type='mayaAscii')
		logger.info('[' + os.path.basename(maFileList[maFile]) + '] Import Done.')


logger.info('quit')
cmds.quit(force= True)