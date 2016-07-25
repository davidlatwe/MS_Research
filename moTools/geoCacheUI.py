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
import ctypes
import json
import os
import moCache.moGeoCache as moGeoCache; reload(moGeoCache)
import moSceneInfo; reload(moSceneInfo)
import moCam.moCam as moCam; reload(moCam)

logger = logging.getLogger('MayaOil.moGeocache.UI')



def _getSceneInfo():
	"""
	"""
	return moSceneInfo.SceneInfo()


def getJSONFile():

	return workspace(q= 1, rd= 1) + 'mo_geoCacheLog.json'


def getTempLog():

	return tempfile.gettempdir() + '\\moGeoCacheUserHistory.json'


def getProjList():

	return tempfile.gettempdir() + '\\myFavoriteProjList.txt'


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


def hex_rgb(strHex):

	if strHex.startswith('#'):
		strHex = strHex[1:]
	r = int(strHex[0:2], 16)
	g = int(strHex[2:4], 16)
	b = int(strHex[4:6], 16)

	return [r, g, b]


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

	return uiPySide


def renewUI(*args):

	ui_geoCacheIO()


def dataStruct_proj():

	return {
		'asset':{},
		'shots':{}
	}


def dataStruct_asset():

	return {
		'MOD':{"MST": {}, "WIP": {}},
		'SHD':{"MST": {}, "WIP": {}},
		'RIG':{"MST": {}, "WIP": {}}
	}


def dataStruct_shots():

	return {
		'INF':{'fps':0.0, 'min':0, 'max':0},
		'ANI':{},
		'GEO':{},
		'CAM':{}
	}


def readJSON():

	jsonFile = getJSONFile()

	if not os.path.isfile(jsonFile):
		with open(jsonFile, 'w') as json_file:
			json.dump(dataStruct_proj(), json_file)
	try:
		with open(jsonFile) as json_file:

			return json.load(json_file)
	except:

		return {}


def updateJSON(subTyp, shotNum= None, assetList= None, filePath= None):

	jsonFile = getJSONFile()
	snameObj = system.sceneName()
	filePath = str(snameObj) if not filePath else filePath
	cDate = str(datetime.now())

	# read
	gcLog = readJSON()
	goUpdate = True


	# update shots
	if shotNum and not gcLog['shots'].has_key(shotNum):
		gcLog['shots'][shotNum] = dataStruct_shots()
	
	if shotNum and assetList and subTyp in ['GEO']:
		for ast in assetList:
			if not ast in gcLog['shots'][shotNum][subTyp].keys():
				gcLog['shots'][shotNum][subTyp][ast] = {}
			gcLog['shots'][shotNum][subTyp][ast][cDate] = filePath

	if shotNum and subTyp in ['ANI', 'CAM']:
		if subTyp == 'CAM':
			filePath = filePath + ';' + str(snameObj.namebase)
		gcLog['shots'][shotNum][subTyp][cDate] = filePath

		if subTyp == 'ANI' and assetList:
			for ast in assetList:
				if not ast in gcLog['shots'][shotNum]['GEO'].keys():
					gcLog['shots'][shotNum]['GEO'][ast] = {}
					if ast in gcLog['asset'].keys():
						logger.info('[ANI] assigned with [' + ast + ']')
					else:
						logger.warning('[ANI] assigned with [%s], but this asset is not registered.' % ast)

	if shotNum and subTyp in ['ANI', 'CAM', 'GEO']:
		sInfo = _getSceneInfo()
		gcLog['shots'][shotNum]['INF']['fps'] = sInfo.fps
		gcLog['shots'][shotNum]['INF']['min'] = sInfo.palybackStart
		gcLog['shots'][shotNum]['INF']['max'] = sInfo.palybackEnd


	# update asset
	if assetList and subTyp in ['MOD', 'SHD', 'RIG']:
		if filePath:
			for ast in assetList:
				if not ast in gcLog['asset'].keys():
					gcLog['asset'][ast] = dataStruct_asset()
				if 'master' in str(snameObj.namebase):
					gcLog['asset'][ast][subTyp]['MST'][cDate] = filePath
				else:
					gcLog['asset'][ast][subTyp]['RIG'][cDate] = filePath
		else:
			goUpdate = False
			logger.warning('[%s] can\'t submit, due to filePath is incorrect. -> %s' % filePath)


	# remove shot
	if shotNum and subTyp == 'dSh':
		if not gcLog['shots'].pop(shotNum, False):
			logger.debug('KeyError, Might removed by someone else.')


	# remove asset in shot
	if shotNum and assetList and subTyp == 'dAs':
		if not gcLog['shots'][shotNum]['GEO'].pop(assetList[0], False):
			logger.debug('KeyError, Might removed by someone else.')

	# write
	if goUpdate:
		with open(jsonFile, 'w') as json_file:
			json.dump(gcLog, json_file, indent=4)
		renewUI()


def setUserHistory(userHistory):

	tempLog = getTempLog()

	with open(tempLog, 'w') as tempLogJson:
		json.dump(userHistory, tempLogJson, indent=4)


def getUserHistory():
	
	tempLog = getTempLog()
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


def shortDateFormat(latestDate):

	return '' \
		+ latestDate.split('.')[0].split(' ')[0][5:].replace('-', '/') \
		+ '  ' \
		+ latestDate.split('.')[0].split(' ')[1][:-3]


def fileLocationCheck():

	filePath = system.sceneName()
	if ':' in filePath:
		drive = filePath.split(':')[0]
		driveType = ctypes.windll.kernel32.GetDriveTypeW(u'%s:' % drive)
		if driveType == 4:

			return True

	driveTypes = ['DRIVE_UNKNOWN', 'DRIVE_NO_ROOT_DIR', 'DRIVE_REMOVABLE', 'DRIVE_FIXED', 'DRIVE_REMOTE', 'DRIVE_CDROM', 'DRIVE_RAMDISK']
	logger.warning('Expecting [DRIVE_REMOTE] path, instead [%s]. -> %s' % (driveTypes[driveType], filePath))
	confirmDialog(
		t= u'動作中止',
		m= u'目前場景檔案並非儲存於網路硬碟。\n'
			+ u'為確保其他專案成員皆可存取，'
			+ u'請另存至網路硬碟後再行提交。',
		b= ['Ok'],
		db= 'Ok',
		icn= 'warning'
		)
	
	return False


def submitMOD(*args):

	if fileLocationCheck():
		assetName_override = str(textField('textF_assetName', q= 1, tx= 1))
		sname = system.sceneName().namebase
		if sname:
			assetList = [sname.split('_')[0]] if not assetName_override else [assetName_override]
			if assetList:
				updateJSON('MOD', assetList= assetList)
			else:
				logger.warning('[MOD] submit faild.')


def submitSHD(*args):

	if fileLocationCheck():
		assetName_override = str(textField('textF_assetName', q= 1, tx= 1))
		sname = system.sceneName().namebase
		if sname:
			assetList = [sname.split('_')[0]] if not assetName_override else [assetName_override]
			if assetList:
				updateJSON('SHD', assetList= assetList)
			else:
				logger.warning('[SHD] submit faild.')


