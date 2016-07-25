"""
Copy all texture file in current scene to one folder.

@author: David


import sys
toolPath = '//storage-server/LaiTaWei/script/MS_MayaOil'
if not toolPath in sys.path:
	sys.path.insert(0, toolPath)
import moTools.exportAllTexture as exportAllTexture; reload(exportAllTexture)
exportAllTexture.ui_main()
"""

from pymel.core import *
from pymel.util import *
from subprocess import Popen
import os



def pathReDir(fnp):
	"""
	if texture path is not vaild
	"""
	fnp = os.path.normpath(fnp)
	ori = os.path.normpath('O:/')
	fix = os.path.normpath('//backup-server/StorageProduct/Project/')
	fnp = fnp.replace(ori, fix + '\\')

	return fnp


def copyAll(*args):
	"""
	"""
	global textFieldName

	dirPath = textField(textFieldName, q= 1, tx= 1)
	if not os.path.exists(dirPath):
		os.makedirs(dirPath)
	if os.path.exists(dirPath):
		print dirPath
		for fnp in [fnode.fileTextureName.get() for fnode in ls(type= 'file')]:
			fnp = pathReDir(fnp)
			print fnp
			path(fnp).copy(dirPath)
		Popen(['explorer', os.path.abspath(dirPath)])


def ui_main():
	"""
	"""
	global textFieldName

	windowName = 'exportAllTexture_mainUI'

	if window(windowName, q= 1, ex= 1):
		deleteUI(windowName)
	
	window(windowName, t= 'Export all texture', w= 400)
	columnLayout(adj= 1)
	text(l= 'All texture copy to ...', al= 'left')
	rowLayout(nc= 2, adj= 1)
	textFieldName = textField(pht= 'paste your folder path')
	itb_openDir = iconTextButton(i= 'fileOpen.png', w= 20, h= 20)
	setParent('..')
	button(l= 'Do Copy', c= copyAll)
	setParent('..')

	def ui_openDir(*args):
		result = fileDialog2(cap= 'Dist Folder', fm= 3, okc= 'Select')
		if result:
			textField(textFieldName, e= 1, tx= result[0])

	iconTextButton(itb_openDir, e= 1, c= ui_openDir)

	showWindow(windowName)
