# -*- coding:utf-8 -*-
'''
Created on 2016.07.06

@author: davidpower
'''
from pymel.core import *
from functools import partial
from subprocess import Popen, PIPE
import moCache.moGeoCache as moGeoCache; reload(moGeoCache)
import moCache.moGeoCacheUICmdExport as moGeoCacheUICmdExport; reload(moGeoCacheUICmdExport)
import os



def exec_getParams(*args):

	global rbtn_geoIO
	global txt_infoAssetName
	global txt_infoSceneName
	global cBox_isPartial
	global cBox_isStatic
	global cBox_division
	global cBox_dupName
	global textF_filter
	global rbtn_execBy
	
	conflictList = str(textField(textF_filter, q= 1, tx= 1))
	assetName_override = str(textField(textF_assetName, q= 1, tx= 1))
	paramDict = {
		'assetName' : assetName_override if assetName_override else None,
		'sceneName' : str(text(txt_infoSceneName, q= 1, l= 1)),
		'isPartial' : checkBox(cBox_isPartial, q= 1, v= 1),
		 'isStatic' : checkBox(cBox_isStatic, q= 1, v= 1),
		   'subdiv' : 1 if checkBox(cBox_division, q= 1, v= 1) else None,
		 'sameName' : checkBox(cBox_dupName, q= 1, v= 1),
		 'conflict' : conflictList.split(';') if conflictList else []
	}

	if exec_checkParam(paramDict):
		mode = radioButtonGrp(rbtn_geoIO, q= 1, sl= 1)
		actionType = radioButtonGrp(rbtn_execBy, q= 1, sl= 1)
		if mode == 1:
			exec_Export(actionType, paramDict)
		if mode == 2:
			exec_Import(3, paramDict)


def exec_checkParam(paramDict):
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
	return True

	
def exec_Export(actionType, paramDict):
	"""
	"""
	if actionType == 1:
		pyFile = moGeoCacheUICmdExport.__file__
		projPath = workspace(q= 1, rd= 1)
		filePath = str(system.sceneName())
		assetList = str([dag.name() for dag in ls(sl= 1)])
		paramDict = str(paramDict)
		Popen(['mayapy', pyFile, projPath, filePath, assetList, paramDict], shell= False)
	if actionType == 2:
		pass
	if actionType == 3:
		moGeoCache.exportGeoCache(
			subdivLevel= paramDict['subdiv'],
			isPartial= paramDict['isPartial'],
			isStatic= paramDict['isStatic'],
			assetName_override= paramDict['assetName'],
			sceneName_override= paramDict['sceneName']
			)


def exec_Import(actionType, paramDict):
	"""
	"""
	'''
	if actionType == 1:
		pass
	if actionType == 2:
		pass
	'''
	if actionType == 3:
		moGeoCache.importGeoCache(
			sceneName= paramDict['sceneName'],
			isPartial= paramDict['isPartial'],
			assetName_override= paramDict['assetName'],
			ignorDuplicateName= paramDict['sameName'],
			conflictList= paramDict['conflict']
			)


def prep_SHDSet(mode, *args):
	"""
	"""
	sname = system.sceneName().namebase.lower()
	if '_shading_' not in sname and '_shd_' not in sname:
		msg = 'This scene is not a shading asseet.\n' \
			+ '(Filename does not contain "_shading_" or "_shd_".)'
		confirmDialog(t= 'Abort', m= msg, b= ['Ok'], db= 'Ok', icn= 'warning')
		return

	if mode == 'wrapSet':
		actSetName = 'moGCWrap'
		filt = ['mesh']

	# deselect non-filt object
	objList = ls(sl= 1)
	for obj in objList:
		if (obj.nodeType() == 'transform' and obj.getShape().nodeType() not in filt)\
		or (obj.nodeType() != 'transform' and obj.nodeType() not in filt):
			select(obj, tgl= 1)
	# check if set exists
	objList = ls(sl= 1)

	if mode == 'wrapSet':
		if len(objList) > 1:
			actSet = ls(actSetName + '_*', typ= 'objectSet')
			srcObj = objList[-1].name()
			if actSet:
				wsDict = {}
				for wSet in actSet:
					wsDict[getAttr(wSet + '.wrapSource')] = wSet
				# check if selected source had assigned
				if srcObj in wsDict.keys():
					sets(wsDict[srcObj], add= objList)

					return
			# create set and add mesh
			wSet = sets(n= actSetName + '_1')
			addAttr(wSet, ln= 'wrapSource', dt= 'string')
			setAttr(wSet + '.wrapSource', srcObj)
		else:
			msg = 'Select at least two objects.\n' \
				+ '(wrap targets, and one wrap source.)'
			confirmDialog(t= 'Abort', m= msg, b= ['Ok'], db= 'Ok', icn= 'warning')


