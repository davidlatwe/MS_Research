# -*- coding:utf-8 -*-
'''
Created on 2016.05.10

@author: davidpower
'''
import maya.cmds as cmds
import maya.mel as mel


componentList = cmds.filterExpand(sm= [31, 32, 34])
if componentList:
    for component in componentList:
        cmds.spaceLocator(n= component + 'loc')
        grpName = cmds.group(n= component + 'grp')
        cmds.select(component, r= 1)
        cmds.select(grpName, add= 1)
        mel.eval('doCreatePointOnPolyConstraintArgList 2 {"0", "0", "0", "1", "", "1", "0", "0", "0", "0"}')
else:
    cmds.warning('select one or more vertex, edge or face')