def submitRIG(*args):

	if fileLocationCheck():
		assetName_override = str(textField('textF_assetName', q= 1, tx= 1))
		sname = system.sceneName().namebase
		if sname:
			assetList = [sname.split('_')[0]] if not assetName_override else [assetName_override]
			if assetList:
				updateJSON('RIG', assetList= assetList)
			else:
				logger.warning('[RIG] submit faild.')


def submitANI(*args):

	if fileLocationCheck():
		assetName_override = str(textField('textF_assetName', q= 1, tx= 1))
		sInfo = _getSceneInfo()
		sname = system.sceneName().namebase
		if sname:
			shotNum = sInfo.shotNum
			assetList = moGeoCache.getAssetList() if not assetName_override else [assetName_override]
			if shotNum:
				updateJSON('ANI', shotNum, assetList)
			else:
				logger.warning('[ANI] submit faild.')


def submitGEO(*args):

	if fileLocationCheck():
		subdivLevel = intFieldGrp('intF_sdLevel', q= 1, v1= 1)
		isPartial = checkBox('cBox_isPartial', q= 1, v= 1)
		assetName_override = str(textField('textF_assetName', q= 1, tx= 1))
		sceneName_override = str(textField('textF_sceneName', q= 1, tx= 1))
		sInfo = _getSceneInfo()
		sname = system.sceneName().namebase
		if sname:
			shotNum = sInfo.shotNum
			assetList = moGeoCache.getAssetList() if not assetName_override else [assetName_override]
			moGeoCache.exportGeoCache(
				subdivLevel = subdivLevel if subdivLevel else None,
				isPartial = isPartial if isPartial else None,
				assetName_override = assetName_override if assetName_override else None,
				sceneName_override = sceneName_override if sceneName_override else None
				)

			if assetList and shotNum:
				updateJSON('GEO', shotNum, assetList)
			else:
				logger.warning('[GEO] submit faild.')


def submitCAM(*args):

	if fileLocationCheck():
		assetName_override = str(textField('textF_assetName', q= 1, tx= 1))
		sInfo = _getSceneInfo()
		sname = system.sceneName().namebase
		if sname:
			shotNum = sInfo.shotNum
			camera = [dag for dag in ls(sl= 1) if dag.getShape() and dag.getShape().type() == 'camera']
			if camera:
				select(camera, r= 1)
				filePath = moCam.exportCam()
				if shotNum and filePath:
					updateJSON('CAM', shotNum, filePath= filePath)
			else:
				logger.warning('[CAM] submit faild.')