def prep_RIGSet(mode, *args):
	"""
	"""
	sname = system.sceneName().namebase.lower()
	if '_rigging_' not in sname and '_rig_' not in sname:
		msg = 'This scene is not a rigging asseet.\n' \
			+ '(Filename does not contain "_rigging_" or "_rig_".)'
		confirmDialog(t= 'Abort', m= msg, b= ['Ok'], db= 'Ok', icn= 'warning')
		return

	if mode == 'smoothSet':
		actSetName = 'moGCSmoothMask'
		filt = ['mesh']
	if mode == 'rigCtrlSet':
		actSetName = 'moGCRigCtrlExport'
		filt = ['nurbsCurve', 'locator']
	if mode == 'nodeOutSet':
		actSetName = 'moGCNodeOut'
		filt = ['mesh']

	if mode != 'nodeOutSet':
		# deselect non-filt object
		objList = ls(sl= 1)
		for obj in objList:
			if (obj.nodeType() == 'transform' and obj.getShape().nodeType() not in filt)\
			or (obj.nodeType() != 'transform' and obj.nodeType() not in filt):
				select(obj, tgl= 1)
		objList = ls(sl= 1)

	if mode == 'nodeOutSet':
		objList = []
		mChB =  uitypes.ChannelBox('mainChannelBox')
		ctrlList = mChB.getMainObjectList()
		attrList = mChB.getSelectedMainAttributes()
		if ctrlList:
			exec('dag = SCENE.' + ctrlList[0])
			objList = [dag]

	# check if set exists
	if objList:
		actSet = ls(actSetName, typ= 'objectSet')
		if actSet:
			if mode == 'nodeOutSet':
				nOutNodeDict = eval(actSet[0].outNodeDict.get())
			members = sets(actSet[0], q= 1, no= 1)
			for obj in objList:
				if obj.nodeType() != 'transform':
					obj = obj.getParent()
				if obj in members:
					# remove mesh
					sets(actSet[0], rm= obj)
					if mode == 'nodeOutSet':
						del nOutNodeDict[obj.name()]
						actSet[0].outNodeDict.set(str(nOutNodeDict))
				else:
					# add mesh
					sets(actSet[0], add= obj)
					if mode == 'nodeOutSet':
						nOutNodeDict[obj.name()] = attrList
						actSet[0].outNodeDict.set(str(nOutNodeDict))
		else:
			# create set and add mesh
			actSet = sets(n= actSetName)
			if mode == 'nodeOutSet':
				nOutNodeDict = { objList[0].name() : attrList }
				if not attributeQuery('outNodeDict', node= actSet, ex= 1):
					addAttr(actSet, ln= 'outNodeDict', dt= 'string')
				actSet.outNodeDict.set(str(nOutNodeDict))


def prep_setSmoothExclusive(*args):
	"""
	"""
	global cBox_exclusive
	sname = system.sceneName().namebase.lower()
	if '_rigging_' not in sname and '_rig_' not in sname:
		msg = 'This scene is not a rigging asseet.\n' \
			+ '(Filename does not contain "_rigging_" and "_rig_".)'
		confirmDialog(t= 'Abort', m= msg, b= ['Ok'], db= 'Ok', icn= 'warning')
		checkBox(cBox_exclusive, e= 1, v= 0)
		return

	smoothSetName = 'moGCSmoothMask'

	smoothSet = ls(smoothSetName, typ= 'objectSet')
	if smoothSet:
		if not attributeQuery('smoothExclusive', node= smoothSet[0], ex= 1):
			addAttr(smoothSet[0], ln= 'smoothExclusive', at= 'bool')
		value = checkBox(cBox_exclusive, q= 1, v= 1)
		setAttr(smoothSet[0] + '.smoothExclusive', value)
	else:
		checkBox(cBox_exclusive, e= 1, v= 0)


