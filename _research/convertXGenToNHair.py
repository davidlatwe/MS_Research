# -*- coding:utf-8 -*-
'''
Created on 2016.06.06

@author: davidpower
'''
import logging
logger = logging.getLogger('MayaOil.moTools')

from pymel.core import *

# get selected xgen descriptions and patch geo
xgmDescList = [dag for dag in ls(sl= 1) if dag.getShape().type() == 'xgmDescription' ]
xgmPoly = [dag for dag in ls(sl= 1) if dag.getShape().type() == 'mesh' ][0]

# remove xgGroom group
if objExists('xgGroom'):
	delete('xgGroom')

for xgmDesc in xgmDescList:
	# vars
	nucleus = xgmDesc + '_nucleus'
	hairSys = xgmDesc + '_hairSys'

	# create curves from xgen guides
	select(xgmDesc, r= 1)
	curveList = mel.eval('xgmCreateCurvesFromGuides 2 0')

	# create nucleus
	rename(mel.eval('createNSystem'), nucleus)
	mel.eval('setActiveNucleusNode("' + nucleus + '")')

	# create hairSystem
	hairSysShape = createNode('hairSystem')
	rename(hairSysShape.getParent(), hairSys)
	# hairSystem init
	removeMultiInstance(hairSysShape + '.stiffnessScale[1]', b= 1)
	hairSysShape.clumpWidth.set(0.00001)
	hairSysShape.hairsPerClump.set(1)
	connectAttr('time1.outTime', hairSysShape + '.currentTime')
	mel.eval('addActiveToNSystem("' + hairSysShape + '", "' + nucleus + '")')
	connectAttr(nucleus + '.startFrame', hairSysShape + '.startFrame')

	# make dynamic
	select([curveList, xgmPoly, hairSys], r= 1)
	mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')


# xgGroom hide and rename
SCENE.xgGroom.v.set(0)
SCENE.xgGroom.rename('nHairGroom')
