import vray.utils as vrUtils
import re





def vrre_coverage():
	"""
	Coverage
	"""
	vrre = vrUtils.create('RenderChannelCoverage', 'vrayRE_Coverage')
	vrre.set('name', 'coverage')


def vrre_drBucket():
	"""
	DR_Bucket
	"""
	vrre = vrUtils.create('RenderChannelDRBucket', 'vrayRE_DR_Bucket')
	vrre.set('name', 'DR')
	vrre.set('text_alignment', 0)


def vrre_objectSelect():
	"""
	Object_select
	"""
	vrre = vrUtils.create('RenderChannelObjectSelect', 'vrayRE_Object_select')
	vrre.set('name', 'objectSelect')
	vrre.set('id', 0)
	vrre.set('use_mtl_id', 0)
	vrre.set('affect_matte_objects', 1)
	vrre.set('consider_for_aa', 0)
	vrre.set('invert_selection', 0)


def vrre_renderID():
	"""
	Render_ID
	"""
	vrre = vrUtils.create('RenderChannelRenderID', 'vrayRE_Render_ID')
	vrre.set('name', 'renderId')


def vrre_objectID():
	"""
	Object_ID
	"""
	vrre = vrUtils.create('RenderChannelNodeID', 'vrayRE_Object_ID')
	vrre.set('name', 'objectId')


def vrre_multiMatte():
	"""
	Multi_Matte
	"""
	vrre = vrUtils.create('RenderChannelMultiMatte', 'vrayRE_Multi_Matte')
	vrre.set('name', 'multimatte')
	vrre.set('consider_for_aa', 1)
	vrre.set('affect_matte_objects', 1)
	vrre.set('texmap', vrUtils.AColor(0, 0, 0, 1))
	vrre.set('filtering', 1)
	vrre.set('exclude_list_as_inclusive_set', 0)


def vrre_normals():
	"""
	Normals
	"""
	vrre = vrUtils.create('RenderChannelNormals', 'vrayRE_Normals')
	vrre.set('name', 'normals')
	vrre.set('filtering', 1)


def vrre_bumpNormals():
	"""
	Bump Normals
	"""
	vrre = vrUtils.create('RenderChannelBumpNormals', 'vrayRE_BumpNormals')
	vrre.set('name', 'bumpnormals')
	vrre.set('filtering', 1)


def vrre_velocity():
	"""
	Velocity
	"""
	vrre = vrUtils.create('RenderChannelVelocity', 'vrayRE_Velocity')
	vrre.set('name', 'velocity')
	vrre.set('clamp_velocity', 0)
	vrre.set('max_velocity', 1)
	vrre.set('max_velocity_last_frame', 5)
	vrre.set('ignore_z', 1)
	vrre.set('filtering', 1)


def vrre_zDepth():
	"""
	Z_depth
	"""
	vrre = vrUtils.create('RenderChannelZDepth', 'vrayRE_Z_depth')
	vrre.set('name', 'zDepth')
	vrre.set('depth_from_camera', 0)
	vrre.set('depth_black', 0)
	vrre.set('depth_white', 1000)
	vrre.set('depth_clamp', 1)
	vrre.set('filtering', 1)


def vrre_extraTex():
	"""
	Extra_Tex
	"""
	vrre = vrUtils.create('RenderChannelExtraTex', 'vrayRE_Extra_Tex')
	vrre.set('name', 'extraTex')
	vrre.set('texmap', vrUtils.AColor(0, 0, 0, 1))
	vrre.set('filtering', 1)
	vrre.set('exclude_list', None)
	vrre.set('exclude_list_as_inclusive_set', None)
	vrre.set('affect_matte_objects', 1)
	vrre.set('consider_for_aa', 1)


def vrre_color(name, alias, mapping= None, aa= None, filtering= None, derive= None):
	"""
	Color Channel
	"""
	vrre = vrUtils.create('RenderChannelColor', name)
	vrre.set('name', name)
	vrre.set('alias', alias)
	vrre.set('color_mapping', mapping)
	vrre.set('consider_for_aa', aa)
	vrre.set('filtering', filtering)
	vrre.set('derive_raw_channels', derive)


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


def vrre_getDefault(elementType, elementName):
	vrUtils.create(elementType, elementName)
	pv = vrUtils.getPluginParams(elementName, getValues= True)
	for p in pv.keys():
		mel.warning(p + ' = ' + str(pv[p]))