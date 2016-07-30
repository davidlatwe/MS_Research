'''
build a simple off-axis stereo camera rig, based on vray env
for Maya 2016
'''

import maya.cmds as cmds
import maya.mel as mel
import maya.app.stereo.stereoCameraRig

# load vray and make it as currentRenderer
if not cmds.pluginInfo('vrayformaya', q= 1, loaded= 1):
    cmds.loadPlugin('vrayformaya')
cmds.setAttr('defaultRenderGlobals.currentRenderer', 'vray', type= 'string')

targetCamera = ''
targetZeroPn = ''
autoParent = 0

if len(cmds.ls(sl= 1, hd= 2)) >= 1:
	targetCamera = cmds.ls(sl= 1, hd= 2)[0]
	try:
		targetZeroPn = cmds.ls(sl= 1, hd= 2)[1]
	except:
		pass
	autoParent = 1
else:
	pass

# build vray stereo camera rig and do some basic stereo setup
myStereoCamRig = maya.app.stereo.stereoCameraRig.createStereoCameraRig(rigName= 'StereoCamera')
myStereoCamCenterShape = cmds.listRelatives(myStereoCamRig[0], s= 1, f= 1)[0]
cmds.setAttr(myStereoCamCenterShape + '.stereo', 2)
mel.eval('vray addAttributesFromGroup "' + myStereoCamCenterShape + '" vray_cameraStereoscopic 1')
cmds.setAttr(myStereoCamCenterShape + '.vrayCameraStereoscopicOn', 1)
cmds.setAttr(myStereoCamCenterShape + '.vrayCameraStereoscopicAdjustResolution', 1)


# make locators and group
myZeroPoint_invert = cmds.group(em= 1)
myZeroPoint_offset = cmds.group(em= 1)
myZeroPoint_loc = cmds.spaceLocator()[0]
myZeroPoint_handle = cmds.spaceLocator()[0]


# assembling rigs
cmds.parent(myZeroPoint_invert, myStereoCamRig[0])
cmds.parent(myZeroPoint_loc, myZeroPoint_invert)
cmds.parent(myZeroPoint_handle, myZeroPoint_offset)
cmds.pointConstraint(myZeroPoint_handle, myZeroPoint_loc, mo= 0)
cmds.setAttr(myZeroPoint_invert + '.ry', 180)
cmds.setAttr(myZeroPoint_loc + '.v', 0)
cmds.connectAttr(myZeroPoint_loc + '.tz', myStereoCamCenterShape + '.zeroParallax')

# connect some useful attrs
cmds.addAttr(myZeroPoint_handle, ln= 'zeroParallaxPlane', at= 'bool', k= 1)
cmds.connectAttr(myZeroPoint_handle + '.zeroParallaxPlane', myStereoCamCenterShape + '.zpp')

cmds.addAttr(myZeroPoint_handle, ln= 'FocalLength', at= 'float', min= 2.5, k= 1)
cmds.connectAttr(myZeroPoint_handle + '.FocalLength', myStereoCamCenterShape + '.focalLength')

cmds.addAttr(myZeroPoint_handle, ln= 'InteraxialSeparation', at= 'float', min= 0, k= 1)
cmds.connectAttr(myZeroPoint_handle + '.InteraxialSeparation', myStereoCamCenterShape + '.interaxialSeparation')

cmds.addAttr(myZeroPoint_handle, ln= 'CameraLocScale', at= 'float', min= 0.001, k= 1)
cmds.connectAttr(myZeroPoint_handle + '.CameraLocScale', myStereoCamCenterShape + '.lls')
cmds.connectAttr(myZeroPoint_handle + '.CameraLocScale', cmds.listRelatives(myStereoCamRig[1], s= 1, f= 1)[0] + '.lls')
cmds.connectAttr(myZeroPoint_handle + '.CameraLocScale', cmds.listRelatives(myStereoCamRig[2], s= 1, f= 1)[0] + '.lls')


# setup default
cmds.setAttr(myZeroPoint_handle + '.zeroParallaxPlane', 1)
cmds.setAttr(myZeroPoint_handle + '.FocalLength', 16)
cmds.setAttr(myZeroPoint_handle + '.InteraxialSeparation', 6.35)
cmds.setAttr(myZeroPoint_handle + '.CameraLocScale', 1)
cmds.setAttr(myZeroPoint_handle + '.tz', -10)
cmds.select(myZeroPoint_handle, r= 1)


# hide or lock unused attr
def attrLocknHide(atName, at):
	cmds.setAttr(atName + '.' + at + 'x', k= 0)
	cmds.setAttr(atName + '.' + at + 'y', k= 0)
	cmds.setAttr(atName + '.' + at + 'z', k= 0)
	cmds.setAttr(atName + '.' + at, l= 1)

attrLocknHide(myZeroPoint_handle, 'r')
attrLocknHide(myStereoCamRig[0], 's')
attrLocknHide(myZeroPoint_loc, 't')
attrLocknHide(myZeroPoint_loc, 'r')
attrLocknHide(myZeroPoint_loc, 's')
attrLocknHide(myZeroPoint_invert, 't')
attrLocknHide(myZeroPoint_invert, 'r')
attrLocknHide(myZeroPoint_invert, 's')


if autoParent:
	fail = []
	try:
		cmds.parentConstraint(targetCamera, myStereoCamRig[0], mo= 0)
	except:
		fail.append('Camera -> ' + targetCamera)
	try:
		cmds.parentConstraint(targetZeroPn, myZeroPoint_offset, mo= 0)
	except:
		fail.append('ZeroPoint -> ' + targetZeroPn)
	if fail:
		cmds.warning('Fail to auto parent: ' + str(fail))


# rename rigs
cmds.rename(myZeroPoint_invert,'zeroPoint_invert')
cmds.rename(myZeroPoint_loc,'zeroPoint_loc')
cmds.rename(myZeroPoint_offset,'zeroPoint_offset')
cmds.rename(myZeroPoint_handle,'zeroPoint_handle')