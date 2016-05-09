# -*- coding:utf-8 -*-
'''
Created on 2016.04.29

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
import functools
import logging

logging.basicConfig(level=logging.WARNING)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def workspaceRoot():
	"""
	"""
	return cmds.workspace(q= 1, rd= 1)


def sceneName(shn= None, ext= None):
	"""
	"""
	shn = True if shn is None or shn else False

	if not untitled():
		# scene is not untitled, do things
		sceneName = cmds.file(q= 1, exn = 1)
		
		# shn
		if shn:
			# return short scene name
			sceneName = os.path.basename(sceneName)
		
		# ext
		if ext == '':
			# return without ext
			sceneName = '.'.join(sceneName.split('.')[:-1])
		if ext == 'ma' or (ext == 'cn' and sceneName.endswith('.mb')):
			# return mayaAscii file name
			sceneName = '.'.join(sceneName.split('.')[:-1]) + '.ma'
		if ext == 'mb' or (ext == 'cn' and sceneName.endswith('.ma')):
			# return mayaBinary file name
			sceneName = '.'.join(sceneName.split('.')[:-1]) + '.mb'

		return sceneName

	else:
		pass


def untitled():
	"""
	"""
	if cmds.file(q= 1, exn = 1).endswith('untitled'):
		return True
	else:
		return False


def namespaceDel(name):
	"""
	"""
	for ns in cmds.namespaceInfo(lon= 1, r= 1, an= 1):
		if name in ns:
			cmds.namespace(rm = ns, dnc = 1)


def namespaceSet(name):
	"""
	"""
	if not cmds.namespace(ex = name):
		cmds.namespace(add = name)
	cmds.namespace(set = name)


if __name__ == '__main__':
	pass