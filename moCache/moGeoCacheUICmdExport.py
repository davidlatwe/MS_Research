# -*- coding:utf-8 -*-
'''
Created on 2016.05.18

@author: davidpower
'''
from inspect import getsourcefile
import os, sys
import logging

logging.basicConfig(
	level=logging.DEBUG,
	format='%(asctime)s - %(levelname)s - %(message)s'
	)
logger = logging.getLogger(__name__)



def _processEndMsg(fileName, msg):
	"""
	"""
	print '\n' * 20
	print './' * 20
	print '\.' * 20
	print '  ' * 20
	print '[' + fileName + '] ' + msg
	print '  ' * 20
	print './' * 20
	print '\.' * 20


def _checkParam(paramDict):
	"""
	"""
	paramList = [
		'assetName',
		'sceneName',
		'isPartial',
		 'isStatic',
		   'subdiv',
		 'sameName',
		 'conflict'
	]

	for param in paramList:
		print param.rjust(10) + ' : ' + str(paramDict[param])


def _checkSelection():
	"""
	"""
	for dag in ls(sl= 1):
		print dag


def main(projPath, filePath, assetList, paramDict):
	"""
	"""
	# get moudel, add parent-parent directory
	# some say the __file__ attribute is not allways given...
	'''
	parentdir = os.path.dirname(os.path.dirname(__file__))
	sys.path.insert(0, parentdir)
	'''	
	current_dir = os.path.dirname(os.path.abspath(getsourcefile(lambda:0)))
	sys.path.insert(0, current_dir[:current_dir.rfind(os.path.sep)])
	import moCache.moGeoCache as moGeoCache

	mel.eval('setProject \"' + projPath + '\"')
	openFile(filePath, loadReferenceDepth= 'all', force= True)
	fileName = system.sceneName().namebase
	select(assetList, r= 1)
	logger.debug(_checkSelection())

	mel.eval('source cleanUpScene;')
	mel.eval('putenv "MAYA_TESTING_CLEANUP" "1";')
	mel.eval('scOpt_saveAndClearOptionVars(1);')
	mel.eval('scOpt_setOptionVars( {"unknownNodesOption"} );')
	mel.eval('cleanUpScene( 1 );')
	mel.eval('scOpt_saveAndClearOptionVars(0);')
	mel.eval('putenv "MAYA_TESTING_CLEANUP" "";')
	
	moGeoCache.exportGeoCache(
		subdivLevel= paramDict['subdiv'],
		isPartial= paramDict['isPartial'],
		isStatic= paramDict['isStatic'],
		assetName_override= paramDict['assetName'],
		sceneName_override= paramDict['sceneName']
		)
	
	_processEndMsg(fileName, 'Export Done.')
	newFile(force= True)
	cmds.quit(force= True)


if __name__ == '__main__':
	projPath = sys.argv[1]
	filePath = sys.argv[2]
	assetList = eval(sys.argv[3])
	paramDict = eval(sys.argv[4])
	logger.debug(projPath)
	logger.debug(filePath)
	logger.debug(assetList)
	logger.debug(_checkParam(paramDict))
	logger.info(__file__ + '  [START]')
	if assetList and os.path.isfile(filePath):
		import maya.standalone as standalone
		standalone.initialize()
		from pymel.core import *
		import maya.cmds as cmds
		main(projPath, filePath, assetList, paramDict)
	elif os.path.isfile(filePath):
		fileName = os.path.splitext(os.path.basename(filePath))
		_processEndMsg(fileName, 'Nothing to Export.')
	else:
		_processEndMsg('None', 'File not exists.')
		logger.debug(filePath)
	
	logger.info(__file__ + '  [END]')
	raw_input()
