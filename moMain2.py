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
reload(moGeoCache)

import logging
logger = logging.getLogger('MayaOil')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  
ch.setFormatter(formatter)


logger.info('start')

projPath = 'O:/201603_SongOfKnights/Maya'
mel.eval('setProject \"' + projPath + '\"')


exportGeo = 0
importGeo = 1

maFileList = {#'c01/SOK_c01_anim_v02.ma':'c01/BOSS_c01_geoCache_v01.ma',
			  'c02/SOK_c02_c03_anim_v02.ma':'c02/BOSS_c02_geoCache_v01.ma',
			  #'c04/SOK_c04_anim_v02.ma':'c04/BOSS_c04_geoCache_v01.ma',
			  #'c05/SOK_c05_anim_v01.ma':'c05/BOSS_c05_geoCache_v01.ma',
			  #'c06/SOK_c06_anim_v02.ma':'c06/BOSS_c06_geoCache_v01.ma',
			  'c07/SOK_c07_anim_v02.ma':'c07/BOSS_c07_geoCache_v01.ma',
			  'c08/SOK_c08_anim_v02.ma':'c08/BOSS_c08_geoCache_v01.ma',
			  'c09/SOK_c09_anim_v01.ma':'c09/BOSS_c09_geoCache_v01.ma',
			  'c10/SOK_c10_anim_v01.ma':'c10/BOSS_c10_geoCache_v01.ma',
			  'c12/SOK_c12_anim_v01.ma':'c12/BOSS_c12_geoCache_v01.ma',
			  'c14/SOK_c14_anim_v04.ma':'c14/BOSS_c14_geoCache_v01.ma',
			  'c15/SOK_c15_anim_v03.ma':'c15/BOSS_c15_geoCache_v01.ma'
			  }



for maFile in maFileList.keys():

	if exportGeo:
		cmds.file('O:/201603_SongOfKnights/Maya/scenes/anim/' + maFile, o= 1, f= 1)
		targetList = cmds.ls('*BOSS', r= 1)
		if targetList:
			cmds.select(targetList, r= 1)
			logger.info('Export Start.')
			moGeoCache.exportGeoCache(1)
		else:
			logger.info('Nothing to Export.')
			continue

		logger.info('Export Done.')
	
	if importGeo:
		cacheName = maFile.split('/')[1].split('.')[0]
		cmds.file(new= 1, f= 1)
		refFile = 'O:/201603_SongOfKnights/Maya/assets/char/BOSS_shading_master.ma'
		cmds.file(refFile, r= 1, type= 'mayaAscii', iv= 1, gl= 1, lrd= 'all', shd= 'renderLayersByName', mnc= 0, ns= 'BOSS_shading_master', op= 'v=0;')
		cmds.select(cmds.ls('*geo_grp', r= 1), r= 1)
		logger.info('Import Start.')
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
		logger.info('Import Done.')


logger.info('quit')
cmds.quit(force= True)