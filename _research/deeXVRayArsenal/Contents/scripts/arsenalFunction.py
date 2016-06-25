import vray.utils as vrUtils
import os
import pymel.all as pm
import maya.OpenMaya as OpenMaya
import arsenalToolBox

class ArsenalFunctionObjectsProperties(object):

	def __init__(self, parent = None):
		self.blackHoleMembers = False
		self.blackHoleMembersReceiveShd = False
		self.giMembersGenerate = False
		self.giMembersReceive = False
		self.primaryMembersOff = False
		self.reflectionMembersOff = False
		self.refractionMembersOff = False
		self.shadowCastsMembersOff = False




class ArsenalFunction(object):

	def __init__(self, parent = None):
		self.parent = parent
		self.dir = str(os.path.abspath(os.path.dirname(__file__))) + '/'
		self.vrsceneMaterialDir = self.dir + 'vrscenes/materials/'



	def getAllChildShapes(self, selection = [], type = None):
		allShapes = []
		go = True
		while go:
			allChilds = []
			tmpNode = selection
			for tmp in tmpNode:
				if pm.objectType(tmp) in type:
					allShapes.append(tmp)
				allChilds += tmp.getChildren()

			selection = allChilds
			for mySel in selection:
				if pm.objectType(mySel) in type:
					allShapes.append(mySel)

			if not selection:
				go = False

		return list(set(allShapes))



	def deeXLightSelectGeneratorFunc(self, lightNormal = list(), lightDiffuse = list(), lightRaw = list(), lightSpecular = list()):
		for myLight in lightNormal:
			name = 'lightSelect_' + myLight.name().replace('|', '_').replace(':', '_') + '_normal'
			vrUtils.create('RenderChannelColor', name)
			lightSelect = vrUtils.findByName(name)
			lightSelect[0].set('name', name)
			lightSelect[0].set('consider_for_aa', 1)
			myLight.set('channels', [lightSelect[0]])

		for myLight in lightRaw:
			name = 'lightSelect_' + myLight.name().replace('|', '_').replace(':', '_') + '_raw'
			vrUtils.create('RenderChannelColor', name)
			lightSelect = vrUtils.findByName(name)
			lightSelect[0].set('name', name)
			lightSelect[0].set('consider_for_aa', 1)
			myLight.set('channels_raw', [lightSelect[0]])

		for myLight in lightDiffuse:
			name = 'lightSelect_' + myLight.name().replace('|', '_').replace(':', '_') + '_diffuse'
			vrUtils.create('RenderChannelColor', name)
			lightSelect = vrUtils.findByName(name)
			lightSelect[0].set('name', name)
			lightSelect[0].set('consider_for_aa', 1)
			myLight.set('channels_diffuse', [lightSelect[0]])

		for myLight in lightSpecular:
			name = 'lightSelect_' + myLight.name().replace('|', '_').replace(':', '_') + '_spec'
			vrUtils.create('RenderChannelColor', name)
			lightSelect = vrUtils.findByName(name)
			lightSelect[0].set('name', name)
			lightSelect[0].set('consider_for_aa', 1)
			myLight.set('channels_specular', [lightSelect[0]])




	def deeXProxyObjectIDGeneratorFunc(self):
		OpenMaya.MGlobal.displayInfo('[Arsenal] Proxy ObjectID Generator start')
		proxyNode = pm.ls(type='VRayMesh')
		for myProxy in proxyNode:
			mesh = myProxy.listHistory(future=True, exactType='mesh')
			allParent = mesh[0].listRelatives(ap=True, pa=True)
			go = False
			for myP in allParent:
				if myP.isVisible():
					print myProxy.name() + ' is visible.'
					go = True
					break

			if not go:
				continue
			OpenMaya.MGlobal.displayInfo('              Generate ID for proxy : ' + myProxy.name())
			idList = myProxy.objectListIDs.get()
			if len(idList) <= 1:
				continue
			count = 0
			maskNumber = 0
			for myID in idList:
				if myID != 0.0:
					multiMatteName = str('MultiMatte_%04d' % maskNumber + '_%010d' % myID)
					if count % 3 == 0:
						n2 = 'None'
						if len(idList) - 1 >= count + 2 and idList[(count + 2)] != 0.0:
							n2 = idList[(count + 2)]
						n1 = 'None'
						if len(idList) - 1 >= count + 1 and idList[(count + 1)] != 0.0:
							n1 = idList[(count + 1)]
						n = 'None'
						if len(idList) - 1 >= count and idList[count] != 0.0:
							n = idList[count]
						OpenMaya.MGlobal.displayInfo('                - Create multimatte : ' + multiMatteName + ' with ID : ' + str(n) + ' - ' + str(n1) + ' - ' + str(n2) + ' from ' + str(idList))
						vrUtils.create('RenderChannelMultiMatte', multiMatteName)
						myMask = vrUtils.findByName(multiMatteName)
						myMask[0].set('name', str(multiMatteName))
						if len(idList) - 1 >= count + 2 and idList[(count + 2)] != 0.0:
							myMask[0].set('red_id', idList[(count + 2)])
						if len(idList) - 1 >= count + 1 and idList[(count + 1)] != 0.0:
							myMask[0].set('green_id', idList[(count + 1)])
						if len(idList) - 1 >= count and idList[count] != 0.0:
							myMask[0].set('blue_id', idList[count])
						myMask[0].set('use_mtl_id', 0)
						myMask[0].set('affect_matte_objects', 1)
						myMask[0].set('consider_for_aa', 1)
						maskNumber += 1
					count += 1





	def deeXMaterialIDGeneratorFunc(self):
		allMaterial = vrUtils.findByType('MtlSingleBRDF')
		allBumpMaterial = vrUtils.findByType('MtlBump')
		allBaseMtlFromBump = list()
		allDuplicated = list()
		for eachBumpMtl in allBumpMaterial:
			allBaseMtlFromBump.append(eachBumpMtl.get('base_mtl'))

		generalCount = 0
		OpenMaya.MGlobal.displayInfo('[Arsenal] MaterialID Generator start')
		OpenMaya.MGlobal.displayInfo('START PASS 01')
		for eachMtl in allMaterial:
			eachBlend = eachMtl.get('brdf')
			if 'brdfs' in eachBlend.params():
				listmtl = eachBlend.get('brdfs')
				listWeight = eachBlend.get('weights')
				if listWeight:
					listWeight.pop(len(listWeight) - 1)
					listMtlID = list()
					duplicatedList = list()
					for (i, eachVRayMtl,) in enumerate(listmtl):
						nameDuplicated = eachVRayMtl.name() + '_' + eachMtl.name() + '_deeXDuplicated_' + str(0)
						if nameDuplicated not in duplicatedList:
							duplicatedList.append(nameDuplicated)
							duplicatedMtl = eachVRayMtl.duplicate(nameDuplicated)
							allDuplicated.append(duplicatedMtl)
							mtlID = vrUtils.create('MtlMaterialID', duplicatedMtl.name() + '_MtlMaterialID')
							listMtlID.append(mtlID)
							mtlID.set('base_mtl', duplicatedMtl)
							(multimatteID, rgb,) = arsenalToolBox.arsenal_generateNumberFromString(string=eachVRayMtl.name())
							mtlID.set('material_id_number', multimatteID)
							OpenMaya.MGlobal.displayInfo('                RGB for ' + nameDuplicated + ' : ' + str(rgb) + '    MaterialMultimatteID = ' + str(multimatteID))
							if i == len(listmtl) - 1:
								textLayered = vrUtils.create('TexLayered', duplicatedMtl.name() + '_layered')
								textLayered.set('alpha_from_intensity', 0)
								blendMode = list()
								listTexLayer = list()
								for blendCount in range(len(listWeight) + 1):
									if blendCount == 0:
										blendMode.append(1)
										firstTextColor = vrUtils.create('TexAColorOp', duplicatedMtl.name() + '_firstText')
										firstTextColor.set('color_a', vrUtils.AColor(rgb[0], rgb[1], rgb[2], 1))
										listTexLayer.append(firstTextColor)
									else:
										blendMode.append(5)
										clamper = vrUtils.create('TexClamp', duplicatedMtl.name() + listWeight[(blendCount - 1)].name() + '_clamper')
										clamper.set('texture', listWeight[(blendCount - 1)])
										clamper.set('min_color', vrUtils.AColor(0, 0, 0, 0))
										clamper.set('max_color', vrUtils.AColor(1, 1, 1, 1))
										listTexLayer.append(clamper)

								textLayered.set('blend_modes', blendMode)
								textLayered.set('textures', listTexLayer)
								clamper = vrUtils.create('TexClamp', duplicatedMtl.name() + '_clamper')
								clamper.set('texture', textLayered)
								clamper.set('min_color', vrUtils.AColor(0, 0, 0, 0))
								clamper.set('max_color', vrUtils.AColor(1, 1, 1, 1))
								textToConnect = clamper
							else:
								multiplyMaya = vrUtils.create('MayaMultiplyDivide', duplicatedMtl.name() + '_multiply')
								multiplyMaya.set('color1', vrUtils.AColor(rgb[0], rgb[1], rgb[2], 1))
								multiplyMaya.set('color2', listWeight[i])
								multiplyMaya.set('operation', 1)
								clamper = vrUtils.create('TexClamp', duplicatedMtl.name() + '_clamper')
								clamper.set('texture', multiplyMaya)
								clamper.set('min_color', vrUtils.AColor(0, 0, 0, 1))
								clamper.set('max_color', vrUtils.AColor(1, 1, 1, 1))
							textToConnect = clamper
						else:
							duplicatedMtl = vrUtils.findByName(nameDuplicated)[0]
							textToConnect = vrUtils.findByName(duplicatedMtl.name() + '_clamper')[0]
						mtlID.set('material_id_color', textToConnect)

					eachBlend.set('brdfs', listMtlID)
				else:
					nameDuplicated = eachBlend.name() + '_deeXDuplicated'
					duplicatedMtl = eachBlend.duplicate(nameDuplicated)
					allDuplicated.append(duplicatedMtl)
					(multimatteID, rgb,) = arsenalToolBox.arsenal_generateNumberFromString(string=eachBlend.name())
					OpenMaya.MGlobal.displayInfo('                RGB for ' + duplicatedMtl.name() + ' : ' + str(rgb) + '    MaterialMultimatteID = ' + str(multimatteID))
					mtlID = vrUtils.create('MtlMaterialID', duplicatedMtl.name() + '_MtlMaterialID')
					mtlID.set('base_mtl', duplicatedMtl)
					mtlID.set('material_id_color', vrUtils.AColor(rgb[0], rgb[1], rgb[2], 1))
					mtlID.set('material_id_number', multimatteID)
					eachMtl.set('brdf', mtlID)
			elif eachMtl in allBaseMtlFromBump:
				OpenMaya.MGlobal.displayInfo('                ' + eachMtl.name() + ' in a bumpMtl, exclude')
				continue
			nameDuplicated = eachBlend.name() + '_deeXDuplicated_' + str(generalCount)
			duplicatedMtl = eachBlend.duplicate(nameDuplicated)
			allDuplicated.append(duplicatedMtl)
			(multimatteID, rgb,) = arsenalToolBox.arsenal_generateNumberFromString(string=eachBlend.name())
			OpenMaya.MGlobal.displayInfo('                RGB for ' + duplicatedMtl.name() + ' : ' + str(rgb) + '    MaterialMultimatteID = ' + str(multimatteID))
			mtlID = vrUtils.create('MtlMaterialID', duplicatedMtl.name() + '_MtlMaterialID')
			mtlID.set('base_mtl', duplicatedMtl)
			mtlID.set('material_id_color', vrUtils.AColor(rgb[0], rgb[1], rgb[2], 1))
			mtlID.set('material_id_number', multimatteID)
			eachMtl.set('brdf', mtlID)
			generalCount += 1

		OpenMaya.MGlobal.displayInfo('START PASS 02')
		allBumpMaterial = vrUtils.findByType('MtlBump')
		for (i, eachBumpMtl,) in enumerate(allBumpMaterial):
			if eachBumpMtl in allDuplicated:
				OpenMaya.MGlobal.displayInfo('                ' + eachBumpMtl.name() + ' is from a duplicated shader, do nothing')
				continue
			baseMtl = eachBumpMtl.get('base_mtl')
			if 'brdf' not in baseMtl.params():
				continue
			eachSimple = baseMtl.get('brdf')
			if 'brdfs' in eachSimple.params():
				OpenMaya.MGlobal.displayInfo('                ' + eachSimple.name() + ' is from a blend shader, do nothing')
				continue
			nameDuplicated = eachSimple.name() + '_deeXDuplicated'
			if vrUtils.findByName(nameDuplicated):
				continue
			duplicatedMtl = eachSimple.duplicate(nameDuplicated)
			allDuplicated.append(duplicatedMtl)
			(multimatteID, rgb,) = arsenalToolBox.arsenal_generateNumberFromString(string=eachSimple.name())
			OpenMaya.MGlobal.displayInfo('                RGB for ' + eachSimple.name() + ' : ' + str(rgb) + '    MaterialMultimatteID = ' + str(multimatteID))
			mtlID = vrUtils.create('MtlMaterialID', duplicatedMtl.name() + '_MtlMaterialID')
			mtlID.set('base_mtl', duplicatedMtl)
			mtlID.set('material_id_color', vrUtils.AColor(rgb[0], rgb[1], rgb[2], 1))
			mtlID.set('material_id_number', multimatteID)
			eachBumpMtl.set('base_mtl', mtlID)

		OpenMaya.MGlobal.displayInfo('START PASS 03')
		allMaterial = vrUtils.findByType('MtlSingleBRDF')
		for (i, eachMtl,) in enumerate(allMaterial):
			if eachMtl in allDuplicated:
				OpenMaya.MGlobal.displayInfo('                ' + eachMtl.name() + ' is from a duplicated shader, do nothing')
				continue
			eachSimple = eachMtl.get('brdf')
			if 'brdfs' in eachSimple.params():
				OpenMaya.MGlobal.displayInfo('                ' + eachSimple.name() + ' is from a blend shader, do nothing')
				continue
			if eachSimple.type() == 'MtlMaterialID':
				OpenMaya.MGlobal.displayInfo('                ' + eachSimple.name() + ' is already a MtlMaterialID, do nothing')
				continue
			nameDuplicated = eachSimple.name() + '_deeXDuplicated'
			if vrUtils.findByName(nameDuplicated):
				continue
			duplicatedMtl = eachSimple.duplicate(nameDuplicated)
			allDuplicated.append(duplicatedMtl)
			(multimatteID, rgb,) = arsenalToolBox.arsenal_generateNumberFromString(string=eachSimple.name())
			OpenMaya.MGlobal.displayInfo('                RGB for ' + eachSimple.name() + ' : ' + str(rgb) + '    MaterialMultimatteID = ' + str(multimatteID))
			mtlID = vrUtils.create('MtlMaterialID', duplicatedMtl.name() + '_MtlMaterialID')
			mtlID.set('base_mtl', duplicatedMtl)
			mtlID.set('material_id_color', vrUtils.AColor(rgb[0], rgb[1], rgb[2], 1))
			mtlID.set('material_id_number', multimatteID)
			eachMtl.set('brdf', mtlID)

		OpenMaya.MGlobal.displayInfo('[Arsenal] MaterialID Generator end')



	def start(self, renderPass = None, blackHoleMembers = list(), blackHoleMembersReceiveShd = list(), giMembersGenerate = list(), giMembersReceive = list(), primaryMembersOff = list(), reflectionMembersOff = list(), refractionMembersOff = list(), shadowCastsMembersOff = list(), lightSelectNormalMembers = list(), lightSelectDiffuseMembers = list(), lightSelectRawMembers = list(), lightSelectSpecularMembers = list()):
		if renderPass is None:
			renderPass = pm.editRenderLayerGlobals(query=True, currentRenderLayer=True)
		arsenalPassName = str(renderPass) + '_arsenalPass'
		if not pm.objExists(arsenalPassName):
			OpenMaya.MGlobal.displayError('[Arsenal] ' + arsenalPassName + ' not found.')
			return 
		if not blackHoleMembers:
			myConnected = pm.listConnections(arsenalPassName + '.blackHoleMembers', destination=False, source=True)
			for dag in self.getAllChildShapes(selection=myConnected, type=['mesh', 'VRayPlane']):
				if not dag.intermediateObject.get():
					blackHoleMembers.append(dag)

		if not blackHoleMembersReceiveShd:
			myConnected = pm.listConnections(arsenalPassName + '.blackHoleMembersReceiveShd', destination=False, source=True)
			for dag in self.getAllChildShapes(selection=myConnected, type=['mesh', 'VRayPlane']):
				if not dag.intermediateObject.get():
					blackHoleMembersReceiveShd.append(dag)

		if not giMembersGenerate:
			myConnected = pm.listConnections(arsenalPassName + '.giMembersGenerate', destination=False, source=True)
			for dag in self.getAllChildShapes(selection=myConnected, type=['mesh', 'VRayPlane']):
				if not dag.intermediateObject.get():
					giMembersGenerate.append(dag)

		if not giMembersReceive:
			myConnected = pm.listConnections(arsenalPassName + '.giMembersReceive', destination=False, source=True)
			for dag in self.getAllChildShapes(selection=myConnected, type=['mesh', 'VRayPlane']):
				if not dag.intermediateObject.get():
					giMembersReceive.append(dag)

		if not primaryMembersOff:
			myConnected = pm.listConnections(arsenalPassName + '.primaryMembersOff', destination=False, source=True)
			for dag in self.getAllChildShapes(selection=myConnected, type=['mesh', 'VRayPlane']):
				if not dag.intermediateObject.get():
					primaryMembersOff.append(dag)

		if not reflectionMembersOff:
			myConnected = pm.listConnections(arsenalPassName + '.reflectionMembersOff', destination=False, source=True)
			for dag in self.getAllChildShapes(selection=myConnected, type=['mesh', 'VRayPlane']):
				if not dag.intermediateObject.get():
					reflectionMembersOff.append(dag)

		if not refractionMembersOff:
			myConnected = pm.listConnections(arsenalPassName + '.refractionMembersOff', destination=False, source=True)
			for dag in self.getAllChildShapes(selection=myConnected, type=['mesh', 'VRayPlane']):
				if not dag.intermediateObject.get():
					refractionMembersOff.append(dag)

		if not shadowCastsMembersOff:
			myConnected = pm.listConnections(arsenalPassName + '.shadowCastsMembersOff', destination=False, source=True)
			for dag in self.getAllChildShapes(selection=myConnected, type=['mesh', 'VRayPlane']):
				if not dag.intermediateObject.get():
					shadowCastsMembersOff.append(dag)

		allGroups = {}
		allGroups['blackHoleMembers'] = blackHoleMembers
		allGroups['blackHoleMembersReceiveShd'] = blackHoleMembersReceiveShd
		allGroups['giMembersGenerate'] = giMembersGenerate
		allGroups['giMembersReceive'] = giMembersReceive
		allGroups['primaryMembersOff'] = primaryMembersOff
		allGroups['reflectionMembersOff'] = reflectionMembersOff
		allGroups['refractionMembersOff'] = refractionMembersOff
		allGroups['shadowCastsMembersOff'] = shadowCastsMembersOff
		dicoInverse = {}
		for p in allGroups.keys():
			for o in allGroups[p]:
				if dicoInverse.has_key(o):
					dicoInverse[o].append(p)
				else:
					dicoInverse[o] = []
					dicoInverse[o].append(p)


		liste = {}
		for dk in dicoInverse.keys():
			if liste.has_key(str(dicoInverse[dk])):
				liste[str(dicoInverse[dk])].append(dk)
			else:
				liste[str(dicoInverse[dk])] = []
				liste[str(dicoInverse[dk])].append(dk)

		liste_finale = {}
		for lk in liste.keys():
			liste_finale[str(liste[lk])] = lk

		vrayLambertMtl = None
		vrayLambert = False
		if pm.getAttr(arsenalPassName + '.vrayLambert'):
			vrayLambert = True
			vrayLambertbrdfMtlName = 'vrayLambertBRDFMtl_arsenal@diffuse'
			if not vrUtils.findByName(vrayLambertbrdfMtlName):
				vrUtils.create('BRDFDiffuse', vrayLambertbrdfMtlName)
			vrayLambertbrdfMtl = vrUtils.findByName(vrayLambertbrdfMtlName)
			gamaValue = pm.getAttr('vraySettings.cmap_gamma')
			if float('%.2f' % gamaValue) == 2.2 and not pm.getAttr('vraySettings.cmap_linearworkflow'):
				vrayLambertCOlorCorrectMtlName = 'vrayLambertCOlorCorrect_arsenal'
				if not vrUtils.findByName(vrayLambertCOlorCorrectMtlName):
					vrUtils.create('ColorCorrect', vrayLambertCOlorCorrectMtlName)
				vrayLambertCOlorCorrect = vrUtils.findByName(vrayLambertCOlorCorrectMtlName)
				vrayLambertCOlorCorrect[0].set('texture_map', vrUtils.AColor(0.7, 0.7, 0.7, 1))
				vrayLambertCOlorCorrect[0].set('preprocess', 1)
				vrayLambertCOlorCorrect[0].set('pre_gamma', 2.2)
				vrayLambertbrdfMtl[0].set('color', vrUtils.Color(0, 0, 0))
				vrayLambertbrdfMtl[0].set('color_tex', vrayLambertCOlorCorrect[0])
			else:
				vrayLambertbrdfMtl[0].set('color', vrUtils.Color(0.7, 0.7, 0.7))
		if vrayLambert:
			allNodes = vrUtils.findByType('Node')
		i = 0
		for result in liste_finale:
			listObjects = eval(result.replace('nt', 'pm.nt'))
			i += 1
			for mySel in listObjects:
				strObj = str(mySel.name()).replace(':', '__')
				node = vrUtils.findByName(strObj + '@node')
				if len(node) == 0:
					continue
				baseMat = node[0].get('material')
				mode = 0
				if 'primaryMembersOff' in liste_finale[result] or 'reflectionMembersOff' in liste_finale[result] or 'refractionMembersOff' in liste_finale[result] or 'shadowCastsMembersOff' in liste_finale[result]:
					mode = 1
					mtlRenderStatsName = baseMat.name() + '_arsenal%d@renderStats' % i
					if not vrUtils.findByName(mtlRenderStatsName):
						vrUtils.create('MtlRenderStats', mtlRenderStatsName)
					mtlRenderStats = vrUtils.findByName(mtlRenderStatsName)
					if 'primaryMembersOff' in liste_finale[result]:
						mtlRenderStats[0].set('camera_visibility', 0)
					if 'reflectionMembersOff' in liste_finale[result]:
						mtlRenderStats[0].set('reflections_visibility', 0)
					if 'refractionMembersOff' in liste_finale[result]:
						mtlRenderStats[0].set('refractions_visibility', 0)
					if 'shadowCastsMembersOff' in liste_finale[result]:
						mtlRenderStats[0].set('shadows_visibility', 0)
				if 'blackHoleMembers' in liste_finale[result] or 'blackHoleMembersReceiveShd' in liste_finale[result] or 'giMembersGenerate' in liste_finale[result] or 'giMembersReceive' in liste_finale[result]:
					if mode == 1:
						mode = 3
					else:
						mode = 2
					wrapperName = baseMat.name() + '_arsenal%d@mtlwrapper' % i
					if not vrUtils.findByName(wrapperName):
						vrUtils.create('MtlWrapper', wrapperName)
					wrapper = vrUtils.findByName(wrapperName)
					if 'blackHoleMembers' in liste_finale[result]:
						wrapper[0].set('matte_surface', 1)
						wrapper[0].set('alpha_contribution', -1)
						wrapper[0].set('reflection_amount', 0)
						wrapper[0].set('refraction_amount', 0)
						if 'generate_render_elements' in vrUtils.getPluginParams(wrapper[0]):
							wrapper[0].set('generate_render_elements', 0)
						if 'blackHoleMembersReceiveShd' in liste_finale[result]:
							wrapper[0].set('shadows', 1)
							wrapper[0].set('affect_alpha', 1)
					if 'giMembersGenerate' in liste_finale[result]:
						wrapper[0].set('generate_gi', 0)
					if 'giMembersReceive' in liste_finale[result]:
						wrapper[0].set('receive_gi', 0)
				if mode == 1:
					mtlRenderStats[0].set('base_mtl', baseMat)
					node[0].set('material', mtlRenderStats)
				elif mode == 2:
					wrapper[0].set('base_material', baseMat)
					node[0].set('material', wrapper)
				elif mode == 3:
					wrapper[0].set('base_material', baseMat)
					mtlRenderStats[0].set('base_mtl', wrapper)
					node[0].set('material', mtlRenderStats)


		if vrayLambert:
			vrayBumpNodes = vrUtils.findByType('BRDFBump')
			for vrayBumpNode in vrayBumpNodes:
				vrayBumpNode.set('base_brdf', vrayLambertbrdfMtl[0])

			vrayBlendNodeNodes = vrUtils.findByType('BRDFLayered')
			for vrayBlendNodeNode in vrayBlendNodeNodes:
				goodListBrdf = list()
				listBrdfs = vrayBlendNodeNode.get('brdfs')
				for listBrdf in listBrdfs:
					if listBrdf in vrayBumpNodes:
						goodListBrdf.append(listBrdf)
					else:
						goodListBrdf.append(vrayLambertbrdfMtl[0])

				vrayBlendNodeNode.set('brdfs', goodListBrdf)

			vraySimpleBRDFNodes = vrUtils.findByType('MtlSingleBRDF')
			for vraySimpleBRDFNode in vraySimpleBRDFNodes:
				inBRDF = vraySimpleBRDFNode.get('brdf')
				if inBRDF not in vrayBumpNodes and inBRDF not in vrayBlendNodeNodes:
					vraySimpleBRDFNode.set('brdf', vrayLambertbrdfMtl[0])

		actualList = pm.getAttr(arsenalPassName + '.multimatteMaskName')
		if actualList not in ('', '{}'):
			actualList = eval(actualList)
			for matteNumber in actualList:
				extraTexName = arsenalPassName + '_VRayUserColorMultimatte_number' + str(matteNumber)
				vrUtils.create('TexUserColor', extraTexName)
				variableName = actualList[matteNumber] + '_' + arsenalPassName
				extraTex = vrUtils.findByName(extraTexName)
				extraTex[0].set('default_color', vrUtils.AColor(0, 0, 0, 1))
				extraTex[0].set('user_attribute', variableName)
				extraTexRenderElementName = arsenalPassName + '_RenderElementMultimatte_number' + str(matteNumber)
				vrUtils.create('RenderChannelExtraTex', extraTexRenderElementName)
				extraTexRenderElement = vrUtils.findByName(extraTexRenderElementName)
				extraTexRenderElement[0].set('name', actualList[matteNumber])
				extraTexRenderElement[0].set('consider_for_aa', 1)
				extraTexRenderElement[0].set('affect_matte_objects', 1)
				extraTexRenderElement[0].set('texmap', extraTex[0])
				extraTexRenderElement[0].set('filtering', 1)
				myConnected = pm.listConnections(arsenalPassName + '.multimatteMaskMembers[' + str(matteNumber) + '].multimatteMaskMembersRed', destination=False, source=True)
				for dag in self.getAllChildShapes(selection=myConnected, type=['mesh', 'VRayPlane']):
					if not dag.intermediateObject.get():
						strObj = str(dag.name()).replace(':', '__')
						node = vrUtils.findByName(strObj + '@node')
						if len(node) == 0:
							continue
						currentUserAttr = node[0].get('user_attributes')
						value = variableName + '=1,0,0;' + currentUserAttr
						node[0].set('user_attributes', value)
						pm.mel.warning(strObj + '@node')
						pm.mel.warning(variableName)

				myConnected = pm.listConnections(arsenalPassName + '.multimatteMaskMembers[' + str(matteNumber) + '].multimatteMaskMembersGreen', destination=False, source=True)
				for dag in self.getAllChildShapes(selection=myConnected, type=['mesh', 'VRayPlane']):
					if not dag.intermediateObject.get():
						strObj = str(dag.name()).replace(':', '__')
						node = vrUtils.findByName(strObj + '@node')
						if len(node) == 0:
							continue
						currentUserAttr = node[0].get('user_attributes')
						value = variableName + '=0,1,0;' + currentUserAttr
						node[0].set('user_attributes', value)

				myConnected = pm.listConnections(arsenalPassName + '.multimatteMaskMembers[' + str(matteNumber) + '].multimatteMaskMembersBlue', destination=False, source=True)
				for dag in self.getAllChildShapes(selection=myConnected, type=['mesh', 'VRayPlane']):
					if not dag.intermediateObject.get():
						strObj = str(dag.name()).replace(':', '__')
						node = vrUtils.findByName(strObj + '@node')
						if len(node) == 0:
							continue
						currentUserAttr = node[0].get('user_attributes')
						value = variableName + '=0,0,1;' + currentUserAttr
						node[0].set('user_attributes', value)


		if pm.getAttr(arsenalPassName + '.vrayMaterialID'):
			self.deeXMaterialIDGeneratorFunc()
		if pm.getAttr(arsenalPassName + '.vrayProxyObjectID'):
			self.deeXProxyObjectIDGeneratorFunc()
		if not lightSelectNormalMembers:
			if pm.getAttr(arsenalPassName + '.lightSelectAllNormal'):
				lightSelectNormalMembers = vrUtils.findByType('Light*') + vrUtils.findByType('MayaLight*')
			else:
				myConnected = pm.listConnections(arsenalPassName + '.lightSelectNormalMembers', destination=False, source=True)
				for dag in self.getAllChildShapes(selection=myConnected, type=pm.listNodeTypes('light')):
					if not dag.intermediateObject.get():
						strObj = str(dag.name()).replace(':', '__')
						node = vrUtils.findByName(strObj)
						lightSelectNormalMembers.append(node[0])

		if not lightSelectDiffuseMembers:
			if pm.getAttr(arsenalPassName + '.lightSelectAllDiffuse'):
				lightSelectDiffuseMembers = vrUtils.findByType('Light*') + vrUtils.findByType('MayaLight*')
			else:
				myConnected = pm.listConnections(arsenalPassName + '.lightSelectDiffuseMembers', destination=False, source=True)
				for dag in self.getAllChildShapes(selection=myConnected, type=pm.listNodeTypes('light')):
					if not dag.intermediateObject.get():
						strObj = str(dag.name()).replace(':', '__')
						node = vrUtils.findByName(strObj)
						lightSelectDiffuseMembers.append(node[0])

		if not lightSelectRawMembers:
			if pm.getAttr(arsenalPassName + '.lightSelectAllRaw'):
				lightSelectRawMembers = vrUtils.findByType('Light*') + vrUtils.findByType('MayaLight*')
			else:
				myConnected = pm.listConnections(arsenalPassName + '.lightSelectRawMembers', destination=False, source=True)
				for dag in self.getAllChildShapes(selection=myConnected, type=pm.listNodeTypes('light')):
					if not dag.intermediateObject.get():
						strObj = str(dag.name()).replace(':', '__')
						node = vrUtils.findByName(strObj)
						lightSelectRawMembers.append(node[0])

		if not lightSelectSpecularMembers:
			if pm.getAttr(arsenalPassName + '.lightSelectAllSpecular'):
				lightSelectSpecularMembers = vrUtils.findByType('Light*') + vrUtils.findByType('MayaLight*')
			else:
				myConnected = pm.listConnections(arsenalPassName + '.lightSelectSpecularMembers', destination=False, source=True)
				for dag in self.getAllChildShapes(selection=myConnected, type=pm.listNodeTypes('light')):
					if not dag.intermediateObject.get():
						strObj = str(dag.name()).replace(':', '__')
						node = vrUtils.findByName(strObj)
						lightSelectSpecularMembers.append(node[0])

		self.deeXLightSelectGeneratorFunc(lightNormal=lightSelectNormalMembers, lightDiffuse=lightSelectDiffuseMembers, lightRaw=lightSelectRawMembers, lightSpecular=lightSelectSpecularMembers)




def arsenalFunction():
	pm.mel.warning('Start Arsenal Function')
	tool = ArsenalFunction()
	tool.start()
	pm.mel.warning('Arsenal Function done')



