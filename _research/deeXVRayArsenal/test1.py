import vray.utils as vrUtils
import re


def vrre_rgbMatte(renderLayer, matteName, matteMembers):
	"""
	RGB Matte
	"""
	extName = 'objID_' + matteName
	uctName = '_'.join(['uct', renderLayer, matteName])
	varName = '_'.join(['var', renderLayer, matteName])
	# userColorTex
	userColorTex = vrUtils.create('TexUserColor', uctName)
	userColorTex.set('default_color', vrUtils.AColor(0, 0, 0, 1))
	userColorTex.set('user_attribute', varName)
	# extraTex
	re_extraTex = vrUtils.create('RenderChannelExtraTex', extName)
	re_extraTex.set('name', extName)
	re_extraTex.set('consider_for_aa', 1)
	re_extraTex.set('affect_matte_objects', 1)
	re_extraTex.set('texmap', userColorTex)
	re_extraTex.set('filtering', 1)
	# assign channel
	chValue = {'R':'1, 0, 0', 'G':'0, 1, 0', 'B':'0, 0, 1'}
	for ch in matteMembers.keys():
		for dag in matteMembers[ch]:
			node = vrUtils.findByName(dag + '@node')[0]
			oldValue = node.get('user_attributes')
			newValue = varName + '=' + chValue[ch] + ';' + oldValue
			# check if this node also in other channel
			if varName in oldValue:
				r = re.search(varName + '(.+?);', oldValue)
				if r:
					# add channel, and replace old userAttr
					a = eval(chValue[ch])
					b = eval(r.group(1)[1:])
					addValue = str([a[i] + b[i] for i in range(len(a))])[1:-1]
					ovList = oldValue.split(';')
					ovid = ovList.index(varName + r.group(1))
					ovList[ovid] = varName + '=' + addValue
					newValue = ';'.join(ovList)
			node.set('user_attributes', newValue)


vrre_rgbMatte('defaultrenderLayer', 'pCylinder1', {'R':['pCylinderShape1']})
vrre_rgbMatte('defaultrenderLayer', 'pCube1', {'R':['pCubeShape1']})
vrre_rgbMatte('defaultrenderLayer', 'pTorus1', {'R':['pTorusShape1']})
vrre_rgbMatte('defaultrenderLayer', 'group1', {'R':['pCylinderShape1', 'pCubeShape1', 'pTorusShape1']})