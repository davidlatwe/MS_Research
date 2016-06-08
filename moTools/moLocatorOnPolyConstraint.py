# -*- coding:utf-8 -*-
'''
Created on 2016.05.10

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel
import maya.app.general.pointOnPolyConstraint as ppc


def locatorPPC():
	"""
	sourceFile: doCreatePointOnPolyConstraintArgList.mel
	sourcePath: C:\Program Files\Autodesk\Maya2015\scripts\others
	
	[note 1] # mel.eval('doCreatePointOnPolyConstraintArgList 2 {"0", "0", "0", "1", "", "1", "0", "0", "0", "0"}')
	[note 1] # eval 上面指令，會在某些狀況出錯，像當目標為 rigidBody 時，會因為 pycmd 抓到 shapeName 而產生
	[note 1] # " // Error: line 0: setAttr: No object matches name: " 這樣的錯誤
	[note 1] # 因此將指令依照 sourceFile 拆解如下
	
	"""
	def evalPPC(pycmd):
		# doCreatePointOnPolyConstraint
		cmd = '{string $constraint[]=`pointOnPolyConstraint -offset 0 0 0  -weight 1`' + pycmd + ';}'
		mel.eval(cmd)

	componentList = cmds.filterExpand(sm= [31, 32, 34])
	if componentList:
		for component in componentList:
			cmds.spaceLocator(n= component + 'loc')
			grpName = cmds.group(n= component + 'grp')
			cmds.select(component, r= 1)
			cmds.select(grpName, add= 1)
			# [note 1] start
			# make cmd
			pycmd = ppc.assembleCmd()
			try:
				evalPPC(pycmd)
			except:
				cmds.warning('Error occurred during operation. This is Plan B trying.')
				wrongName = pycmd.split('"')[1][1:-2]
				shapeName = component.split('.')[0]
				transName = cmds.listRelatives(shapeName, p= 1)[0].split(':')[-1]
				pycmd = pycmd.replace(wrongName, transName)
				evalPPC(pycmd)
			# [note 1] end
	else:
		cmds.warning('select one or more vertex, edge or face')


locatorPPC()