def ui_getSmoothExclusive():
	"""
	"""
	global cBox_exclusive
	sname = system.sceneName().namebase.lower()
	if '_rigging_' not in sname and '_rig_' not in sname:
		checkBox(cBox_exclusive, e= 1, v= 0)
		return

	smoothSetName = 'moGCSmoothMask'
	
	smoothSet = ls(smoothSetName, typ= 'objectSet')
	if smoothSet and attributeQuery('smoothExclusive', node= smoothSet[0], ex= 1):
		value = getAttr(smoothSet[0] + '.smoothExclusive')
		checkBox(cBox_exclusive, e= 1, v= 1)
	else:
		checkBox(cBox_exclusive, e= 1, v= 0)


def ui_getAssetName():
	"""
	"""
	if ls(sl= 1):
		if not textField(textF_assetName, q= 1, tx= 1):
			assetList = moGeoCache.getAssetList()
			text(txt_infoAssetName, e= 1, l= ', '.join(assetList))
		else:
			warning('AssetName has override, only the last rootNode will be processed.')
			text(txt_infoAssetName, e= 1, l= textField(textF_assetName, q= 1, tx= 1))
	else:
		text(txt_infoAssetName, e= 1, l= '')


def ui_getSceneName():
	"""
	"""
	if not textField(textF_sceneName, q= 1, tx= 1):
		if radioButtonGrp(rbtn_geoIO, q= 1, sl= 1) == 1:
			sname = system.sceneName().namebase
			text(txt_infoSceneName, e= 1, l= sname)
		else:
			text(txt_infoSceneName, e= 1, l= '')
	else:
		text(txt_infoSceneName, e= 1, l= textField(textF_sceneName, q= 1, tx= 1))


def ui_initPrep(sideValue):
	"""
	"""
	global cBox_exclusive

	frameLayout(l= ' Preparation  -  S H D   R I G')
	columnLayout(adj= 1, rs= 4)
	if True:
		columnLayout(adj= 1)
		if True:
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 10)
				tex_shd = text(l= 'S H D', al= 'center', fn= 'boldLabelFont', w= 40)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 3, adj= 2)
			if True:
				text(l= '', w= sideValue)
				btn_addWrapSet = button(l= 'Add Wrap Set', c= partial(prep_SHDSet, 'wrapSet'))
				text(l= '', w= sideValue)
				setParent('..')

		columnLayout(adj= 1)
		if True:
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 10)
				tex_rig = text(l= 'R I G', al= 'center', fn= 'boldLabelFont', w= 40)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 2, adj= 2, h= 18)
			if True:
				text(l= '', w= sideValue)
				cBox_exclusive = checkBox(l= 'Make Smooth Set Excludsive', cc= prep_setSmoothExclusive)
				setParent('..')
			rowLayout(nc= 3, adj= 2)
			if True:
				text(l= '', w= sideValue)
				btn_makeSmoothSet = button(l= 'Model Smooth Set', c= partial(prep_RIGSet, 'smoothSet'))
				text(l= '', w= sideValue)
				setParent('..')
			#text(l= '', h= 5)
			rowLayout(nc= 3, adj= 2)
			if True:
				text(l= '', w= sideValue)
				btn_makeCurvesSet = button(l= 'Rigging Control Set', c= partial(prep_RIGSet, 'rigCtrlSet'))
				text(l= '', w= sideValue)
				setParent('..')
			#text(l= '', h= 5)
			rowLayout(nc= 3, adj= 2)
			if True:
				text(l= '', w= sideValue)
				btn_makeSpecKeyRig = button(l= 'Node Output Set', c= partial(prep_RIGSet, 'nodeOutSet'))
				text(l= '', w= sideValue)
				setParent('..')
			setParent('..')

		text(l= '', h= 5)

		setParent('..')
		setParent('..')


