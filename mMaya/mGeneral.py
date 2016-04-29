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