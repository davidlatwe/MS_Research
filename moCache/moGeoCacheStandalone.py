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


logger.info('start')

projPath = 'O:/201603_SongOfKnights/Maya'
mel.eval('setProject \"' + projPath + '\"')


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
	geoCacheDir = moRules.rGeoCacheDir(charName, cacheName)
	if not cmds.file(geoCacheDir, q= 1, ex= 1):
		logger.info('[' + os.path.basename(maFile) + '] Nothing to Import.')
		continue
	refFile = 'O:/201603_SongOfKnights/Maya/assets/char/' + charFile + '.ma'
	cmds.file(refFile, r= 1, type= 'mayaAscii', iv= 1, gl= 1, lrd= 'all', shd= 'renderLayersByName', mnc= 0, ns= charFile, op= 'v=0;')
	cmds.select(cmds.ls(charName + '*:geo_grp', r= 1), r= 1)
	logger.info('[' + os.path.basename(maFileList[maFile]) + '] Import Start.')
	moGeoCache.importGeoCache(cacheName, assetName= charName)

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




# C:\Program Files\Autodesk\Maya2016\bin\mayapy.exe" "O:\201603_SongOfKnights\Maya\scripts\moMain.py