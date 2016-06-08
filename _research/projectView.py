import json
from pymel.core import *

from functools import partial
from maya.OpenMayaUI import MQtUtil
from shiboken import wrapInstance
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore


def dp_makePySideUI(ctrlName, myStyle):

	# thanks to Nathan Horne
	ctrlName = long(MQtUtil.findControl(ctrlName))
	qObj = wrapInstance(ctrlName, QtCore.QObject)
	metaObj = qObj.metaObject()
	cls = metaObj.className()
	superCls = metaObj.superClass().className()

	if hasattr(QtGui, cls):
		base = getattr(QtGui, cls)
	elif hasattr(QtGui, superCls):
		base = getattr(QtGui, superCls)
	else:
		base = QtGui.QWidget

	uiPySide = wrapInstance(ctrlName, base)
	uiPySide.setStyleSheet(myStyle)



def autoFrameLayout(data, box):
	def func(key, box):
		d = ''
		item = ['ASSETS', 'SHOTS', 'char', 'prop', 'set', 'fx']
		tmpKey = key[1:-1] if key[0].isdigit() else key[:-1]
		lenNote = '(' + str(len(data[key].keys())) + ')' if tmpKey in item else ''
		num = len(box.split('|')) - 4
		if key.endswith('+'):
			item = ['ASSETS', 'SHOTS']
			frameLayout('frame_' + tmpKey, l= tmpKey + lenNote, bgc= [num * 0.12, 0.32, 0.34], cll= 0 if tmpKey in item else 1, cl= 1, bv= 0, p= box)
			d = columnLayout('column_' + tmpKey, adj= 1)
		else:
			button('button_' + tmpKey, l= tmpKey, bgc= [0.48, 0.38, 0.32], c= partial(objDataframe, ['MOD', 'RIG', 'SHD'], tmpKey), p= box)
		
		return d
	
	if type(data) is dict:
		dataList = data.keys()
		dataList.sort()
		for key in dataList:
			d = func(key, box)
			if d:
				autoFrameLayout(data[key], d)



def objDataframe(objType, asName, *args):
	global flowList
	#formLayout(objType, h= 200)
	uiList = layout(flowList, q= 1, ca= 1)
	if uiList:
		for ui in uiList:
			deleteUI(ui)
	for typ in objType:
		formLayout('form_' + typ, h= 120, p= flowList)

		text('objTitle_' + typ, l= typ)
		dp_makePySideUI('objTitle_' + typ, 'QObject {font: bold 24px; font-family: Arial;}')# color: Salmon; 

		button('fileMaster_' + typ, l= asName + '_' + typ + '_v01.ma')
		text('filePath_' + typ, l= 'O:/20160607_HaHa/Maya/Scene/' + typ)
		text('fileAuthor_' + typ, l= 'David')
		text('fileDate_' + typ, l= '2016.06.07 18:32:45')

		formLayout('form_' + typ, e= 1, af=[('objTitle_' + typ, 'left', 5), ('objTitle_' + typ, 'top', 5)])
		formLayout('form_' + typ, e= 1, af=[('fileMaster_' + typ, 'left', 100), ('fileMaster_' + typ, 'right', 10), ('fileMaster_' + typ, 'top', 9)])
		formLayout('form_' + typ, e= 1, af=[('filePath_' + typ, 'left', 10), ('filePath_' + typ, 'top', 50)])
		formLayout('form_' + typ, e= 1, af=[('fileAuthor_' + typ, 'left', 10), ('fileAuthor_' + typ, 'top', 70)])
		formLayout('form_' + typ, e= 1, af=[('fileDate_' + typ, 'left', 10), ('fileDate_' + typ, 'top', 90)])







jsonFile = 'C:/Users/David/Documents/GitHub/MS_MayaOil/projStructTest.json'

with open(jsonFile) as json_file:
    proj = json.load(json_file)

windowName = 'testWindow'

if window(windowName, q= 1, ex= 1):
	deleteUI(windowName)

window(windowName, s= 1)
pane = cmds.paneLayout(cn= 'vertical2', swp= 1, ps= [1, 25, 0])

#--------------
# Left pane
global projTree
projTree = scrollLayout(vst= 5, hst= 5, cr= 1, p= pane)
# Right pane
global flowList
flowList = scrollLayout(vst= 5, hst= 5, cr= 1, p= pane)
#--------------

autoFrameLayout(proj, columnLayout(adj= 1, p= projTree))

window(windowName, e= 1, w= 600, h= 300)
showWindow(windowName)