def btncmd_ANI(filePath, *args):

	if filePath:
		try:
			system.openFile(filePath)
		except:
			decision = confirmDialog(
				t= u'警告',
				m= u'目前場景有未儲存的變更\n要忽略嗎 ?\n繼續開啟檔案請按 [Yes]',
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
	conflictList = [] if not conflictList else conflictList.split(';')
	
	moGeoCache.importGeoCache(
		sceneName if not sceneName_override else sceneName_override,
		isPartial = isPartial if isPartial else None,
		assetName_override = assetName_override if assetName_override else None,
		ignorDuplicateName = ignorDuplicateName if ignorDuplicateName else None,
		conflictList = conflictList if conflictList else None
		)


def btncmd_CAM(shotNum, *args):
	
	moCam.referenceCam(shotNum)


def btncmd_AST(filePath, *args):

	if filePath:
		system.createReference(filePath, namespace= '')
		'''
		try:
			system.openFile(filePath)
		except:
			decision = confirmDialog(
				t= u'警告',
				m= u'目前場景有未儲存的變更\n要忽略嗎 ?\n繼續開啟檔案請按 [Yes]',
				b= ['Yes', 'No'],
				db= 'Yes',
				cb= 'No',
				ds= 'No',
				icn= 'warning'
				)
			if decision == 'Yes':
				system.openFile(filePath, f= 1)
		'''


def btncmd_SHD(filePath, *args):

	if filePath:
		system.createReference(filePath, namespace= '')


def btncmd_RIG(filePath, *args):

	if filePath:
		system.createReference(filePath, namespace= '')


def btncmd_delShot(shotNum, *args):

	decision = confirmDialog(
		t= u'警告',
		m= u'此動作無法復原\n你確定要刪除第 %s 卡的 Log ?' % shotNum,
		b= ['Yes', 'No'],
		db= 'Yes',
		cb= 'No',
		ds= 'No',
		icn= 'warning'
		)
	if decision == 'Yes':
		updateJSON('dSh', shotNum)
		

def btncmd_delAsset(shotNum, asset, *args):

	decision = confirmDialog(
		t= u'警告',
		m= u'此動作無法復原\n你確定要刪除第 %s 卡 - %s 的 Log ?' % (shotNum, asset),
		b= ['Yes', 'No'],
		db= 'Yes',
		cb= 'No',
		ds= 'No',
		icn= 'warning'
		)
	if decision == 'Yes':
		updateJSON('dAs', shotNum, [asset])


def intcmd_setMinMax(*args):
	intvalue = intFieldGrp('intF_sdLevel', q= 1, v1= 1)
	if intvalue < 0:
		intFieldGrp('intF_sdLevel', e= 1, v1= 0)
	if intvalue > 4:
		intFieldGrp('intF_sdLevel', e= 1, v1= 4)


def btncmd_cancleSetProj(*args):

	deleteUI('mo_setProject', lay= True)
	renewUI()


def btncmd_setProject(projPath, *args):

	mel.eval('setProject \"' + projPath + '\"')
	btncmd_cancleSetProj()


def btncmd_addProject(*args):

	projListTxt = getProjList()
	projPath = textField('mo_addProj', q= 1, tx= 1).replace('\\', '/')
	
	if projPath:
		if not os.path.isfile(projListTxt):
			with open(projListTxt, 'w') as projList:
				projList.write(projPath)
		else:
			double = False
			with open(projListTxt, 'r') as projList:
				for line in projList:
					if line.strip() == projPath:
						double = True
						break
			if not double:
				with open(projListTxt, 'a') as projList:
					projList.write('\n' + projPath)

		ui_setProject()


def btncmd_delProject(pbtn, dbtn, *args):

	projListTxt = getProjList()
	projPath = button(pbtn, q= 1, ann= 1)
	newProjList = []

	if os.path.isfile(projListTxt):
		with open(projListTxt, 'r') as projList:
			for line in projList:
				if line.strip() != projPath:
					newProjList.append(line.strip())
		with open(projListTxt, 'w') as projList:
			projList.write('\n'.join(newProjList))

	deleteUI(pbtn)
	deleteUI(dbtn)


def mkProjListBtn(layout):

	sInfo = _getSceneInfo()
	projListTxt = getProjList()
	
	if os.path.isfile(projListTxt):
		projListSort = []
		with open(projListTxt, 'r') as projList:
			for line in projList:
				projListSort.append(line.strip())
		projListSort.sort()
		for proj in projListSort:
			if proj:
				rowLayout(nc= 2, adj= 1, p= layout)
				btnLabel = proj.split(sInfo.sep)[1]
				pbtn = button(l= btnLabel, ann= proj, c= partial(btncmd_setProject, proj.strip()), h= 40, w= 315)
				dp_makePySideUI(pbtn, 'QPushButton {font: 14px Courier;}')
				dbtn = button(l= ' x ', h= 40, w= 30, bgc= [.20, .20, .20])
				dp_makePySideUI(dbtn, 'QPushButton {font: 16px bold Arial; color: #8B3C3C;}')
				button(dbtn, e= 1, c= partial(btncmd_delProject, pbtn, dbtn))
				setParent('..')


def ui_setProject(*args):

	windowName = 'mo_setProject'

	if dockControl(windowName, q= 1, ex= 1):
		deleteUI(windowName, lay= True)

	main_window = window()
	main_ly = scrollLayout(p= main_window)
	dockControl(windowName, area= 'right', content= main_window, allowedArea= ['right', 'left'], vis= 1, s= 0, w= 370)
	
	columnLayout(adj= 1, rs= 5, p= main_ly)
	rowLayout(nc= 2, adj= 1)
	textField('mo_addProj', pht= 'O:/....', h= 23, w= 310)
	proj_add = button(l= ' ADD ', w= 40, h= 20, c= btncmd_addProject)
	dp_makePySideUI(proj_add, 'QPushButton {color: #76A87A;}')
	setParent('..')
	proj_cancle = button(l= ' Cancel ', w= 350, h= 30, bgc= [.20, .20, .20], c= btncmd_cancleSetProj)
	dp_makePySideUI(proj_cancle, 'QPushButton {font: 16px Courier; color: #8B3C3C;}')
	separator()

	projListColumn = columnLayout(adj= 1)
	mkProjListBtn(projListColumn)

	setParent('..')


def mkAssetListBtn(windowName, assetColumn):

	def expandCollapseFrames(btnExpCol, *args):
		if button(btnExpCol, q= 1, l= 1) == 'Expand All':
			cmd = 0
			button(btnExpCol, e= 1, l= 'Collapse All')
		else:
			cmd = 1
			button(btnExpCol, e= 1, l= 'Expand All')
		for ui in columnLayout(assetColumn, q= 1, ca= 1):
			if objectTypeUI(ui) == 'frameLayout':
				frameLayout(ui, e= 1, cl= cmd)
	text(l= '', h= 1)
	rowLayout(nc= 2, adj= 1)
	btnExpCol = button(l= 'Collapse All', w= 340)
	button(btnExpCol, e= 1, c= partial(expandCollapseFrames, btnExpCol))
	dp_makePySideUI(btnExpCol, 'QPushButton {color: #%s; background-color: #%s}' % ('598075', '454545'))
	setParent('..')

	sInfo = _getSceneInfo()
	userHistory = getUserHistory()
	workRoot = workspace(q= 1, rd= 1)

	frameBaseColor = hex_rgb('646464')

	gcLog = readJSON()
	assetList = gcLog['asset'].keys()
	assetList.sort()

	for asset in assetList:

		colorA = hex_rgb('505050')
		
		# asset frameLayout
		BGcolor = rgb_nor(frameBaseColor)
		assetFrameName = frameLayout(l= asset, fn= 'fixedWidthFont', cll= 1, bgc= BGcolor, w= 345)
		BGcolor = rgb_hex(frameBaseColor, 10)
		dp_makePySideUI(assetFrameName, 'QWidget {font: bold; color: #222222; background-color: %s}' % BGcolor)

		# asset ui parent formLayout
		formName = formLayout()

		# huge asset capital
		titleRow = rowLayout(nc= 2, adj= 1, rat= [2, 'bottom', 4])
		titleName1 = text(l= asset[0].title(), al= 'right')
		dp_makePySideUI(titleName1, 'QObject {font: Bold 70px Courier; color: #' + '252525' + ';}')
		titleName2 = text(l= asset[1].lower(), al= 'right')
		dp_makePySideUI(titleName2, 'QObject {font: Bold 55px Courier; color: #' + '252525' + ';}')
		setParent('..')

		# MODm info extract
		date_MODm = gcLog['asset'][asset]['MOD']['MST'].keys() if gcLog['asset'].has_key(asset) else []
		date_MODm.sort()
		dateShortMODm = shortDateFormat(date_MODm[-1]) if date_MODm and date_MODm[-1] else ''
		filePath_MODm = gcLog['asset'][asset]['MOD']['MST'][date_MODm[-1]] if dateShortMODm else ''
		fileName_MODm = os.path.basename(filePath_MODm) if dateShortMODm else ''
		sceneName_MODm = os.path.splitext(fileName_MODm)[0] if dateShortMODm else ''

		# MODw info extract
		date_MODw = gcLog['asset'][asset]['MOD']['WIP'].keys() if gcLog['asset'].has_key(asset) else []
		date_MODw.sort()
		dateShortMODw = shortDateFormat(date_MODw[-1]) if date_MODw and date_MODw[-1] else ''
		filePath_MODw = gcLog['asset'][asset]['MOD']['WIP'][date_MODw[-1]] if dateShortMODw else ''
		fileName_MODw = os.path.basename(filePath_MODw) if dateShortMODw else ''
		sceneName_MODw = os.path.splitext(fileName_MODw)[0] if dateShortMODw else ''

		# SHDm info extract
		date_SHDm = gcLog['asset'][asset]['SHD']['MST'].keys() if gcLog['asset'].has_key(asset) else []
		date_SHDm.sort()
		dateShortSHDm = shortDateFormat(date_SHDm[-1]) if date_SHDm and date_SHDm[-1] else ''
		filePath_SHDm = gcLog['asset'][asset]['SHD']['MST'][date_SHDm[-1]] if dateShortSHDm else ''
		fileName_SHDm = os.path.basename(filePath_SHDm) if dateShortSHDm else ''
		sceneName_SHDm = os.path.splitext(fileName_SHDm)[0] if dateShortSHDm else ''

		# SHDw info extract
		date_SHDw = gcLog['asset'][asset]['SHD']['WIP'].keys() if gcLog['asset'].has_key(asset) else []
		date_SHDw.sort()
		dateShortSHDw = shortDateFormat(date_SHDw[-1]) if date_SHDw and date_SHDw[-1] else ''
		filePath_SHDw = gcLog['asset'][asset]['SHD']['WIP'][date_SHDw[-1]] if dateShortSHDw else ''
		fileName_SHDw = os.path.basename(filePath_SHDw) if dateShortSHDw else ''
		sceneName_SHDw = os.path.splitext(fileName_SHDw)[0] if dateShortSHDw else ''

		# RIGm info extract
		date_RIGm = gcLog['asset'][asset]['RIG']['MST'].keys() if gcLog['asset'].has_key(asset) else []
		date_RIGm.sort()
		dateShortRIGm = shortDateFormat(date_RIGm[-1]) if date_RIGm and date_RIGm[-1] else ''
		filePath_RIGm = gcLog['asset'][asset]['RIG']['MST'][date_RIGm[-1]] if dateShortRIGm else ''
		fileName_RIGm = os.path.basename(filePath_RIGm) if dateShortRIGm else ''
		sceneName_RIGm = os.path.splitext(fileName_RIGm)[0] if dateShortRIGm else ''

		# RIGw info extract
		date_RIGw = gcLog['asset'][asset]['RIG']['WIP'].keys() if gcLog['asset'].has_key(asset) else []
		date_RIGw.sort()
		dateShortRIGw = shortDateFormat(date_RIGw[-1]) if date_RIGw and date_RIGw[-1] else ''
		filePath_RIGw = gcLog['asset'][asset]['RIG']['WIP'][date_RIGw[-1]] if dateShortRIGw else ''
		fileName_RIGw = os.path.basename(filePath_RIGw) if dateShortRIGw else ''
		sceneName_RIGw = os.path.splitext(fileName_RIGw)[0] if dateShortRIGw else ''

		columName = columnLayout(adj= 1)

		rowLayout(nc= 4, adj= 1)
		txt_MODm = text(l= dateShortMODm, al= 'center', w= 70)
		txt_SHDm = text(l= dateShortSHDm, al= 'center', w= 70)
		txt_RIGm = text(l= dateShortRIGm, al= 'center', w= 70)
		text(l= '', w= 3)
		setParent('..')
		
		rowLayout(nc= 4, adj= 1)
		btn_MODm = button(l= 'MOD', w= 70, h= 30, ann= fileName_MODm, c= partial(btncmd_AST, filePath_MODm))
		btn_SHDm = button(l= 'SHD', w= 70, h= 30, ann= fileName_SHDm, c= partial(btncmd_AST, filePath_SHDm))
		btn_RIGm = button(l= 'RIG', w= 70, h= 30, ann= fileName_RIGm, c= partial(btncmd_AST, filePath_RIGm))
		dp_makePySideUI(btn_SHDm, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, 0)))
		dp_makePySideUI(btn_RIGm, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, 0)))
		text(l= '', w= 3)
		setParent('..')

		rowLayout(nc= 4, adj= 1)
		txt_MODw = text(l= dateShortMODw, al= 'center', w= 70)
		txt_SHDw = text(l= dateShortSHDw, al= 'center', w= 70)
		txt_RIGw = text(l= dateShortRIGw, al= 'center', w= 70)
		text(l= '', w= 3)
		setParent('..')
		
		rowLayout(nc= 4, adj= 1)
		btn_MODw = button(l= 'MOD_wip', w= 70, h= 30, ann= fileName_MODw, c= partial(btncmd_AST, filePath_MODw))
		btn_SHDw = button(l= 'SHD_wip', w= 70, h= 30, ann= fileName_SHDw, c= partial(btncmd_AST, filePath_SHDw))
		btn_RIGw = button(l= 'RIG_wip', w= 70, h= 30, ann= fileName_RIGw, c= partial(btncmd_AST, filePath_RIGw))
		dp_makePySideUI(btn_SHDw, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, 0)))
		dp_makePySideUI(btn_RIGw, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, 0)))
		text(l= '', w= 3)
		setParent('..')

		text(l= '', h= 6)

		setParent('..')
		setParent('..')

		formLayout(formName, e= 1, af=[(titleRow, 'left', 0), (titleRow, 'top', -10)])
		formLayout(formName, e= 1, af=[(columName, 'right', 0), (columName, 'top', 0), (columName, 'left', 120)])
		setParent('..')

		colorHide = rgb_hex(colorA, -15)
		colorGray = rgb_hex(colorA, 0)
		# check MODm
		if not os.path.exists(filePath_MODm):
			button(btn_MODm, e= 1, en= 0)
			dp_makePySideUI(btn_MODm, 'QPushButton {color: %s; background-color: %s}' % (colorGray, colorHide))
		# check MODw
		if not os.path.exists(filePath_MODw):
			button(btn_MODw, e= 1, en= 0)
			dp_makePySideUI(btn_MODw, 'QPushButton {color: %s; background-color: %s}' % (colorGray, colorHide))
		else:
			ver = sInfo.getVerSN(sceneName_MODw)
			button(btn_MODw, e= 1, l= 'MOD' + (('_' + ver) if ver else ''))
		# check SHDm
		if not os.path.exists(filePath_SHDm):
			button(btn_SHDm, e= 1, en= 0)
			dp_makePySideUI(btn_SHDm, 'QPushButton {color: %s; background-color: %s}' % (colorGray, colorHide))
		# check SHDw
		if not os.path.exists(filePath_SHDw):
			button(btn_SHDw, e= 1, en= 0)
			dp_makePySideUI(btn_SHDw, 'QPushButton {color: %s; background-color: %s}' % (colorGray, colorHide))
		else:
			ver = sInfo.getVerSN(sceneName_SHDw)
			button(btn_SHDw, e= 1, l= 'SHD' + (('_' + ver) if ver else ''))
		# check RIGm
		if not os.path.exists(filePath_RIGm):
			button(btn_RIGm, e= 1, en= 0)
			dp_makePySideUI(btn_RIGm, 'QPushButton {color: %s; background-color: %s}' % (colorGray, colorHide))
		# check RIGw
		if not os.path.exists(filePath_RIGw):
			button(btn_RIGw, e= 1, en= 0)
			dp_makePySideUI(btn_RIGw, 'QPushButton {color: %s; background-color: %s}' % (colorGray, colorHide))
		else:
			ver = sInfo.getVerSN(sceneName_RIGw)
			button(btn_RIGw, e= 1, l= 'RIG' + (('_' + ver) if ver else ''))


		# check update
		if date_MODm and date_MODm[-1] >= userHistory[workRoot]:
			dp_makePySideUI(txt_MODm, 'QObject {font: bold; color: #E3C55E}')
			dp_makePySideUI(btn_MODm, 'QPushButton {background-color: #E3C55E}')
		if date_MODw and date_MODw[-1] >= userHistory[workRoot]:
			dp_makePySideUI(txt_MODw, 'QObject {font: bold; color: #E3C55E}')
			dp_makePySideUI(btn_MODw, 'QPushButton {background-color: #E3C55E}')
		if date_SHDm and date_SHDm[-1] >= userHistory[workRoot]:
			dp_makePySideUI(txt_SHDm, 'QObject {font: bold; color: #E3C55E}')
			dp_makePySideUI(btn_SHDm, 'QPushButton {background-color: #E3C55E}')
		if date_SHDw and date_SHDw[-1] >= userHistory[workRoot]:
			dp_makePySideUI(txt_SHDw, 'QObject {font: bold; color: #E3C55E}')
			dp_makePySideUI(btn_SHDw, 'QPushButton {background-color: #E3C55E}')
		if date_RIGm and date_RIGm[-1] >= userHistory[workRoot]:
			dp_makePySideUI(txt_RIGm, 'QObject {font: bold; color: #E3C55E}')
			dp_makePySideUI(btn_RIGm, 'QPushButton {background-color: #E3C55E}')
		if date_RIGw and date_RIGw[-1] >= userHistory[workRoot]:
			dp_makePySideUI(txt_RIGw, 'QObject {font: bold; color: #E3C55E}')
			dp_makePySideUI(btn_RIGw, 'QPushButton {background-color: #E3C55E}')


