# -*- coding:utf-8 -*-
'''
Created on 2016.06.16

@author: davidpower
'''

from pymel.core import *
from datetime import *
from functools import partial
from maya.OpenMayaUI import MQtUtil
from shiboken import wrapInstance
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
import tempfile
import logging
import json
import os
import moCache.moGeoCache as moGeoCache; reload(moGeoCache)
import moCam.moCam as moCam; reload(moCam)

logger = logging.getLogger('MayaOil.moGeocache.UI')

tempLog = tempfile.gettempdir() + '\\moGeoCacheUserHistory.json'
jsonFile = workspace(q= 1, rd= 1) + 'mo_geoCacheLog.json'






def rgb_hex(rgb, downGrade= None):
	def _hex(num):
		if num < 16:
			return '0' + hex(num)[2:]
		else:
			return hex(num)[2:]
	r, g, b = rgb
	if downGrade:
		r = (r - downGrade) if downGrade < r else 0
		g = (g - downGrade) if downGrade < g else 0
		b = (b - downGrade) if downGrade < b else 0
	return ('#' + _hex(r) + _hex(g) + _hex(b)).upper()


def rgb_nor(rgb, downGrade= None):
	r, g, b = rgb
	if downGrade:
		r = (r - downGrade) if downGrade < r else 0
		g = (g - downGrade) if downGrade < g else 0
		b = (b - downGrade) if downGrade < b else 0
	return [r/255.0, g/255.0, b/255.0]


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


def renewUI(*args):

	ui_geoCacheIO()


def readJSON():

	if not os.path.isfile(jsonFile):
		with open(jsonFile, 'w') as json_file:
			json.dump({}, json_file)

	with open(jsonFile) as json_file:

		return json.load(json_file)


def updateJSON(shotNum, assetList, subTyp, filePath= None):

	snameObj = system.sceneName()
	filePath = str(snameObj) if not filePath else (filePath + ';' + str(snameObj.namebase))
	cDate = str(datetime.now())
	gcLog = readJSON()

	if not gcLog.has_key(shotNum):
		gcLog[shotNum] = {}
	
	for ast in assetList:
		if not ast in gcLog[shotNum].keys():
			gcLog[shotNum][ast] = {subTyp:{}}
		if not subTyp in gcLog[shotNum][ast].keys():
			gcLog[shotNum][ast][subTyp] = {}
		gcLog[shotNum][ast][subTyp][cDate] = filePath

	with open(jsonFile, 'w') as json_file:
		json.dump(gcLog, json_file, indent=4)


def setUserHistory(userHistory):

	with open(tempLog, 'w') as tempLogJson:
		json.dump(userHistory, tempLogJson, indent=4)


def getUserHistory():
	
	userHistory = {}
	workRoot = workspace(q= 1, rd= 1)

	if not os.path.isfile(tempLog):
		userHistory[workRoot] = str(datetime.now()).split(' ')[0] + ' 00:00:00.000000'
		
		with open(tempLog, 'w') as tempLogJson:
			json.dump(userHistory, tempLogJson, indent=4)
	else:
		with open(tempLog) as tempLogJson:
			userHistory = json.load(tempLogJson)
		if not userHistory.has_key(workRoot):
			userHistory[workRoot] = str(datetime.now()).split(' ')[0] + ' 00:00:00.000000'

	return userHistory


def getVerSN(filename):

	txList = filename.split('_')
	txList.reverse()
	for tx in txList:
		if tx.startswith('v') and tx[1].isdigit():
			return tx[1:]
	return ''


def shortDateFormat(latestDate):

	return '' \
		+ latestDate.split('.')[0].split(' ')[0][5:].replace('-', '/') \
		+ '  ' \
		+ latestDate.split('.')[0].split(' ')[1][:-3]


def submitANI(*args):

	assetName_override = str(textField('textF_assetName', q= 1, tx= 1))

	sname = system.sceneName().namebase
	if sname:
		shotNum = moCam.getShotNum(sname)
		assetList = moGeoCache.getAssetList() if not assetName_override else [assetName_override]

		if assetList and shotNum:
			updateJSON(shotNum, assetList, 'ANI')
			renewUI()