def ui_geoCache(midValue):
	"""
	"""
	global rbtn_geoIO
	global txt_infoAssetName
	global txt_infoSceneName
	global cBox_isPartial
	global cBox_isStatic
	global textF_assetName
	global cBox_division
	global textF_sceneName
	global menu_choose
	global cBox_dupName
	global textF_filter
	global rbtn_execBy

	frameLayout(l= ' GeoCaching  -  A N I   S I M   G E O')
	columnLayout(adj= 1)
	if True:
		columnLayout(adj= 1)
		stuValue = 100
		if True:
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 10)
				tex_sta = text(l= 'Status', al= 'center', fn= 'boldLabelFont', w= 40)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= 'Mode : ', al= 'right', w= stuValue)
				rbtn_geoIO = radioButtonGrp(nrb= 2, l='', cw3= [0, 70, 70],
					cl3= ['right', 'left', 'left'], la2= ['Export', 'Import'], sl= 1)
				setParent('..')
			text(l= '', h= 4)
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= 'Asset : ', al= 'right', w= stuValue)
				txt_infoAssetName = text(l= '', al= 'left')
				setParent('..')
			text(l= '', h= 3)
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= 'Scene : ', al= 'right', w= stuValue)
				txt_infoSceneName = text(l= '', al= 'left')
				setParent('..')
			setParent('..')

		columnLayout(adj= 1)
		if True:
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 5)
				tex_com = text(l= 'Common', al= 'center', fn= 'boldLabelFont', w= 50)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= '', w= midValue)
				cBox_isPartial = checkBox(l= 'Partial Export')
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				txt_assetName = text('Asset ', al= 'right', w= midValue)
				textF_assetName = textField(pht= 'assetName override')
				setParent('..')
			setParent('..')

		col_exp = columnLayout(adj= 1, vis= 1)
		if True:
			en = 1
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 10)
				tex_exp = text(l= 'Export', al= 'center', fn= 'boldLabelFont', w= 40, en= en)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= '', w= midValue)
				cBox_isStatic = checkBox(l= 'Static Object')
				setParent('..')
			'''
			rowLayout(nc= 3, adj= 3, h= 22)
			if True:
				text(l= '( 0~4 ) ', al= 'right', en= 0, w= midValue)
				intF_division = intFieldGrp(l= '', v1= 0, ad2= 1, cw= [2, 36], w= 40, en= en)
				tex_division = text(l= 'Division Smooth', al= 'left', en= en)
				setParent('..')
			'''
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= '', w= midValue)
				cBox_division = checkBox(l= 'Division Smooth')
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				txt_sceneName = text('Scene ', al= 'right', w= midValue, en= en)
				textF_sceneName = textField(pht= 'sceneName override', en= en)
				setParent('..')
			text(l= '', h= 3)
			setParent('..')

		col_imp = columnLayout(adj= 1, vis= 0)
		if True:
			en = 1
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 10)
				tex_com = text(l= 'Import', al= 'center', fn= 'boldLabelFont', w= 40, en= en)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 3, adj= 3)
			if True:
				txt_choose = text('', al= 'right', w= midValue - 20, en= en)
				icBtn_textF_choose = iconTextButton(i= 'fileOpen.png', w= 20, h= 20, en= en)
				textF_choose = textField(pht= 'scene geoCacheDir', en= en)
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= '', w= midValue)
				cBox_dupName = checkBox(l= 'Duplicate Names', en= en)
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				txt_filter = text('Filter Out ', al= 'right', w= midValue, en= en)
				textF_filter = textField(pht= 'string1;string2...', en= en)
				setParent('..')
			setParent('..')

		col_action = columnLayout(adj= 1)
		actValue = 50
		if True:
			rowLayout(nc= 3, adj= 3)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 10)
				tex_act = text(l= 'Action', al= 'center', fn= 'boldLabelFont', w= 40, en= 1)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				text(l= 'By : ', al= 'right', w= actValue)
				rbtn_execBy = radioButtonGrp(nrb= 3, l='', cw4= [0, 70, 70, 70], h= 30,
					cl4= ['right', 'left', 'left', 'left'],
					la3= ['mayapy', 'deadline', 'GUI'], sl= 1)
				setParent('..')

			text(l= '', h= 5)
			setParent('..')
		button(l= 'Execute', h= 50, c= exec_getParams)

		setParent('..')
	setParent('..')

	# commands
	'''
	def intcmd_setMinMax(*args):
		global intF_division
		intvalue = intFieldGrp(intF_division, q= 1, v1= 1)
		if intvalue < 0:
			intFieldGrp(intF_division, e= 1, v1= 0)
		if intvalue > 4:
			intFieldGrp(intF_division, e= 1, v1= 4)

	intFieldGrp(intF_division, e= 1, cc= intcmd_setMinMax)
	'''

	def geoCacheIOctrlSwitch(col, vis, *args):
		layout(col, e= 1, vis= vis)
		if col == col_exp and vis:
			columnLayout(col_action, e= 1, en= 1)
			checkBox(cBox_isPartial, e= 1, l= 'Partial Export')
			ui_getSceneName()
		if col == col_imp and vis:
			columnLayout(col_action, e= 1, en= 0)
			checkBox(cBox_isPartial, e= 1, l= 'Partial Import')
			text(txt_infoSceneName, e= 1, l= textField(textF_choose, q= 1, tx= 1))

	radioButtonGrp(rbtn_geoIO, e= 1,
			of1= partial(geoCacheIOctrlSwitch, col_exp, 0),
			on1= partial(geoCacheIOctrlSwitch, col_exp, 1),
			of2= partial(geoCacheIOctrlSwitch, col_imp, 0),
			on2= partial(geoCacheIOctrlSwitch, col_imp, 1))

	def textFieldSync(source, target, *args):
		s = textField(source, q= 1, tx= 1)
		if s:
			text(target, e= 1, l= s)
		else:
			if str(textField(source, q= 1, pht= 1)).startswith('asset'):
				ui_getAssetName()
			if str(textField(source, q= 1, pht= 1)).startswith('scene'):
				ui_getSceneName()

	textField(textF_assetName, e= 1, cc= partial(textFieldSync, textF_assetName, txt_infoAssetName))
	textField(textF_sceneName, e= 1, cc= partial(textFieldSync, textF_sceneName, txt_infoSceneName))
	textField(textF_choose, e= 1, cc= partial(textFieldSync, textF_choose, txt_infoSceneName))

	def openCacheFolder(*args):
		assetName = text(txt_infoAssetName, q= 1, l= 1)
		msg = ''
		if assetName:
			geoCacheRoot = workspace(q= 1, rd= 1) + workspace('moGeoCache', q= 1, fre= 1)
			geoCacheDir = geoCacheRoot + '/' + assetName
			if os.path.exists(geoCacheDir):
				result = fileDialog2(cap= 'geoCache Folder', fm= 3, okc= 'Select', dir= geoCacheDir)
				if result:
					folderName = os.path.basename(result[0])
					if os.path.exists(geoCacheDir + '/' + folderName):
						textField(textF_choose, e= 1, tx= folderName)
						text(txt_infoSceneName, e= 1, l= folderName)
					else:
						msg = 'This asset does not have this geoCache folder.'
			else:
				msg = 'Asset [ ' + assetName + ' ] does not exists in the moGeoCache folder.'
		else:
			msg = 'Select an Asset first.'
		if msg:
			confirmDialog(t= 'Warning', m= msg, b= ['Ok'], db= 'Ok', icn= 'warning')

	iconTextButton(icBtn_textF_choose, e= 1, c= openCacheFolder)


def ui_main():
	"""
	"""
	global windowName
	windowName = 'ms_GeoCache_uiMain'

	if window(windowName, q= 1, ex= 1):
		deleteUI(windowName)

	window(windowName, t= 'GeoCache Settings', s= 1, mxb= 0, mnb= 0)
	main_column = columnLayout(adj= 1)
	# geoCache
	ui_initPrep(50)
	ui_geoCache(90)
	setParent('..')

	scriptJob(e= ['SelectionChanged', ui_getAssetName], p= windowName)
	scriptJob(e= ['PostSceneRead', ui_getSceneName], p= windowName)
	scriptJob(e= ['SceneSaved', ui_getSceneName], p= windowName)
	scriptJob(e= ['PostSceneRead', ui_getSmoothExclusive], p= windowName)
	ui_getAssetName()
	ui_getSceneName()
	ui_getSmoothExclusive()

	#cmds.window('ms_GeoCache_uiMain', q= 1, h= 1)
	window(windowName, e= 1, h= 512, w= 270)
	showWindow(windowName)