def mkShotListBtn(windowName, shotColumn):

	def expandCollapseFrames(btnExpCol, *args):
		if button(btnExpCol, q= 1, l= 1) == 'Expand All':
			cmd = 0
			button(btnExpCol, e= 1, l= 'Collapse All')
		else:
			cmd = 1
			button(btnExpCol, e= 1, l= 'Expand All')
		for ui in columnLayout(shotColumn, q= 1, ca= 1):
			if objectTypeUI(ui) == 'frameLayout':
				label = frameLayout(ui, q= 1, ann= 1)
				if not cmd:
					label = ' '.join(label.split(' ')[:2])
				frameLayout(ui, e= 1, cl= cmd, l= label)
	text(l= '', h= 1)
	rowLayout(nc= 2, adj= 1)
	btnExpCol = button(l= 'Expand All', w= 340)
	button(btnExpCol, e= 1, c= partial(expandCollapseFrames, btnExpCol))
	dp_makePySideUI(btnExpCol, 'QPushButton {color: #%s; background-color: #%s}' % ('758095', '454545'))
	setParent('..')

	sInfo = _getSceneInfo()
	userHistory = getUserHistory()
	workRoot = workspace(q= 1, rd= 1)

	shotPadding = 2
	frameBaseColor = hex_rgb('646464')

	gcLog = readJSON()
	shotList = gcLog['shots'].keys()
	shotList.sort()

	for shot in shotList:
		
		# shot info extract
		shotNum = shot[:shotPadding]
		s_fps = gcLog['shots'][shot]['INF']['fps']
		s_fps = str(int(s_fps) if s_fps.is_integer()  else s_fps)
		s_min = str(int(gcLog['shots'][shot]['INF']['min']))
		s_max = str(int(gcLog['shots'][shot]['INF']['max']))

		colorA = hex_rgb('505050')

		# shot frameLayout
		BGcolor = rgb_nor(frameBaseColor)
		s = 'shot ' + shot
		f = s_fps + ' fps'
		ccShotLable = s + ' '*(9-len(s)) + ' '*(4-len(s_fps)) + f + ' '*4 + s_min + ' - ' + s_max
		ecShotLable = s
		shotFrameName = frameLayout(l= ccShotLable, ann= ccShotLable,
			fn= 'fixedWidthFont', cll= 1, cl= 1, bgc= BGcolor, w= 345)
		frameLayout(shotFrameName, e= 1,
			cc= 'cmds.frameLayout("' + shotFrameName + '", e= 1, l= "' + ccShotLable + '")',
			ec= 'cmds.frameLayout("' + shotFrameName + '", e= 1, l= "shot ' + shot + '")')
		BGcolor = rgb_hex(frameBaseColor, 10)
		dp_makePySideUI(shotFrameName, 'QWidget {font: bold; color: #222222; background-color: %s}' % BGcolor)

		# shot ui parent formLayout
		formName = formLayout()

		# huge shot index
		titleName = text(l= shotNum, al= 'right')
		dp_makePySideUI(titleName, 'QObject {font: bold 100px Arial; color: #' + '252525' + ';}')
		# huge fps
		frameRate = formLayout()
		fpsText = text(l= s_fps, al= 'right')
		dp_makePySideUI(fpsText, 'QObject {font: bold 16px Arial; color: #' + '959595' + ';}')
		fpsUnit = text(l= 'FPS', al= 'left')
		dp_makePySideUI(fpsUnit, 'QObject {font: bold 10px Arial; color: #' + '959595' + ';}')
		setParent('..')
		formLayout(frameRate, e= 1, af=[(fpsText, 'left',   0), (fpsText, 'bottom', 0)])
		formLayout(frameRate, e= 1, af=[(fpsUnit, 'bottom', 3)])
		formLayout(frameRate, e= 1, ac=[(fpsUnit, 'left', 4, fpsText)])
		# huge frame range
		frameRang = text(l= s_min + ' - ' + s_max)
		dp_makePySideUI(frameRang, 'QObject {font: bold 11px Arial; color: #' + '959595' + ';}')
		
		
		columName = columnLayout(adj= 1, w= 120)

		# ANI info extract
		date_ANI = gcLog['shots'][shot]['ANI'].keys()
		date_ANI.sort()
		dateShortANI = shortDateFormat(date_ANI[-1]) if date_ANI and date_ANI[-1] else ''
		filePath_ANI = gcLog['shots'][shot]['ANI'][date_ANI[-1]] if dateShortANI else ''
		#author_ANI =
		#station_ANI =
		fileName_ANI = os.path.basename(filePath_ANI) if dateShortANI else ''
		sceneName_ANI = os.path.splitext(fileName_ANI)[0] if dateShortANI else ''

		# CAM info extract
		date_CAM = gcLog['shots'][shot]['CAM'].keys()
		date_CAM.sort()
		dateShortCAM = shortDateFormat(date_CAM[-1]) if date_CAM and date_CAM[-1] else ''
		mixPath_CAM = gcLog['shots'][shot]['CAM'][date_CAM[-1]] if dateShortCAM else ''
		filePath_CAM = mixPath_CAM.split(';')[0] if dateShortCAM else ''
		fileName_CAM = os.path.basename(filePath_CAM) if dateShortCAM else ''
		sceneName_CAM = mixPath_CAM.split(';')[1] if dateShortCAM else ''

		# shot buttons
		columnLayout(adj= 1)
		rowLayout(nc= 3, adj= 2)
		#text(l= '', h= 8, w= 85)
		ecAssetBtn = button(l= '+', h= 14, w= 14)
		dp_makePySideUI(ecAssetBtn, 
			'QPushButton {font: bold 14px Arial; background-color: #%s; color: #%s}' % ('5A5A5A', '222222'))
		text(l= '', h= 8, w= 136)
		delShotBtn = button(l= 'X', h= 14, w= 14, c= partial(btncmd_delShot, shotNum))
		dp_makePySideUI(delShotBtn, 'QPushButton {background-color: #%s; color: #%s}' % ('624249', '9F9F9F'))
		setParent('..')

		rowLayout(nc= 3, adj= 1)
		txt_ANI = windowName + '_text_' + shot + 'ANI'
		txt_CAM = windowName + '_text_' + shot + 'CAM'
		text(txt_ANI, l= dateShortANI, al= 'center', w= 98)
		text(txt_CAM, l= dateShortCAM, al= 'center', w= 97)
		text(l= '', w= 5)
		setParent('..')

		rowLayout(nc= 3, adj= 1)
		btn_ANI = windowName + '_button_' + shot + 'ANI'
		btn_ANI_label = 'ANI' if not 'layout' in sceneName_ANI else 'LAY'
		button(btn_ANI, l= btn_ANI_label, w= 98, h= 30, ann= fileName_ANI, c= partial(btncmd_ANI, filePath_ANI))

		btn_CAM = windowName + '_button_' + shot + 'CAM'
		button(btn_CAM, l= 'CAM', w= 97, h= 30, ann= fileName_CAM, c= partial(btncmd_CAM, shotNum))
		text(l= '', w= 5)
		setParent('..')
		setParent('..')

		dp_makePySideUI(btn_ANI, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, 0)))
		dp_makePySideUI(btn_CAM, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, 0)))

		colorHide = rgb_hex(colorA, -15)
		colorGray = rgb_hex(colorA, 0)
		# check animation
		if not os.path.exists(filePath_ANI):
			button(btn_ANI, e= 1, en= 0)
			if filePath_ANI: button(btn_ANI, e= 1, ann= button(btn_ANI, q= 1, ann= 1) + ' (Not Exists)')
			text(txt_ANI, e= 1, en= 0)
			uiObj = dp_makePySideUI(btn_ANI, 'QPushButton {color: %s; background-color: %s}' % (colorGray, colorHide))
			if filePath_ANI: f = uiObj.font();f.setStrikeOut(True);uiObj.setFont(f)
			uiObj = dp_makePySideUI(txt_ANI, 'QObject {color: %s;}' % colorGray)
			if filePath_ANI: f = uiObj.font();f.setStrikeOut(True);uiObj.setFont(f)
		else:
			ver = sInfo.getVerSN(sceneName_ANI)
			button(btn_ANI, e= 1, l= btn_ANI_label + (('_' + ver) if ver else ''))
		# check camera
		if not os.path.exists(filePath_CAM):
			button(btn_CAM, e= 1, en= 0)
			if filePath_CAM: button(btn_CAM, e= 1, ann= button(btn_CAM, q= 1, ann= 1) + ' (Not Exists)')
			text(txt_CAM, e= 1, en= 0)
			uiObj = dp_makePySideUI(btn_CAM, 'QPushButton {color: %s; background-color: %s}' % (colorGray, colorHide))
			if filePath_CAM: f = uiObj.font();f.setStrikeOut(True);uiObj.setFont(f)
			uiObj = dp_makePySideUI(txt_CAM, 'QObject {color: %s;}' % colorGray)
			if filePath_CAM: f = uiObj.font();f.setStrikeOut(True);uiObj.setFont(f)
		else:
			ver = sInfo.getVerSN(sceneName_CAM)
			button(btn_CAM, e= 1, l= 'CAM' + (('_' + ver) if ver else ''))

		# check update
		if date_ANI and date_ANI[-1] >= userHistory[workRoot]:
			dp_makePySideUI(txt_ANI, 'QObject {font: bold; color: #E3C55E}')
			dp_makePySideUI(btn_ANI, 'QPushButton {background-color: #E3C55E}')
			frameLayout(shotFrameName, e= 1, cl= 0, l= ecShotLable, bgc= rgb_nor(hex_rgb('E3C55E')))
		if date_CAM and date_CAM[-1] >= userHistory[workRoot]:
			dp_makePySideUI(txt_CAM, 'QObject {font: bold; color: #E3C55E}')
			dp_makePySideUI(btn_CAM, 'QPushButton {background-color: #E3C55E}')
			frameLayout(shotFrameName, e= 1, cl= 0, l= ecShotLable, bgc= rgb_nor(hex_rgb('E3C55E')))


		# build asset frameLayouts
		shotFrameName_asset_Dict = {}
		shot_assetList = gcLog['shots'][shot]['GEO'].keys()
		shot_assetList.sort()
		for num, asset in enumerate(shot_assetList):

			# SHD info extract
			date_SHD = gcLog['asset'][asset]['SHD']['MST'].keys() if gcLog['asset'].has_key(asset) else []
			date_SHD.sort()
			dateShortSHD = shortDateFormat(date_SHD[-1]) if date_SHD and date_SHD[-1] else ''
			filePath_SHD = gcLog['asset'][asset]['SHD']['MST'][date_SHD[-1]] if dateShortSHD else ''
			fileName_SHD = os.path.basename(filePath_SHD) if dateShortSHD else ''
			sceneName_SHD = os.path.splitext(fileName_SHD)[0] if dateShortSHD else ''

			# RIG info extract
			date_RIG = gcLog['asset'][asset]['RIG']['MST'].keys() if gcLog['asset'].has_key(asset) else []
			date_RIG.sort()
			dateShortRIG = shortDateFormat(date_RIG[-1]) if date_RIG and date_RIG[-1] else ''
			filePath_RIG = gcLog['asset'][asset]['RIG']['MST'][date_RIG[-1]] if dateShortRIG else ''
			fileName_RIG = os.path.basename(filePath_RIG) if dateShortRIG else ''
			sceneName_RIG = os.path.splitext(fileName_RIG)[0] if dateShortRIG else ''
			
			# GEO info extract
			date_GEO = gcLog['shots'][shot]['GEO'][asset].keys()
			date_GEO.sort()
			dateShortGEO = shortDateFormat(date_GEO[-1]) if date_GEO and date_GEO[-1] else ''
			filePath_GEO = gcLog['shots'][shot]['GEO'][asset][date_GEO[-1]] if dateShortGEO else ''
			fileName_GEO = os.path.basename(filePath_GEO) if dateShortGEO else ''
			sceneName_GEO = os.path.splitext(fileName_GEO)[0] if dateShortGEO else ''
			geoCacheDir = moGeoCache.getGeoCacheDir(asset, 0, sceneName_GEO) if dateShortGEO else ''

			astRow = rowLayout(nc= 2, adj= 1, h= 24)
			shotFrameName_asset = frameLayout(l= asset, cll= 1, cl= 1, bgc= rgb_nor(hex_rgb('686868')),
				cc= 'cmds.rowLayout("' + astRow + '", e= 1, h= 24)',
				ec= 'cmds.rowLayout("' + astRow + '", e= 1, h= 69)')
			dp_makePySideUI(shotFrameName_asset, 'QWidget {color: #222222; background-color: #606060}')
			
			columnLayout(adj= 1)

			rowLayout(nc= 3, adj= 1)
			txt_SHD = windowName + '_text_' + shot + asset + 'SHD'
			txt_RIG = windowName + '_text_' + shot + asset + 'RIG'
			txt_GEO = windowName + '_text_' + shot + asset + 'GEO'
			text(txt_SHD, l= dateShortSHD, al= 'center', w= 65)
			text(txt_RIG, l= dateShortRIG, al= 'center', w= 65)
			text(txt_GEO, l= dateShortGEO, al= 'center', w= 65)
			setParent('..')
			
			rowLayout(nc= 3, adj= 1)
			btn_SHD = windowName + '_button_' + shot + asset + 'SHD'
			btn_RIG = windowName + '_button_' + shot + asset + 'RIG'
			btn_GEO = windowName + '_button_' + shot + asset + 'GEO'

			button(btn_SHD, l= 'SHD', w= 65, h= 25, ann= fileName_SHD, c= partial(btncmd_SHD, filePath_SHD))
			button(btn_RIG, l= 'RIG', w= 65, h= 25, ann= fileName_RIG, c= partial(btncmd_RIG, filePath_RIG))
			button(btn_GEO, l= 'GEO', w= 65, h= 25, ann= fileName_GEO, c= partial(btncmd_GEO, sceneName_GEO))
			dp_makePySideUI(btn_SHD, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, 0)))
			dp_makePySideUI(btn_RIG, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, 0)))
			dp_makePySideUI(btn_GEO, 'QPushButton {background-color: %s}' % (rgb_hex(colorA, 0)))
			setParent('..')

			setParent('..')
			setParent('..')
			columnLayout(adj= 2)
			delAssetBtn = button(l= '', w= 5, h= 20, c= partial(btncmd_delAsset, shotNum, asset))
			text(l= '', w= 5, h= 45)
			dp_makePySideUI(delAssetBtn, 'QPushButton {background-color: #%s; color: #%s}' % ('624249', '1F1F1F'))
			setParent('..')
			setParent('..')

			colorHide = rgb_hex(colorA, -15)
			colorGray = rgb_hex(colorA, 0)
			# check SHD
			if not os.path.exists(filePath_SHD):
				button(btn_SHD, e= 1, en= 0)
				if filePath_SHD: button(btn_SHD, e= 1, ann= button(btn_SHD, q= 1, ann= 1) + ' (Not Exists)')
				text(txt_SHD, e= 1, en= 0)
				uiObj = dp_makePySideUI(btn_SHD, 'QPushButton {color: %s; background-color: %s}' % (colorGray, colorHide))
				if filePath_SHD: f = uiObj.font();f.setStrikeOut(True);uiObj.setFont(f)
				uiObj = dp_makePySideUI(txt_SHD, 'QObject {color: %s;}' % colorGray)
				if filePath_SHD: f = uiObj.font();f.setStrikeOut(True);uiObj.setFont(f)
			else:
				ver = sInfo.getVerSN(sceneName_SHD)
				button(btn_SHD, e= 1, l= 'SHD' + (('_' + ver) if ver else ''))
			# check RIG
			if not os.path.exists(filePath_RIG):
				button(btn_RIG, e= 1, en= 0)
				if filePath_RIG: button(btn_RIG, e= 1, ann= button(btn_RIG, q= 1, ann= 1) + ' (Not Exists)')
				text(txt_RIG, e= 1, en= 0)
				uiObj = dp_makePySideUI(btn_RIG, 'QPushButton {color: %s; background-color: %s}' % (colorGray, colorHide))
				if filePath_RIG: f = uiObj.font();f.setStrikeOut(True);uiObj.setFont(f)
				uiObj = dp_makePySideUI(txt_RIG, 'QObject {color: %s;}' % colorGray)
				if filePath_RIG: f = uiObj.font();f.setStrikeOut(True);uiObj.setFont(f)
			else:
				ver = sInfo.getVerSN(sceneName_RIG)
				button(btn_RIG, e= 1, l= 'RIG' + (('_' + ver) if ver else ''))
			
			# check GEO
			if not os.path.exists(geoCacheDir):
				button(btn_GEO, e= 1, en= 0)
				if filePath_GEO: button(btn_GEO, e= 1, ann= button(btn_GEO, q= 1, ann= 1) + ' (Not Exists)')
				text(txt_GEO, e= 1, en= 0)
				uiObj = dp_makePySideUI(btn_GEO, 'QPushButton {color: %s; background-color: %s}' % (colorGray, colorHide))
				if filePath_GEO: f = uiObj.font();f.setStrikeOut(True);uiObj.setFont(f)
				uiObj = dp_makePySideUI(txt_GEO, 'QObject {color: %s;}' % colorGray)
				if filePath_GEO: f = uiObj.font();f.setStrikeOut(True);uiObj.setFont(f)
			else:
				ver = sInfo.getVerSN(sceneName_GEO)
				button(btn_GEO, e= 1, l= 'GEO' + (('_' + ver) if ver else ''))

			# check update
			hasUpdate = 0
			if date_SHD and date_SHD[-1] >= userHistory[workRoot]:
				dp_makePySideUI(txt_SHD, 'QObject {font: bold; color: #E3C55E}')
				dp_makePySideUI(btn_SHD, 'QPushButton {background-color: #E3C55E}')
				hasUpdate = 1
			if date_RIG and date_RIG[-1] >= userHistory[workRoot]:
				dp_makePySideUI(txt_RIG, 'QObject {font: bold; color: #E3C55E}')
				dp_makePySideUI(btn_RIG, 'QPushButton {background-color: #E3C55E}')
				hasUpdate = 1
			if date_GEO and date_GEO[-1] >= userHistory[workRoot]:
				dp_makePySideUI(txt_GEO, 'QObject {font: bold; color: #E3C55E}')
				dp_makePySideUI(btn_GEO, 'QPushButton {background-color: #E3C55E}')
				hasUpdate = 1
			if hasUpdate:
				frameLayout(shotFrameName, e= 1, cl= 0, l= ecShotLable, bgc= rgb_nor(hex_rgb('E3C55E')))
				rowLayout(astRow, e= 1, h= 69)
				frameLayout(shotFrameName_asset, e= 1, cl= 0, bgc= rgb_nor(hex_rgb('E3C55E')))

			shotFrameName_asset_Dict[astRow] = shotFrameName_asset

		def ecAssetBtn_do(ecAssetBtn, shotFrameName_asset_Dict, *args):
			if button(ecAssetBtn, q= 1, l= 1) == '+':
				cmd = 0
				h = 69
				button(ecAssetBtn, e= 1, l= '-')
			else:
				cmd = 1
				h = 24
				button(ecAssetBtn, e= 1, l= '+')
			for row in shotFrameName_asset_Dict.keys():
				frameLayout(shotFrameName_asset_Dict[row], e= 1, cl= cmd)
				rowLayout(row, e= 1, h= h)
		button(ecAssetBtn, e= 1, c= partial(ecAssetBtn_do, ecAssetBtn, shotFrameName_asset_Dict))


		formLayout(formName, e= 1, af=[(titleName, 'left', -20), (titleName, 'top', -25)])
		formLayout(formName, e= 1, af=[(frameRate, 'left',   4), (frameRate, 'top',  74)])
		formLayout(formName, e= 1, af=[(frameRang, 'left',  10), (frameRang, 'top',  92)])
		formLayout(formName, e= 1, af=[(columName, 'right',  0), (columName, 'top', 0), (columName, 'left', 120)])

		setParent('..')
		setParent('..')
		text(l= '', h= 2)
		setParent('..')