def submitGEO(*args):

	subdivLevel = intFieldGrp('intF_sdLevel', q= 1, v1= 1)
	isPartial = checkBox('cBox_isPartial', q= 1, v= 1)
	assetName_override = str(textField('textF_assetName', q= 1, tx= 1))
	sceneName_override = str(textField('textF_sceneName', q= 1, tx= 1))

	sname = system.sceneName().namebase
	if sname:
		shotNum = moCam.getShotNum(sname)
		assetList = moGeoCache.getAssetList() if not assetName_override else [assetName_override]
		moGeoCache.exportGeoCache(
			subdivLevel = subdivLevel if subdivLevel else None,
			isPartial = isPartial if isPartial else None,
			assetName_override = assetName_override if assetName_override else None,
			sceneName_override = sceneName_override if sceneName_override else None
			)

		if assetList and shotNum:
			updateJSON(shotNum, assetList, 'GEO')
			renewUI()


def submitCAM(*args):

	assetName_override = str(textField('textF_assetName', q= 1, tx= 1))

	sname = system.sceneName().namebase
	if sname:
		print 'hi'
		camera = [dag for dag in ls(sl= 1) if dag.getShape() and dag.getShape().type() == 'camera']
		print camera
		assets = [dag for dag in ls(sl= 1) if not (dag.getShape() and dag.getShape().type() == 'camera')]
		print assets
		shotNum = moCam.getShotNum(sname)
		select(assets, r= 1)
		assetList = moGeoCache.getAssetList() if not assetName_override else [assetName_override]
		select(camera, r= 1)
		filePath = moCam.exportCam()
		if assetList and shotNum and filePath:
			updateJSON(shotNum, assetList, 'CAM', filePath)
			renewUI()


def btncmd_ANI(filePath, *args):

	try:
		system.openFile(filePath)
	except:
		decision = confirmDialog(
			t= 'Wanring',
			m= 'Unsaved changes.\nContinue open?',
			b= ['Yes', 'No'],
			db= 'Yes',
			cb= 'No',
			ds= 'No',
			icn= 'warning'
			)
		if decision == 'Yes':
			system.openFile(filePath, f= 1)


def btncmd_GEO(sceneName, *args):
	
	isPartial = checkBox('cBox_isPartial', q= 1, v= 1)
	ignorDuplicateName = checkBox('cBox_ignorDupl', q= 1, v= 1)
	assetName_override = str(textField('textF_assetName', q= 1, tx= 1))
	sceneName_override = str(textField('textF_sceneName', q= 1, tx= 1))
	conflictList = str(textField('textF_filter', q= 1, tx= 1))

	moGeoCache.importGeoCache(
		sceneName if not sceneName_override else sceneName_override,
		isPartial = isPartial if isPartial else None,
		assetName_override = assetName_override if assetName_override else None,
		ignorDuplicateName = ignorDuplicateName if ignorDuplicateName else None,
		conflictList = conflictList if conflictList else None
		)


def btncmd_CAM(shotNum, *args):
	
	moCam.referenceCam(shotNum)


def intcmd_setMinMax(*args):
	intvalue = intFieldGrp('intF_sdLevel', q= 1, v1= 1)
	if intvalue < 0:
		intFieldGrp('intF_sdLevel', e= 1, v1= 0)
	if intvalue > 4:
		intFieldGrp('intF_sdLevel', e= 1, v1= 4)


