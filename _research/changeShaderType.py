"""
@source: C:\Program Files\Autodesk\Maya2016\scripts\AETemplates\AEshaderTypeNew.mel
@source func: AEshaderTypeCB
"""
from pymel.core import *


def getMaterialInfo(shaderNode):
	connections = listConnections(shaderNode + '.message')
	for item in connections:
		if objectType(item) == 'materialInfo':
			return item
	return ''


def disconnectMaterialInfo(shaderNode, newShaderNode):
	materialInfoNode = getMaterialInfo(shaderNode)
	if materialInfoNode == '':
		# The materialInfoNode doesn't exist... fail silently.
		return
	disconnectAttr(shaderNode + '.message', materialInfoNode + '.material')


for shaderNode in ls(sl= 1, typ= 'lambert'):
	if shaderNode != 'lambert1':
		replaceType = 'VRayMtl'
		replaceNode = createNode(replaceType)
		# Disconnect the materialInfo node.
		disconnectMaterialInfo(shaderNode, replaceNode)		
		mel.replaceNode(shaderNode, replaceNode)
		delete(shaderNode)
