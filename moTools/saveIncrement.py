# -*- coding:utf-8 -*-
'''
Created on 2016.06.17

@author: davidpower

'''

# Increment Save File

from pymel.core import *
import os


def _getIncrement(filename):

	txList = filename.split('_')
	txList.reverse()
	for tx in txList:
		if tx.startswith('v') and tx[1].isdigit():
			return filename.replace(tx, 'v' + str(int(tx[1:]) + 1))

def mo_saveIncrement():

	currentPath = system.sceneName()
	currentName = currentPath.namebase
	incrementName = _getIncrement(currentName)
	incrementPath = currentPath.replace(currentName, incrementName)
	incrementDir = os.path.dirname(incrementPath)

	if not os.path.exists(incrementDir):
		os.makedirs(incrementDir)

	system.saveAs(incrementPath)


if __name__ == '__main__':
	mo_saveIncrement()
	