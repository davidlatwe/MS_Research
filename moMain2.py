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
import moCache.moGeoCacheRules as moRules

import os
import logging

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  
logLevel = logging.DEBUG

logger = logging.getLogger('MayaOil')
ch = logging.StreamHandler()

logger.setLevel(logLevel)
ch.setLevel(logLevel)
ch.setFormatter(formatter)

'''
exportGeo = 0
importGeo = 1
smooth = 1
projPath = 'O:/201603_SongOfKnights/Maya'

maFileList = {'c01/SOK_c01_anim_v02.ma':'c01/' + charName + '_c01_geoCache_v01.ma'
			  'c02/SOK_c02_c03_anim_v03.ma':'c02/' + charName + '_c02_geoCache_v01.ma',
			  'c04/SOK_c04_anim_v03.ma':'c04/' + charName + '_c04_geoCache_v01.ma',
			  'c05/SOK_c05_anim_v01.ma':'c05/' + charName + '_c05_geoCache_v01.ma',
			  'c06/SOK_c06_anim_v03.ma':'c06/' + charName + '_c06_geoCache_v01.ma',
			  'c07/SOK_c07_anim_v04.ma':'c07/' + charName + '_c07_geoCache_v01.ma',
			  'c08/SOK_c08_anim_v03.ma':'c08/' + charName + '_c08_geoCache_v01.ma',
			  'c09/SOK_c09_anim_v01.ma':'c09/' + charName + '_c09_geoCache_v01.ma',
			  'c10/SOK_c10_anim_v01.ma':'c10/' + charName + '_c10_geoCache_v01.ma',
			  'c12/SOK_c12_anim_v02.ma':'c12/' + charName + '_c12_geoCache_v01.ma',
			  'c14/SOK_c14_anim_v04.ma':'c14/' + charName + '_c14_geoCache_v01.ma',
			  'c15/SOK_c15_anim_v05.ma':'c15/' + charName + '_c15_geoCache_v01.ma'
			  }

'''

def mayaStandaloneGeoCache(exportPath, importPath, smooth, projPath, exMin, exMax, imMin, imMax, isPartial= None, assetName= None, sceneName= None):

	#charInd = 0
	#charName = ['assassin', 'BOSS', ''][charInd]

	logger.info('start')

	
	mel.eval('setProject \"' + projPath + '\"')

	#charFile = ''
	#if charName == 'assassin':
	#	charFile = charName + '_shdaing_master'
	#else:
	#	charFile = charName + '_shading_master'

	for maFile in maFileList.keys():

		if exportPath:
			cmds.file(new= 1, f= 1)
			cmds.file(exportPath, o= 1, lar= 1, f= 1)
			cmds.playbackOptions(min= 1)
			
			targetList = cmds.ls(charName + '*:geo_grp', r= 1)
			if targetList:
				cmds.select(targetList, r= 1)
				logger.info('[' + os.path.basename(exportPath) + '] Export Start.')

				moGeoCache.exportGeoCache(smooth, isPartial= None, assetName= None, sceneName= None)

			else:
				logger.info('[' + os.path.basename(exportPath) + '] Nothing to Export.')
				continue

			logger.info('[' + os.path.basename(exportPath) + '] Export Done.')
		

		if importPath:
			cmds.file(new= 1, f= 1)
			cacheName = importPath.split('/')[1].split('.')[0]
			geoCacheDir = moRules.rGeoCacheDir(charName, cacheName)
			if not cmds.file(geoCacheDir, q= 1, ex= 1):
				logger.info('[' + os.path.basename(importPath) + '] Nothing to Import.')
				continue
			refFile = 'O:/201603_SongOfKnights/Maya/assets/char/' + charFile + '.ma'
			cmds.file(refFile, r= 1, type= 'mayaAscii', iv= 1, gl= 1, lrd= 'all', shd= 'renderLayersByName', mnc= 0, ns= charFile, op= 'v=0;')
			cmds.select(cmds.ls(charName + '*:geo_grp', r= 1), r= 1)
			logger.info('[' + os.path.basename(importPath) + '] Import Start.')
			
			moGeoCache.importGeoCache(cacheName, isPartial= None, assetName= None)

			mel.eval('source cleanUpScene;')
			mel.eval('putenv "MAYA_TESTING_CLEANUP" "1";')
			mel.eval('scOpt_saveAndClearOptionVars(1);')
			mel.eval('scOpt_setOptionVars( {"unknownNodesOption"} );')
			mel.eval('cleanUpScene( 1 );')
			mel.eval('scOpt_saveAndClearOptionVars(0);')
			mel.eval('putenv "MAYA_TESTING_CLEANUP" "";')

			cmds.file(rename= importPath)
			cmds.file(s= 1, type='mayaAscii')
			logger.info('[' + os.path.basename(importPath) + '] Import Done.')


	logger.info('quit')
	cmds.quit(force= True)


if __name__ = '__main__':
	mayaStandaloneGeoCache()



'''
import sys

def printVar(sysVar1, sysVar2):
	print sysVar1
	print sysVar2


printVar(sys.argv[1], sys.argv[2])
'''