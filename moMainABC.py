# -*- coding:utf-8 -*-
'''
Created on 2016.05.18

@author: davidpower
'''
import maya.standalone as standalone
standalone.initialize()

import maya.cmds as cmds
import maya.mel as mel

import os
import logging

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  
logLevel = logging.DEBUG

logger = logging.getLogger('MayaOil')
ch = logging.StreamHandler()

logger.setLevel(logLevel)
ch.setLevel(logLevel)
ch.setFormatter(formatter)





charInd = 0
override = 0



charName = ['assassin', 'BOSS', ''][charInd]

maFileList = {
			  #'c06/' + charName + '_c06_geoCache_v01.ma':'c06/' + charName + '_c06_geoCache.abc',
			  #'c07/' + charName + '_c07_geoCache_v01.ma':'c07/' + charName + '_c07_geoCache.abc'
			  
			  #'c08/' + charName + '_c08_geoCache_v01.ma':'c08/' + charName + '_c08_geoCache.abc',
			  #'c09/' + charName + '_c09_geoCache_v01.ma':'c09/' + charName + '_c09_geoCache.abc',
			  #'c10/' + charName + '_c10_geoCache_v01.ma':'c10/' + charName + '_c10_geoCache.abc'
			  
			  'c12/' + charName + '_c12_geoCache_v01.ma':'c12/' + charName + '_c12_geoCache.abc',
			  'c14/' + charName + '_c14_geoCache_v01.ma':'c14/' + charName + '_c14_geoCache.abc',
			  'c15/' + charName + '_c15_geoCache_v01.ma':'c15/' + charName + '_c15_geoCache.abc'
			  }



logger.info('start')

projPath = 'O:/201603_SongOfKnights/Maya'
mel.eval('setProject \"' + projPath + '\"')


for maFile in maFileList.keys():

	cmds.file(new= 1, f= 1)
	cmds.file('O:/201603_SongOfKnights/Maya/scenes/geoCache/' + maFile, o= 1, lar= 1, f= 1)
	cmds.playbackOptions(min= 101)

	if not cmds.pluginInfo('AbcExport', q= 1, l= 1):
		cmds.loadPlugin('AbcExport')

	targetList = cmds.ls('*:geo_grp', r= 1)
	if targetList:
		cmds.select(targetList, r= 1)
		logger.info('[' + os.path.basename(maFile) + '] Export Start.')
		# export abc
		frameRange = '%d %d' % (cmds.playbackOptions(q= 1, min= 1), cmds.playbackOptions(q= 1, max= 1))
		root = cmds.ls(sl= 1, l= 1)[0]
		abcPath = 'O:/201603_SongOfKnights/Maya/cache/alembic/0614/' + maFileList[maFile]
		doExport = 1
		if cmds.file(abcPath, q= 1, ex= 1) and not override:
			doExport = 0

		if doExport:
			if not cmds.file(os.path.dirname(abcPath), q= 1, ex= 1):
				os.mkdir(os.path.dirname(abcPath))
			mel.eval('AbcExport -j "-frameRange ' + frameRange + ' -ro -stripNamespaces -uvWrite -worldSpace -writeVisibility -dataFormat hdf -root ' + root + ' -file ' + abcPath + '";')
	else:
		logger.info('[' + os.path.basename(maFile) + '] Nothing to Export.')
		continue

	logger.info('[' + os.path.basename(maFile) + '] Export Done.')


logger.info('quit')
cmds.quit(force= True)