def ui_geoCacheIO():

	windowName = 'msMayaHub'

	sInfo = _getSceneInfo()
	userHistory = getUserHistory()
	workRoot = workspace(q= 1, rd= 1)
	ctrBaseColor = [.32, .32, .32]
	ctrSubsColor = [.22, .22, .22]

	if dockControl(windowName, q= 1, ex= 1):
		deleteUI(windowName)

	main_window = window()
	
	mainForm = formLayout(p= main_window)
	
	staticArea = columnLayout(adj= 1, rs= 5)
	if True:
		rowLayout(nc= 3, adj= 3)
		if True:
			btnPrj = button(l= 'Set Project', h= 23, w= 250, bgc= [.25, .25, .25], c= ui_setProject)
			btnREF = button(l= 'Refresh', h= 23, w= 100, bgc= [.21, .21, .21], c= renewUI)
			image(h= 23,
				i= 'T:/MoonShineDesign/MS_Corporate/Logo/LogoTextBlack_NoOpacity_tiny.png')
			setParent('..')
	

		text(l= sInfo.workspaceRoot, al= 'left', en= 0)
		projtext = text(l= sInfo.workspaceRoot.split(sInfo.sep)[1].split('_')[1], h= 36, al= 'left')
		setParent('..')


	paneArea = paneLayout(cn= 'horizontal2', shp= 1, ps= [1, 100, 1])
	if True:	
		# PUSH #####
		columnLayout(adj= 1, rs= 5, p= paneArea)
		if True:
			pushtext = text(l= 'PUSH  `submit / output', al= 'left', h= 20)
			columnLayout(adj= 1, bgc= ctrBaseColor)
			if True:
				rowLayout(nc= 3, adj= 1)
				if True:
					btnMOD = button(l= 'MOD', h= 37, w= 120, bgc= ctrSubsColor, c= submitMOD)
					btnSHD = button(l= 'SHD', h= 37, w= 120, bgc= ctrSubsColor, c= submitSHD)
					btnRIG = button(l= 'RIG', h= 37, w= 120, bgc= ctrSubsColor, c= submitRIG)
					setParent('..')
				
				rowLayout(nc= 7)
				if True:
					tex_com = text(l= 'Common: ', w= 55, al= 'right')
					text(l= '')
					tex_pgeo = text(l= 'Partial GEO ', al= 'right', w= 70)
					checkBox('cBox_isPartial', l= '', w= 13)
					text(l= '')
					txt_over1 = text('  *Override ', en= 0)
					textField('textF_assetName', pht= 'assetName', w= 125)
					setParent('..')
				rowLayout(nc= 7)
				if True:
					tex_exp = text(l= 'Export: ', w= 55, al= 'right')
					text(l= '')
					tex_addD = text(l= 'Add Division ', al= 'right', w= 70)
					intFieldGrp('intF_sdLevel', l= '', v1= 0, ad2= 1, cw= [2, 14], w= 19, cc= intcmd_setMinMax)
					text(l= '')
					txt_over2 = text('*Override ', en= 0)
					textField('textF_sceneName', pht= 'sceneName', w= 125)
					setParent('..')
				rowLayout(nc= 7)
				if True:
					tex_imp = text(l= 'Import: ', w= 55, al= 'right')
					text(l= '')
					tex_sam = text(l= 'Same Name ', al= 'right', w= 70)
					checkBox('cBox_ignorDupl', l= '', w= 13)
					text(l= '')
					txt_filt = text('  *Filter       ', en= 0)
					textField('textF_filter', pht= 'string1;string2...', w= 125)
					setParent('..')
				
				rowLayout(nc= 3, adj= 3)
				if True:
					btnPushName = windowName + '_button_' + 'submit'
					button(btnPushName + 'ANI', l= 'ANI', h= 37, w= 120, bgc= ctrSubsColor, c= submitANI)
					button(btnPushName + 'CAM', l= 'CAM', h= 37, w= 120, bgc= ctrSubsColor, c= submitCAM)
					button(btnPushName + 'GEO', l= 'GEO', h= 37, w= 120, bgc= ctrSubsColor, c= submitGEO)
					setParent('..')
				setParent('..')
			text(l= '', h= 1)
			setParent('..')

		# PULL #####
		pullForm = formLayout(p= paneArea)
		if True:
			pulltext = text(l= 'PULL  `open / input', al= 'left', h= 20)
			pullTab = tabLayout(bs= 'none', scr= 1)
			if True:
				shotColumn = columnLayout(rs= 5)
				if True:
					mkShotListBtn(windowName, shotColumn)
					setParent('..')
				tabLayout(pullTab, e= 1, tabLabel= [shotColumn, '    S H O T S    '])

				assetColumn = columnLayout(rs= 5)
				if True:
					mkAssetListBtn(windowName, assetColumn)
					setParent('..')
				tabLayout(pullTab, e= 1, tabLabel= [assetColumn, '    A S S E T    '])

				setParent('..')

		formLayout(pullForm, e= 1, af=[(pulltext, 'top', 3)])
		formLayout(pullForm, e= 1, ac=[(pullTab, 'top', 8, pulltext)])
		formLayout(pullForm, e= 1, af=[(pullTab, 'bottom', 0), (pullTab, 'right', 0), (pullTab, 'left', 0)])

		logger.info('Last Time Logged in: ' + userHistory[workRoot])
		userHistory[workRoot] = str(datetime.now())
		setUserHistory(userHistory)

	formLayout(mainForm, e= 1, af= [(staticArea, 'top', 0)])
	formLayout(mainForm, e= 1, af= [(paneArea, 'top', 90), (paneArea, 'bottom', 0)])


	# pySide
	dp_makePySideUI(btnPrj, 'QPushButton {font: 14px Courier; color: #25696B;}')
	dp_makePySideUI(btnREF, 'QPushButton {font: 14px Courier; color: #407043;}')
	dp_makePySideUI(projtext, 'QObject {font: bold 32px; color: #222222; font-family: Arial;}')
	dp_makePySideUI(pushtext, 'QObject {font: bold 20px; font-family: Arial; color: #3C3C3C;}')
	dp_makePySideUI(btnMOD, 'QPushButton {font: 24px Courier; color: #8C7B3D;}')
	dp_makePySideUI(btnSHD, 'QPushButton {font: 24px Courier; color: #8C7B3D;}')
	dp_makePySideUI(btnRIG, 'QPushButton {font: 24px Courier; color: #8C7B3D;}')
	dp_makePySideUI(tex_com, 'QObject {color: #AAAAAA;}')
	dp_makePySideUI(tex_pgeo, 'QObject {color: #AAAAAA;}')
	dp_makePySideUI('cBox_isPartial', 'QObject {color: #AAAAAA; background-color: #252525;}')
	dp_makePySideUI(txt_over1, 'QObject {color: #AAAAAA;}')
	dp_makePySideUI('textF_assetName', 'QObject {color: #AAAAAA; background-color: #252525; border-radius: 2px;}')
	dp_makePySideUI(tex_exp, 'QObject {color: #AAAAAA;}')
	dp_makePySideUI(tex_addD, 'QObject {color: #AAAAAA;}')
	dp_makePySideUI('intF_sdLevel', 'QObject {color: #AAAAAA; background-color: #252525; border-radius: 2px;}')
	dp_makePySideUI(txt_over2, 'QObject {color: #AAAAAA;}')
	dp_makePySideUI('textF_sceneName', 'QObject {color: #AAAAAA; background-color: #252525; border-radius: 2px;}')
	dp_makePySideUI(tex_imp, 'QObject {color: #AAAAAA;}')
	dp_makePySideUI(tex_sam, 'QObject {color: #AAAAAA;}')
	dp_makePySideUI('cBox_ignorDupl', 'QObject {color: #AAAAAA; background-color: #252525;}')
	dp_makePySideUI(txt_filt, 'QObject {color: #AAAAAA;}')
	dp_makePySideUI('textF_filter', 'QObject {color: #AAAAAA; background-color: #252525; border-radius: 2px;}')
	dp_makePySideUI(btnPushName + 'ANI', 'QPushButton {font: 24px Courier; color: #9D344C;}')
	dp_makePySideUI(btnPushName + 'CAM', 'QPushButton {font: 24px Courier; color: #9D344C;}')
	dp_makePySideUI(btnPushName + 'GEO', 'QPushButton {font: 24px Courier; color: #AAAAAA;}')
	dp_makePySideUI(pulltext, 'QObject {font: bold 20px; font-family: Arial; color: #3C3C3C;}')

	dockControl(windowName, area= 'right', content= main_window, allowedArea= ['right', 'left'], vis= 1, s= 0, w= 380)


if __name__ == '__main__':
	ui_geoCacheIO()