def ui_geoCacheIO():# border: 1px solid FireBrick; border-radius: 2px;

	userHistory = getUserHistory()
	
	windowName = 'mo_geoCacheIO'
	shotPadding = 2

	workRoot = workspace(q= 1, rd= 1)

	color1 = [125, 130, 90]
	color2 = [95, 140, 150]
	colorM = [100, 130, 70]
	colorN = [50, 120, 140]

	if dockControl(windowName, q= 1, ex= 1):
		deleteUI(windowName)

	main_ui = window()
	main_ly = scrollLayout(p= main_ui)
	dockControl(windowName, area= 'right', content= main_ui, allowedArea= ['right', 'left'], vis= 1, s= 0, w= 370)

	columnLayout(adj= 1, rs= 5, p= main_ly)
	text(l= u'好好幹活兒!', al= 'left')
	text(l= '')

	pulltext = text(l= 'PUSH  `submit / output', al= 'left', h= 28)
	dp_makePySideUI(pulltext, 'QObject {font: bold 30px; font-family: Arial;}')

	separator()
	ctrBaseColor = [.65, .48, .32]
	ctrSubsColor = [.68, .52, .38]

	columnLayout(adj= 1, bgc= ctrBaseColor)
	columnLayout(adj= 1)
	rowLayout(nc= 7)
	text(l= 'Common: ', w= 55, al= 'right')
	text(l= '')
	text(l= 'Partial GEO ', al= 'right', w= 70)
	checkBox('cBox_isPartial', l= '', w= 13)
	dp_makePySideUI('cBox_isPartial', 'QObject {background-color: #63524C;}')
	text(l= '')
	text('  *Override ', en= 0)
	textField('textF_assetName', pht= 'assetName', w= 125)
	dp_makePySideUI('textF_assetName', 'QObject {background-color: #63524C; border-radius: 2px;}')
	setParent('..')

	rowLayout(nc= 7)
	text(l= 'Export: ', w= 55, al= 'right')
	text(l= '')
	text(l= 'Add Division ', al= 'right', w= 70)
	intFieldGrp('intF_sdLevel', l= '', v1= 0, ad2= 1, cw= [2, 14], w= 19, cc= intcmd_setMinMax)
	dp_makePySideUI('intF_sdLevel', 'QObject {background-color: #63524C; border-radius: 2px;}')
	text(l= '')
	text('*Override ', en= 0)
	textField('textF_sceneName', pht= 'sceneName', w= 125)
	dp_makePySideUI('textF_sceneName', 'QObject {background-color: #63524C; border-radius: 2px;}')
	setParent('..')

	rowLayout(nc= 7)
	text(l= 'Import: ', w= 55, al= 'right')
	text(l= '')
	text(l= 'Same Name ', al= 'right', w= 70)
	checkBox('cBox_ignorDupl', l= '', w= 13)
	dp_makePySideUI('cBox_ignorDupl', 'QObject {background-color: #63524C;}')
	text(l= '')
	text('  *Filter       ', en= 0)
	textField('textF_filter', pht= 'string1;string2...', w= 125)
	dp_makePySideUI('textF_filter', 'QObject {background-color: #63524C; border-radius: 2px;}')
	setParent('..')
	setParent('..')

	rowLayout(nc= 4, adj= 1)
	btnPushName = windowName + '_button_' + 'submit'
	button(btnPushName + 'ANI', l= 'ANI', h= 44, w= 100, bgc= ctrSubsColor, c= submitANI)
	button(btnPushName + 'GEO', l= 'GEO', h= 44, w= 100, bgc= ctrBaseColor, c= submitGEO)
	button(btnPushName + 'CAM', l= 'CAM', h= 44, w= 100, bgc= ctrSubsColor, c= submitCAM)
	button(btnPushName + 'REF', l= 'O', h= 44, w= 30, bgc= [.4, .6, .5], c= renewUI)
	dp_makePySideUI(btnPushName + 'ANI', 'QPushButton {font: 28px Courier; color: #714125;}')
	dp_makePySideUI(btnPushName + 'GEO', 'QPushButton {font: 28px Courier; color: #714125;}')
	dp_makePySideUI(btnPushName + 'CAM', 'QPushButton {font: 28px Courier; color: #714125;}')
	dp_makePySideUI(btnPushName + 'REF', 'QPushButton {font: 28px Courier; color: #448553;}')
	setParent('..')
	setParent('..')
	
	separator()
	text(l= '')

	pulltext = text(l= 'PULL  `open / input', al= 'left', h= 28)
	dp_makePySideUI(pulltext, 'QObject {font: bold 30px; font-family: Arial;}')

	gcLog = readJSON()
	shotList = gcLog.keys()
	shotList.sort()

	for shot in shotList:
		# vars
		assetList = gcLog[shot].keys()
		assetList.sort()
		shotNum = shot[:shotPadding]

		# shot frameLayout
		shotFrameName = windowName + '_frameLY_' + shot
		BGcolor = rgb_nor(color1) if int(shotNum) % 2 else rgb_nor(color2)
		frameLayout(shotFrameName, l= 'shot ' + shot, cll= 1, bgc= BGcolor)
		dg = 10
		BGcolor = rgb_hex(color1, dg) if int(shotNum) % 2 else rgb_hex(color2, dg)
		dp_makePySideUI(shotFrameName, 'QWidget {color: #303030; background-color: %s}' % BGcolor)

		# shot ui parent formLayout
		formName = windowName + '_formLY_' + shot
		formLayout(formName)

		titleName = windowName + '_shotTitle_' + shot
		text(titleName, l= shotNum, al= 'right')
		titleColor = '6B6F4E' if int(shotNum) % 2 else '4E757E'
		dp_makePySideUI(titleName, 'QObject {font: bold 100px Arial; color: #' + titleColor + ';}')
		
		columName = windowName + '_shotColumn_' + shot
		columnLayout(columName, adj= 1)

		for num, asset in enumerate(assetList):
			filePath_ANI = ''
			fileName_ANI = ''
			sceneName_ANI = ''
			filePath_GEO = ''
			fileName_GEO = ''
			sceneName_GEO = ''
			geoCacheDir = ''
			filePath_CAM = ''
			fileName_CAM = ''
			sceneName_CAM = ''

			subTypDateDict = {'ANI':'', 'GEO':'', 'CAM':''}
			for typ in subTypDateDict.keys():
				if gcLog[shot][asset].has_key(typ):
					dateList = gcLog[shot][asset][typ].keys()
					dateList.sort()
					subTypDateDict[typ] = dateList[-1]
			
			if subTypDateDict['ANI']:
				filePath_ANI = gcLog[shot][asset]['ANI'][subTypDateDict['ANI']]
				fileName_ANI = os.path.basename(filePath_ANI)
				sceneName_ANI = os.path.splitext(fileName_ANI)[0]
			if subTypDateDict['GEO']:
				filePath_GEO = gcLog[shot][asset]['GEO'][subTypDateDict['GEO']]
				fileName_GEO = os.path.basename(filePath_GEO)
				sceneName_GEO = os.path.splitext(fileName_GEO)[0]
				geoCacheDir = moGeoCache.getGeoCacheDir(asset, sceneName_GEO)
			if subTypDateDict['CAM']:
				mixPath_CAM = gcLog[shot][asset]['CAM'][subTypDateDict['CAM']]
				filePath_CAM = mixPath_CAM.split(';')[0]
				fileName_CAM = os.path.basename(filePath_CAM)
				sceneName_CAM = mixPath_CAM.split(';')[1]

			dg2 = 0 if num % 2 else 0
			colorK = colorM if int(shotNum) % 2 else colorN
			BGcolor = rgb_nor(colorK, dg2)
			frameLayout(shotFrameName + asset, l= asset, cll= 0, bgc= BGcolor)
			columnLayout(adj= 1)

			rowLayout(nc= 3, adj= 1)
			dateShortANI = shortDateFormat(subTypDateDict['ANI']) if subTypDateDict['ANI'] else ''
			dateShortGEO = shortDateFormat(subTypDateDict['GEO']) if subTypDateDict['GEO'] else ''
			dateShortCAM = shortDateFormat(subTypDateDict['CAM']) if subTypDateDict['CAM'] else ''
			txtA = windowName + '_text_' + shot + asset + 'ANI'
			txtB = windowName + '_text_' + shot + asset + 'GEO'
			txtC = windowName + '_text_' + shot + asset + 'CAM'
			text(txtA, l= dateShortANI, al= 'center', w= 75)
			text(txtB, l= dateShortGEO, al= 'center', w= 75)
			text(txtC, l= dateShortCAM, al= 'center', w= 75)
			setParent('..')
			
			rowLayout(nc= 3, adj= 1)
			colorA = [120, 170, 140] if int(shotNum) % 2 else [130, 150, 170]
			colorB = [145, 150, 120] if int(shotNum) % 2 else [130, 130, 150]
			colorC = [160, 150, 130] if int(shotNum) % 2 else [130, 120, 140]
			btnA = windowName + '_button_' + shot + asset + 'ANI'
			btnB = windowName + '_button_' + shot + asset + 'GEO'
			btnC = windowName + '_button_' + shot + asset + 'CAM'

			btnAN = 'ANI' if not 'layout' in sceneName_ANI else 'LAY'
			button(btnA, l= btnAN, w= 75, h= 25, ann= fileName_ANI, c= partial(btncmd_ANI, filePath_ANI))
			button(btnB, l= 'GEO', w= 75, h= 25, ann= fileName_GEO, c= partial(btncmd_GEO, sceneName_GEO))
			button(btnC, l= 'CAM', w= 75, h= 25, ann= fileName_CAM, c= partial(btncmd_CAM, shotNum))
			dp_makePySideUI(btnA, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, dg2)))
			dp_makePySideUI(btnB, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, dg2)))
			dp_makePySideUI(btnC, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, dg2)))
			setParent('..')
			
			setParent('..')
			setParent('..')

			# check animation
			if not os.path.exists(filePath_ANI):
				button(btnA, e= 1, en= 0)
				dp_makePySideUI(btnA, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, 50)))
			else:
				ver = getVerSN(sceneName_ANI)
				button(btnA, e= 1, l= btnAN + '_' + ver)
			# check geoCache
			if not os.path.exists(geoCacheDir):
				button(btnB, e= 1, en= 0)
				dp_makePySideUI(btnB, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, 50)))
			else:
				ver = getVerSN(sceneName_GEO)
				button(btnB, e= 1, l= 'GEO_' + ver)
			# check camera
			if not os.path.exists(filePath_CAM):
				button(btnC, e= 1, en= 0)
				dp_makePySideUI(btnC, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, 50)))
			else:
				ver = getVerSN(sceneName_CAM)
				button(btnC, e= 1, l= 'CAM_' + ver)

			# check update
			if subTypDateDict['ANI'] >= userHistory[workRoot]:
				dp_makePySideUI(txtA, 'QObject {font: bold; color: #E3C55E}')
				dp_makePySideUI(btnA, 'QPushButton {background-color: #E3C55E}')
			if subTypDateDict['GEO'] >= userHistory[workRoot]:
				dp_makePySideUI(txtB, 'QObject {font: bold; color: #E3C55E}')
				dp_makePySideUI(btnB, 'QPushButton {background-color: #E3C55E}')
			if subTypDateDict['CAM'] >= userHistory[workRoot]:
				dp_makePySideUI(txtC, 'QObject {font: bold; color: #E3C55E}')
				dp_makePySideUI(btnC, 'QPushButton {background-color: #E3C55E}')


		formLayout(formName, e= 1, af=[(titleName, 'left', -20), (titleName, 'top', -25)])
		formLayout(formName, e= 1, af=[(columName, 'right', 0), (columName, 'top', 0)])

		setParent('..')
		setParent('..')
		setParent('..')


	separator()
	setParent('..')

	logger.info('Last Time Logged in: ' + userHistory[workRoot])
	userHistory[workRoot] = str(datetime.now())
	setUserHistory(userHistory)


if __name__ == '__main__':
	ui_geoCacheIO()