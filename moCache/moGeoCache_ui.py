# -*- coding:utf-8 -*-
'''
Created on 2016.07.06

@author: davidpower
'''
from pymel.core import *
from functools import partial
import moCache.moGeoCache as moGeoCache; reload(moGeoCache)



def exec_getParams(*args):

	global rbtn_geoIO
	global txt_infoAssetName
	global txt_infoSceneName
	global cBox_isPartial
	global cBox_isStatic
	global intF_division
	global cBox_dupName
	global textF_filter
	global rbtn_execBy
	
	conflictList = str(textField(textF_filter, q= 1, tx= 1))
	assetName_override = str(textField(textF_assetName, q= 1, tx= 1))
	paramDict = {
		'isPartial' : checkBox(cBox_isPartial, q= 1, v= 1),
		 'isStatic' : checkBox(cBox_isStatic, q= 1, v= 1),
		 'sameName' : checkBox(cBox_dupName, q= 1, v= 1),
		'assetName' : assetName_override if assetName_override else None,
		'sceneName' : str(text(txt_infoSceneName, q= 1, l= 1)),
		 'conflict' : [] if not conflictList else conflictList.split(';'),
		   'subdiv' : intFieldGrp(intF_division, q= 1, v1= 1)
	}

	if exec_checkParam(paramDict):
		mode = radioButtonGrp(rbtn_geoIO, q= 1, sl= 1)
		actionType = radioButtonGrp(rbtn_execBy, q= 1, sl= 1)
		if mode == 1:
			exec_Export(actionType, paramDict)
		if mode == 2:
			exec_Import(actionType, paramDict)


def exec_checkParam(paramDict):
	"""
	"""
	return True

	
def exec_Export(actionType, paramDict):
	"""
	"""
	if actionType == 1:
		print paramDict
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
	if actionType == 1:
		print paramDict
	if actionType == 2:
		pass
	if actionType == 3:
		moGeoCache.importGeoCache(
			sceneName= paramDict['sceneName'],
			isPartial= paramDict['isPartial'],
			assetName_override= paramDict['assetName'],
			ignorDuplicateName= paramDict['sameName'],
			conflictList= paramDict['conflict']
			)


def ui_getAssetName():
	"""
	"""
	if ls(sl= 1):
		if not textField(textF_assetName, q= 1, tx= 1):
			assetList = moGeoCache.getAssetList()
			text(txt_infoAssetName, e= 1, l= ', '.join(assetList))
		else:
			text(txt_infoAssetName, e= 1, l= textField(textF_assetName, q= 1, tx= 1))
	else:
		text(txt_infoAssetName, e= 1, l= '')


def ui_getSceneName():
	"""
	"""
	if not textField(textF_sceneName, q= 1, tx= 1):
		sname = system.sceneName().namebase
		text(txt_infoSceneName, e= 1, l= sname)


def ui_initPrep(sideValue):
	"""
	"""
	frameLayout(l= 'Ignition Preparation')
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
				btn_addWrapSet = button(l= 'Add Wrap Set')
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
			rowLayout(nc= 2, adj= 2, h= 20)
			if True:
				text(l= '', w= sideValue)
				cBox_inclusive = checkBox(l= 'Includsive')
				setParent('..')
			rowLayout(nc= 3, adj= 2)
			if True:
				text(l= '', w= sideValue)
				btn_makeSmoothSet = button(l= 'Make Smooth Set')
				text(l= '', w= sideValue)
				setParent('..')
			text(l= '', h= 5)
			rowLayout(nc= 3, adj= 2, h= 24)
			if True:
				text(l= '', w= sideValue)
				btn_makeCurvesSet = button(l= 'Make Curves Set')
				text(l= '', w= sideValue)
				setParent('..')
			setParent('..')

		columnLayout(adj= 1)
		if True:
			rowLayout(nc= 3, adj= 3, h= 30)
			if True:
				separator(h= 10, st= 'double', en= 0, w= 5)
				tex_cpa = text(l= 'Compare', al= 'center', fn= 'boldLabelFont', w= 50)
				separator(h= 10, st= 'double', en= 0)
				setParent('..')
			rowLayout(nc= 3, adj= 2, h= 36)
			if True:
				text(l= '', w= sideValue)
				btn_meshCompare = button(l= 'SHD - RIG\nMesh Compare', al= 'center', h= 32)
				text(l= '', w= sideValue)
				setParent('..')
			rowLayout(nc= 3, adj= 2, h= 24)
			if True:
				text(l= '', w= sideValue)
				tex_meshCompare = text(l= 'Result : ', al= 'left')
				text(l= '', w= sideValue)
				setParent('..')
			setParent('..')

		text(l= '', h= 5)

		setParent('..')
		setParent('..')


def ui_geoCache(midValue):
	"""
	"""
	global windowName
	global rbtn_geoIO
	global txt_infoAssetName
	global txt_infoSceneName
	global cBox_isPartial
	global cBox_isStatic
	global textF_assetName
	global intF_division
	global textF_sceneName
	global menu_choose
	global cBox_dupName
	global textF_filter
	global rbtn_execBy

	frameLayout(l= 'GeoCache I/O Controls')
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
			rowLayout(nc= 3, adj= 3, h= 22)
			if True:
				text(l= '( 0~4 ) ', al= 'right', en= 0, w= midValue)
				intF_division = intFieldGrp(l= '', v1= 0, ad2= 1, cw= [2, 36], w= 40, en= en)
				tex_division = text(l= 'Division Smooth', al= 'left', en= en)
				setParent('..')
			rowLayout(nc= 2, adj= 2)
			if True:
				txt_sceneName = text('Scene ', al= 'right', w= midValue, en= en)
				textF_sceneName = textField(pht= 'sceneName override', en= en)
				setParent('..')
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
			rowLayout(nc= 2, adj= 2)
			if True:
				txt_choose = text('Choose Scene ', al= 'right', w= midValue, en= en)
				menu_choose = optionMenu(l= '', en= en)
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

		columnLayout(adj= 1)
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
			button(l= 'Execute', h= 50, c= exec_getParams)
			setParent('..')

		setParent('..')
	setParent('..')

	# commands
	def intcmd_setMinMax(*args):
		global intF_division
		intvalue = intFieldGrp(intF_division, q= 1, v1= 1)
		if intvalue < 0:
			intFieldGrp(intF_division, e= 1, v1= 0)
		if intvalue > 4:
			intFieldGrp(intF_division, e= 1, v1= 4)

	intFieldGrp(intF_division, e= 1, cc= intcmd_setMinMax)

	def geoCacheIOctrlSwitch(col, vis, *args):
		layout(col, e= 1, vis= vis)
		if col == col_exp and vis:
			checkBox(cBox_isPartial, e= 1, l= 'Partial Export')
			#window(windowName, e= 1, h= 604)
		if col == col_imp and vis:
			checkBox(cBox_isPartial, e= 1, l= 'Partial Import')
			#window(windowName, e= 1, h= 623)

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

	geoCacheRoot = workspace(q= 1, rd= 1) + workspace('moGeoCache', q= 1, fre= 1)


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
	ui_geoCache(100)
	setParent('..')

	scriptJob(e= ['SelectionChanged', ui_getAssetName], p= windowName)
	scriptJob(e= ['PostSceneRead', ui_getSceneName], p= windowName)
	ui_getAssetName()
	ui_getSceneName()

	#cmds.window('ms_GeoCache_uiMain', q= 1, h= 1)
	window(windowName, e= 1, h= 604, w= 254)
	showWindow(windowName)
