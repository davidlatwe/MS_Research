import os
import pymel.all as pm
import maya.OpenMaya as OpenMaya
import subprocess
import math
import re
import sys
import shutil
import hashlib
import datetime
import time
from functools import partial

class deexVrayFastPresetType(object):

    def __init__(self, parent, actualPresetType):
        self.parent = parent
        self.actualPreset = actualPresetType
        self.vraySettings_globopt_mtl_maxDepthM = 1.0
        self.vraySettings_globopt_mtl_maxDepthH = 1.0
        self.vraySettings_dmcMaxSubdivsM = 1.0
        self.vraySettings_dmcMaxSubdivsH = 1.0
        self.vraySettings_dmcMinSubdivsM = 1.0
        self.vraySettings_dmcMinSubdivsH = 1.0
        self.vraySettings_dmcThresholdM = 1.0
        self.vraySettings_dmcThresholdH = 1.0
        self.vraySettings_imap_minRateM = 1.0
        self.vraySettings_imap_minRateH = 1.0
        self.vraySettings_imap_maxRateM = 1.0
        self.vraySettings_imap_maxRateH = 1.0
        self.vraySettings_imap_colorThresholdM = 1.0
        self.vraySettings_imap_colorThresholdH = 1.0
        self.vraySettings_imap_normalThresholdM = 1.0
        self.vraySettings_imap_normalThresholdH = 1.0
        self.vraySettings_imap_distanceThresholdM = 1.0
        self.vraySettings_imap_distanceThresholdH = 1.0
        self.vraySettings_imap_subdivsM = 1.0
        self.vraySettings_imap_subdivsH = 1.0
        self.vraySettings_imap_interpSamplesM = 1.0
        self.vraySettings_imap_interpSamplesH = 1.0
        self.vraySettings_imap_detailRadiusM = 1.0
        self.vraySettings_imap_detailRadiusH = 1.0
        self.vraySettings_imap_detailSubdivsMultM = 1.0
        self.vraySettings_imap_detailSubdivsMultH = 1.0
        self.vraySettings_subdivsM = 1.0
        self.vraySettings_subdivsH = 1.0
        self.vraySettings_sampleSizeM = 1.0
        self.vraySettings_sampleSizeH = 1.0
        self.vraySettings_prefilterSamplesM = 1.0
        self.vraySettings_prefilterSamplesH = 1.0
        self.vraySettings_filterSamplesM = 1.0
        self.vraySettings_filterSamplesH = 1.0
        self.vraySettings_dmcs_adaptiveAmountM = 1.0
        self.vraySettings_dmcs_adaptiveAmountH = 1.0
        self.vraySettings_dmcs_adaptiveThresholdM = 1.0
        self.vraySettings_dmcs_adaptiveThresholdH = 1.0
        self.vraySettings_dmcs_adaptiveMinSamplesM = 1.0
        self.vraySettings_dmcs_adaptiveMinSamplesH = 1.0
        self.vraySettings_dmcs_subdivsMultM = 1.0
        self.vraySettings_dmcs_subdivsMultH = 1.0
        self.multiplicator_vraySettings_dmcMaxSubdivs = 1.0
        self.multiplicator_vraySettings_imap_minRate = 1.0
        self.multiplicator_vraySettings_imap_maxRate = 1.0
        self.multiplicator_vraySettings_imap_detailRadius = 1.0
        self.presetComment = None




class ArsenalQualityTool(object):

    def __init__(self, parent = None):
        self.ui = parent
        self.dir = self.ui.parent.dir
        self.version = 0.7
        self.vraySettings = None
        self.deeXVrayFastOptimized = False
        self.deeXVrayFastLastQuality = 50
        self.deeXVrayFastLastTypePreset = 'deeX_interior'
        self.deeXVrayFastoptimizationChooserSettings = ''
        self.mayaVersion = pm.about(v=True).split()[0]
        self.osSystemType = pm.about(operatingSystem=True)
        self.updatePage = 'http://deex.info/deeXVrayFast/deeXVrayFastUpdate.html'
        self.website = 'http://deex.info/'
        self.alwaysFastInserted = False
        self.actualPresetPrecomp = ''
        self.environVRAY_TOOLS = None
        for myEnv in os.environ:
            if 'VRAY_TOOLS_MAYA' in myEnv:
                self.environVRAY_TOOLS = os.environ[myEnv]

        self.materialIDexcludeType = ['particleCloud',
         'shaderGlow',
         'hairTubeShader',
         'layeredShader',
         'oceanShader',
         'useBackground']
        self.vraySettings_globopt_mtl_maxDepthM = 1.0
        self.vraySettings_globopt_mtl_maxDepthH = 1.0
        self.vraySettings_dmcMaxSubdivsM = 1.0
        self.vraySettings_dmcMaxSubdivsH = 1.0
        self.vraySettings_dmcMinSubdivsM = 1.0
        self.vraySettings_dmcMinSubdivsH = 1.0
        self.vraySettings_dmcThresholdM = 1.0
        self.vraySettings_dmcThresholdH = 1.0
        self.vraySettings_imap_minRateM = 1.0
        self.vraySettings_imap_minRateH = 1.0
        self.vraySettings_imap_maxRateM = 1.0
        self.vraySettings_imap_maxRateH = 1.0
        self.vraySettings_imap_colorThresholdM = 1.0
        self.vraySettings_imap_colorThresholdH = 1.0
        self.vraySettings_imap_normalThresholdM = 1.0
        self.vraySettings_imap_normalThresholdH = 1.0
        self.vraySettings_imap_distanceThresholdM = 1.0
        self.vraySettings_imap_distanceThresholdH = 1.0
        self.vraySettings_imap_subdivsM = 1.0
        self.vraySettings_imap_subdivsH = 1.0
        self.vraySettings_imap_interpSamplesM = 1.0
        self.vraySettings_imap_interpSamplesH = 1.0
        self.vraySettings_imap_detailRadiusM = 1.0
        self.vraySettings_imap_detailRadiusH = 1.0
        self.vraySettings_imap_detailSubdivsMultM = 1.0
        self.vraySettings_imap_detailSubdivsMultH = 1.0
        self.vraySettings_subdivsM = 1.0
        self.vraySettings_subdivsH = 1.0
        self.vraySettings_sampleSizeM = 1.0
        self.vraySettings_sampleSizeH = 1.0
        self.vraySettings_prefilterSamplesM = 1.0
        self.vraySettings_prefilterSamplesH = 1.0
        self.vraySettings_filterSamplesM = 1.0
        self.vraySettings_filterSamplesH = 1.0
        self.vraySettings_dmcs_adaptiveAmountM = 1.0
        self.vraySettings_dmcs_adaptiveAmountH = 1.0
        self.vraySettings_dmcs_adaptiveThresholdM = 1.0
        self.vraySettings_dmcs_adaptiveThresholdH = 1.0
        self.vraySettings_dmcs_adaptiveMinSamplesM = 1.0
        self.vraySettings_dmcs_adaptiveMinSamplesH = 1.0
        self.vraySettings_dmcs_subdivsMultM = 1.0
        self.vraySettings_dmcs_subdivsMultH = 1.0
        self.multiplicator_vraySettings_dmcMaxSubdivs = 1.0
        self.multiplicator_vraySettings_imap_minRate = 1.0
        self.multiplicator_vraySettings_imap_maxRate = 1.0
        self.multiplicator_vraySettings_imap_detailRadius = 1.0
        self.presetComment = None
        self.preCompString = None
        self.preCompComment = None
        self.preCompRenderElements = None



    def initializeSet(self, *args):
        self.vraySettings = pm.PyNode('vraySettings')
        if pm.attributeQuery('deeXVrayFastOptimized', n=self.vraySettings.name(), ex=True):
            self.deeXVrayFastOptimized = True
            self.vraySettings.samplerType.set(1)
            if not pm.attributeQuery('deeXVrayFastLastQuality', n=self.vraySettings.name(), ex=True):
                self.deeXVrayFastLastQuality = 50
                locked = False
                if pm.lockNode(self.vraySettings.name(), query=True, lock=True)[0]:
                    locked = True
                    pm.lockNode(self.vraySettings.name(), lock=False)
                pm.addAttr(self.vraySettings.name(), ln='deeXVrayFastLastQuality', at='long')
                if locked:
                    pm.lockNode(self.vraySettings.name(), lock=True)
                self.vraySettings.deeXVrayFastLastQuality.set(self.deeXVrayFastLastQuality)
            else:
                self.deeXVrayFastLastQuality = self.vraySettings.deeXVrayFastLastQuality.get()



    def saveSetting(self, *args):
        dicoAttr = {}
        for myAttr in pm.listAttr(self.vraySettings.name()):
            try:
                dicoAttr[myAttr] = pm.getAttr('vraySettings.' + myAttr)
            except:
                OpenMaya.MGlobal.displayInfo('[Arsenal Quality] ' + myAttr + ' value can not be saved or have not value.')

        if not pm.attributeQuery('deeXVrayFastActualSettings', n=self.vraySettings.name(), ex=True):
            locked = False
            if pm.lockNode(self.vraySettings.name(), query=True, lock=True)[0]:
                locked = True
                pm.lockNode(self.vraySettings.name(), lock=False)
            pm.addAttr(self.vraySettings.name(), ln='deeXVrayFastActualSettings', dt='string')
            if locked:
                pm.lockNode(self.vraySettings.name(), lock=True)
        self.vraySettings.deeXVrayFastActualSettings.set(str(dicoAttr))



    def optimize(self):
        self.deeXVrayFastOptimized = True
        locked = False
        if pm.lockNode(self.vraySettings.name(), query=True, lock=True)[0]:
            locked = True
            pm.lockNode(self.vraySettings.name(), lock=False)
        if not pm.attributeQuery('deeXVrayFastOptimized', n=self.vraySettings.name(), ex=True):
            pm.addAttr(self.vraySettings.name(), ln='deeXVrayFastOptimized', at='bool')
            self.vraySettings.deeXVrayFastOptimized.set(1)
            pm.addAttr(self.vraySettings.name(), ln='deeXVrayFastLastQuality', at='long')
            self.vraySettings.deeXVrayFastLastQuality.set(50)
            pm.addAttr('vraySettings', ln='deeXVrayFastLastTypePreset', dt='string')
            self.vraySettings.deeXVrayFastLastTypePreset.set('deeX_interior')
            pm.addAttr('vraySettings', ln='deeXVrayFastLastPresetPreComp', dt='string')
            self.vraySettings.deeXVrayFastLastPresetPreComp.set('deeX_basic')
            pm.addAttr('vraySettings', ln='deeXVrayFastoptimizationChooserSettings', dt='string')
            self.vraySettings.deeXVrayFastoptimizationChooserSettings.set("{'OptimizationChooserGlobalOptionInt': [False, 0], 'OptimizationChooserImageSamplerInt': [False, 0], 'OptimizationChooserDMCSamplerInt': [False, 0], 'OptimizationChooserIrradianceMapInt': [False, 0], 'OptimizationChooserLightCacheInt': [False, 0], 'OptimizationChooserSystemInt': [False, 0]}")
        if locked:
            pm.lockNode(self.vraySettings.name(), lock=True)
        self.initAttributes()
        self.refresh()



    def createFile(self, file):
        if os.path.exists(self.dir + file):
            OpenMaya.MGlobal.displayInfo('[Arsenal Quality] File ' + file + ' exists.')
        else:
            fichier = open(self.dir + file, 'w')
            fichier.close()
        return self.dir + file



    def createDir(self, dir):
        if os.path.exists(self.dir + dir):
            OpenMaya.MGlobal.displayInfo('[Arsenal Quality] Dir ' + dir + ' exists.')
        else:
            os.makedirs(self.dir + dir)
            OpenMaya.MGlobal.displayInfo('[Arsenal Quality] Dir ' + self.dir + dir + ' created.')
        return self.dir + dir



    def listFile(self, dir = '', start = '', end = ''):
        dirList = os.listdir(dir)
        listFile = list()
        for fname in dirList:
            if fname.startswith(start) and fname.endswith(end):
                listFile.append(fname)

        return listFile



    def backSetting(self, *args):
        if pm.attributeQuery('deeXVrayFastActualSettings', n='vraySettings', ex=True):
            if pm.objExists('deeXVrayFastExpression'):
                pm.delete('deeXVrayFastExpression')
                print '[Arsenal Quality] OdeeXVrayFastExpression deleted.'
            lines = pm.getAttr('vraySettings.deeXVrayFastActualSettings')
            dico = eval(lines)
            for myAttr in dico:
                value = dico[myAttr]
                if type(dico[myAttr]) == list:
                    value = dico[myAttr][0]
                if value:
                    try:
                        locked = 0
                        if pm.getAttr('vraySettings.' + myAttr, lock=True) == 1:
                            pm.setAttr('vraySettings.' + myAttr, lock=False)
                            locked = 1
                        pm.setAttr('vraySettings.' + myAttr, value)
                        if locked == 1:
                            pm.setAttr('vraySettings.' + myAttr, lock=True)
                    except:
                        print '[Arsenal Quality] ' + myAttr + ' value can not be setted.'

            locked = False
            if pm.lockNode('vraySettings', query=True, lock=True)[0]:
                locked = True
                pm.lockNode('vraySettings', lock=False)
            attToDelete = ['deeXVrayFastLastQuality',
             'deeXVrayFastOptimized',
             'deeXVrayFastActualSettings',
             'deeXVrayFastoptimizationChooserSettings',
             'deeXVrayFastLastTypePreset',
             'deeXVrayFastLastPresetPreComp']
            for myAttr in attToDelete:
                if pm.attributeQuery(myAttr, n='vraySettings', ex=True):
                    pm.deleteAttr('vraySettings.' + myAttr)

            if locked:
                pm.lockNode('vraySettings', lock=True)
            print '[Arsenal Quality] Original settings applied.'
        else:
            print '[Arsenal Quality] deeXVrayFastActualSettings attribute not found'



    def presetTypeInitGetValue(self, preset):
        fileName = self.dir + 'presets/deeXVrayFastPresetType_' + preset + '.txt'
        dico = {}
        dicoMultiplicator = {}
        commentString = ''
        if os.path.exists(fileName):
            file = open(fileName, 'r')
            lines = file.readlines()
            for line in lines:
                if re.search('vraySettings', line) and not re.search('multiplicator\\|vraySettings', line):
                    attribut = line.split('=')[0].strip()
                    mediumValue = line.split('=')[1].split('|')[0].strip()
                    veryHighValue = line.split('=')[1].split('|')[1].strip()
                    dico[attribut] = [mediumValue, veryHighValue]
                elif re.search('multiplicator\\|vraySettings', line):
                    attribut = line.split('=')[0].strip().split('|')[1].strip()
                    multiplicator = line.split('=')[1].strip()
                    dicoMultiplicator[attribut] = [multiplicator]
                elif re.search('presetComment', line):
                    commentString = str(line.split('=')[1].replace('\\\\', '\\').replace('\\n', '\n'))

            file.close()
        return (dico, dicoMultiplicator, commentString)



    def setValue(self, attribute = None, value = None, node = None):
        if node is None or not pm.objExists(node):
            OpenMaya.MGlobal.displayError('[Arsenal] Node ' + str(node) + 'does not exist')
            return 
        if attribute is None:
            OpenMaya.MGlobal.displayError('[Arsenal] Attribute not found on the pass')
            return 
        if value is None:
            OpenMaya.MGlobal.displayError('[Arsenal] No value gave to the pass')
            return 
        if not pm.objExists(node + '.' + attribute):
            OpenMaya.MGlobal.displayError('[Arsenal] Attribute not found on the node ' + node)
            return 
        pm.setAttr(node + '.' + attribute, value)



    def initAttributes(self):
        if not pm.attributeQuery('deeXVrayFastOptimized', n=self.vraySettings.name(), ex=True):
            self.deeXVrayFastOptimized = False
            return 
        self.deeXVrayFastLastQuality = self.vraySettings.deeXVrayFastLastQuality.get()
        self.deeXVrayFastLastTypePreset = self.vraySettings.deeXVrayFastLastTypePreset.get()
        self.deeXVrayFastLastPresetPreComp = self.vraySettings.deeXVrayFastLastPresetPreComp.get()
        self.deeXVrayFastoptimizationChooserSettings = self.vraySettings.deeXVrayFastoptimizationChooserSettings.get()
        (dico, dicoMultiplicator, commentString,) = self.presetTypeInitGetValue(self.deeXVrayFastLastTypePreset)
        for myAttr in dico:
            if myAttr == 'vraySettings.globopt_mtl_maxDepth':
                self.vraySettings_globopt_mtl_maxDepthM = dico[myAttr][0]
                self.vraySettings_globopt_mtl_maxDepthH = dico[myAttr][1]
            if myAttr == 'vraySettings.dmcMaxSubdivs':
                self.vraySettings_dmcMaxSubdivsM = dico[myAttr][0]
                self.vraySettings_dmcMaxSubdivsH = dico[myAttr][1]
            if myAttr == 'vraySettings.dmcMinSubdivs':
                self.vraySettings_dmcMinSubdivsM = dico[myAttr][0]
                self.vraySettings_dmcMinSubdivsH = dico[myAttr][1]
            if myAttr == 'vraySettings.dmcThreshold':
                self.vraySettings_dmcThresholdM = dico[myAttr][0]
                self.vraySettings_dmcThresholdH = dico[myAttr][1]
            if myAttr == 'vraySettings.imap_minRate':
                self.vraySettings_imap_minRateM = dico[myAttr][0]
                self.vraySettings_imap_minRateH = dico[myAttr][1]
            if myAttr == 'vraySettings.imap_maxRate':
                self.vraySettings_imap_maxRateM = dico[myAttr][0]
                self.vraySettings_imap_maxRateH = dico[myAttr][1]
            if myAttr == 'vraySettings.imap_colorThreshold':
                self.vraySettings_imap_colorThresholdM = dico[myAttr][0]
                self.vraySettings_imap_colorThresholdH = dico[myAttr][1]
            if myAttr == 'vraySettings.imap_normalThreshold':
                self.vraySettings_imap_normalThresholdM = dico[myAttr][0]
                self.vraySettings_imap_normalThresholdH = dico[myAttr][1]
            if myAttr == 'vraySettings.imap_distanceThreshold':
                self.vraySettings_imap_distanceThresholdM = dico[myAttr][0]
                self.vraySettings_imap_distanceThresholdH = dico[myAttr][1]
            if myAttr == 'vraySettings.imap_subdivs':
                self.vraySettings_imap_subdivsM = dico[myAttr][0]
                self.vraySettings_imap_subdivsH = dico[myAttr][1]
            if myAttr == 'vraySettings.imap_interpSamples':
                self.vraySettings_imap_interpSamplesM = dico[myAttr][0]
                self.vraySettings_imap_interpSamplesH = dico[myAttr][1]
            if myAttr == 'vraySettings.imap_detailRadius':
                self.vraySettings_imap_detailRadiusM = dico[myAttr][0]
                self.vraySettings_imap_detailRadiusH = dico[myAttr][1]
            if myAttr == 'vraySettings.imap_detailSubdivsMult':
                self.vraySettings_imap_detailSubdivsMultM = dico[myAttr][0]
                self.vraySettings_imap_detailSubdivsMultH = dico[myAttr][1]
            if myAttr == 'vraySettings.subdivs':
                self.vraySettings_subdivsM = dico[myAttr][0]
                self.vraySettings_subdivsH = dico[myAttr][1]
            if myAttr == 'vraySettings.sampleSize':
                self.vraySettings_sampleSizeM = dico[myAttr][0]
                self.vraySettings_sampleSizeH = dico[myAttr][1]
            if myAttr == 'vraySettings.prefilterSamples':
                self.vraySettings_prefilterSamplesM = dico[myAttr][0]
                self.vraySettings_prefilterSamplesH = dico[myAttr][1]
            if myAttr == 'vraySettings.filterSamples':
                self.vraySettings_filterSamplesM = dico[myAttr][0]
                self.vraySettings_filterSamplesH = dico[myAttr][1]
            if myAttr == 'vraySettings.dmcs_adaptiveAmount':
                self.vraySettings_dmcs_adaptiveAmountM = dico[myAttr][0]
                self.vraySettings_dmcs_adaptiveAmountH = dico[myAttr][1]
            if myAttr == 'vraySettings.dmcs_adaptiveThreshold':
                self.vraySettings_dmcs_adaptiveThresholdM = dico[myAttr][0]
                self.vraySettings_dmcs_adaptiveThresholdH = dico[myAttr][1]
            if myAttr == 'vraySettings.dmcs_adaptiveMinSamples':
                self.vraySettings_dmcs_adaptiveMinSamplesM = dico[myAttr][0]
                self.vraySettings_dmcs_adaptiveMinSamplesH = dico[myAttr][1]
            if myAttr == 'vraySettings.dmcs_subdivsMult':
                self.vraySettings_dmcs_subdivsMultM = dico[myAttr][0]
                self.vraySettings_dmcs_subdivsMultH = dico[myAttr][1]

        for myAttr in dicoMultiplicator:
            if myAttr == 'vraySettings.dmcMaxSubdivs':
                self.multiplicator_vraySettings_dmcMaxSubdivs = dicoMultiplicator[myAttr][0]
            if myAttr == 'vraySettings.imap_minRate':
                self.multiplicator_vraySettings_imap_minRate = dicoMultiplicator[myAttr][0]
            if myAttr == 'vraySettings.imap_maxRate':
                self.multiplicator_vraySettings_imap_maxRate = dicoMultiplicator[myAttr][0]
            if myAttr == 'vraySettings.imap_detailRadius':
                self.multiplicator_vraySettings_imap_detailRadius = dicoMultiplicator[myAttr][0]

        self.presetComment = commentString



    def optimizationChooserChange(self, value = None, attribute = None, enabled = None):
        strDico = self.vraySettings.deeXVrayFastoptimizationChooserSettings.get()
        dico = eval(strDico)
        dico[attribute] = [enabled, value]
        self.vraySettings.deeXVrayFastoptimizationChooserSettings.set(str(dico))
        self.refresh()



    def optimizeLights(self):
        allLights = pm.ls(type=['VRayLightIESShape',
         'VRayLightRectShape',
         'VRayLightSphereShape',
         'VRayLightDomeShape',
         'directionalLight',
         'pointLight',
         'spotLight',
         'areaLight'])
        for myLight in allLights:
            if pm.attributeQuery('subdivs', n=myLight, ex=True):
                if not myLight.subdivs.get(lock=True):
                    if myLight.nodeType() == 'VRayLightDomeShape':
                        myLight.subdivs.set(50)
                    else:
                        myLight.subdivs.set(5)
            if pm.attributeQuery('shadowRays', n=myLight, ex=True):
                if not myLight.shadowRays.get(lock=True):
                    myLight.shadowRays.set(5)

        print '[Arsenal Quality] All lights optimized.'



    def optimizeMat(self, layerMode = False, minSub = 8, maxSubd = 92):
        maxGlo = 1
        minGlo = 0
        allMaterials = pm.ls(type=['VRayCarPaintMtl', 'VRayFastSSS2', 'VRayMtl'])
        for myMat in allMaterials:
            reflectanceAttributes = {'["reflectionGlossiness"]': 'reflectionSubdivs',
             '["refractionGlossiness"]': 'refractionSubdivs',
             '["glossiness"]': 'reflectionSubdivs',
             '["coat_glossiness", "base_glossiness"]': 'subdivs'}
            for gloAttList in reflectanceAttributes:
                if pm.objExists(myMat + '.' + reflectanceAttributes[gloAttList]):
                    if not pm.getAttr(myMat + '.' + reflectanceAttributes[gloAttList], lock=True) and len(pm.listConnections(myMat + '.' + reflectanceAttributes[gloAttList], d=False, s=True)) == 0:
                        lastMoyeneValue = 1
                        first = True
                        go = False
                        for gloAtt in eval(gloAttList):
                            if pm.objExists(myMat + '.' + gloAtt) and len(pm.listConnections(myMat + '.' + gloAtt, d=False, s=True)) == 0:
                                gloValue = pm.getAttr(myMat + '.' + gloAtt)
                                if first:
                                    lastMoyeneValue = gloValue
                                    first = False
                                else:
                                    lastMoyeneValue = (lastMoyeneValue + gloValue) / 2
                                go = True

                        if go:
                            value = (lastMoyeneValue - maxGlo) * (maxSubd - minSub) / (minGlo - maxGlo) + minSub
                            if layerMode:
                                if pm.editRenderLayerGlobals(query=True, currentRenderLayer=True) == 'defaultRenderLayer':
                                    OpenMaya.MGlobal.displayError('[Arsenal Quality] You can not use layerMode if you are on masterLayer')
                                    return 
                                pm.editRenderLayerAdjustment(myMat + '.' + reflectanceAttributes[str(gloAttList)])
                            pm.setAttr(myMat.name() + '.' + reflectanceAttributes[str(gloAttList)], value)
                            print '[Arsenal Quality] ' + str(value) + ' setted on attribute ' + reflectanceAttributes[str(gloAttList)] + ' for material ' + myMat.name()


        print '[Arsenal Quality] All materials optimized.'



    def refresh(self):
        if not self.deeXVrayFastOptimized:
            return 
        lines = self.vraySettings.deeXVrayFastoptimizationChooserSettings.get()
        dicoOptimizationChooser = eval(lines)
        valueAs = float(self.vraySettings.width.get() * 1.0 / (self.vraySettings.height.get() * 1.0))
        pm.mel.eval('vrayUpdateAspectRatio;')
        self.vraySettings.aspectRatio.set(valueAs)
        pm.mel.eval('vrayChangeResolution();')
        resolution = self.vraySettings.width.get() * self.vraySettings.height.get()
        realQuality = self.deeXVrayFastLastQuality
        enable = True
        if dicoOptimizationChooser:
            if dicoOptimizationChooser['OptimizationChooserGlobalOptionInt'][0]:
                realQuality += dicoOptimizationChooser['OptimizationChooserGlobalOptionInt'][1]
        if enable:
            multiplier = (float(self.vraySettings_globopt_mtl_maxDepthH) - float(self.vraySettings_globopt_mtl_maxDepthM)) / 50
            minValue = float(self.vraySettings_globopt_mtl_maxDepthM) - multiplier * 50
            if pm.attributeQuery('globopt_mtl_limitDepth', n='vraySettings', ex=True):
                if not self.vraySettings.globopt_mtl_limitDepth.get(lock=True):
                    self.vraySettings.globopt_mtl_limitDepth.set(1)
                value = minValue + realQuality * multiplier
                if value <= 2.0:
                    value = 2.0
                if not self.vraySettings.globopt_mtl_maxDepth.get(lock=True):
                    self.vraySettings.globopt_mtl_maxDepth.set(value)
        realQuality = self.deeXVrayFastLastQuality
        enable = True
        if dicoOptimizationChooser:
            if dicoOptimizationChooser['OptimizationChooserImageSamplerInt'][0]:
                realQuality += dicoOptimizationChooser['OptimizationChooserImageSamplerInt'][1]
        if enable:
            multiplier = (float(self.vraySettings_dmcMaxSubdivsH) - float(self.vraySettings_dmcMaxSubdivsM)) / 50
            minValue = float(self.vraySettings_dmcMaxSubdivsM) - multiplier * 50
            value = minValue + realQuality * multiplier
            if value <= 2:
                value = 2.0
            n = math.log(307200.0 / resolution) / math.log(4.0) * -1
            subdi = math.ceil(value / float(self.multiplicator_vraySettings_dmcMaxSubdivs) ** n)
            if pm.attributeQuery('dmcMaxSubdivs', n='vraySettings', ex=True):
                if not self.vraySettings.dmcMaxSubdivs.get(lock=True):
                    self.vraySettings.dmcMaxSubdivs.set(subdi)
            multiplier = (float(self.vraySettings_dmcMinSubdivsH) - float(self.vraySettings_dmcMinSubdivsM)) / 50
            minValue = float(self.vraySettings_dmcMinSubdivsM) - multiplier * 50
            value = minValue + realQuality * multiplier
            if value <= 1:
                value = 1
            if pm.attributeQuery('dmcMinSubdivs', n='vraySettings', ex=True):
                if not self.vraySettings.dmcMinSubdivs.get(lock=True):
                    self.vraySettings.dmcMinSubdivs.set(value)
            multiplier = (float(self.vraySettings_dmcThresholdM) - float(self.vraySettings_dmcThresholdH)) / 50
            minValue = float(self.vraySettings_dmcThresholdM) + multiplier * 50
            value = minValue - realQuality * multiplier
            if value <= 0.001:
                value = 0.001
            if pm.attributeQuery('dmcThreshold', n='vraySettings', ex=True):
                if not self.vraySettings.dmcThreshold.get(lock=True):
                    self.vraySettings.dmcThreshold.set(value)
        realQuality = self.deeXVrayFastLastQuality
        enable = True
        if dicoOptimizationChooser:
            if dicoOptimizationChooser['OptimizationChooserIrradianceMapInt'][0]:
                realQuality += dicoOptimizationChooser['OptimizationChooserIrradianceMapInt'][1]
        if enable:
            multiplier = (float(self.vraySettings_imap_minRateH) - float(self.vraySettings_imap_minRateM)) / 50
            minValue = float(self.vraySettings_imap_minRateM) - multiplier * 50
            value = minValue + realQuality * multiplier
            n = math.log(307200.0 / resolution) / math.log(4.0) * -1
            subdi = round(value + float(self.multiplicator_vraySettings_imap_minRate) * n)
            if pm.attributeQuery('imap_minRate', n='vraySettings', ex=True):
                if not self.vraySettings.imap_minRate.get(lock=True):
                    self.vraySettings.imap_minRate.set(subdi)
            multiplier = (float(self.vraySettings_imap_maxRateH) - float(self.vraySettings_imap_maxRateM)) / 50
            minValue = float(self.vraySettings_imap_maxRateM) - multiplier * 50
            value = minValue + realQuality * multiplier
            if value >= -1.0:
                value = -1.0
            n = math.log(307200.0 / resolution) / math.log(4.0) * -1
            subdi = round(value + float(self.multiplicator_vraySettings_imap_maxRate) * n)
            if pm.attributeQuery('imap_maxRate', n='vraySettings', ex=True):
                if not self.vraySettings.imap_maxRate.get(lock=True):
                    self.vraySettings.imap_maxRate.set(subdi)
            multiplier = (float(self.vraySettings_imap_colorThresholdM) - float(self.vraySettings_imap_colorThresholdH)) / 50
            minValue = float(self.vraySettings_imap_colorThresholdM) + multiplier * 50
            value = minValue - realQuality * multiplier
            if value <= 0.001:
                value = 0.001
            if pm.attributeQuery('imap_colorThreshold', n='vraySettings', ex=True):
                if not self.vraySettings.imap_colorThreshold.get(lock=True):
                    self.vraySettings.imap_colorThreshold.set(value)
            multiplier = (float(self.vraySettings_imap_normalThresholdM) - float(self.vraySettings_imap_normalThresholdH)) / 50
            minValue = float(self.vraySettings_imap_normalThresholdM) + multiplier * 50
            value = minValue - realQuality * multiplier
            if value <= 0.001:
                value = 0.001
            if pm.attributeQuery('imap_normalThreshold', n='vraySettings', ex=True):
                if not self.vraySettings.imap_normalThreshold.get(lock=True):
                    self.vraySettings.imap_normalThreshold.set(value)
            multiplier = (float(self.vraySettings_imap_distanceThresholdH) - float(self.vraySettings_imap_distanceThresholdM)) / 50
            minValue = float(self.vraySettings_imap_distanceThresholdM) - multiplier * 50
            value = minValue + multiplier * realQuality
            if value <= 0:
                value = 0
            if pm.attributeQuery('imap_distanceThreshold', n='vraySettings', ex=True):
                if not self.vraySettings.imap_distanceThreshold.get(lock=True):
                    self.vraySettings.imap_distanceThreshold.set(value)
            multiplier = (float(self.vraySettings_imap_subdivsM) - float(self.vraySettings_imap_subdivsH)) / 50
            minValue = float(self.vraySettings_imap_subdivsM) + multiplier * 50
            value = minValue - realQuality * multiplier
            if value <= 1:
                value = 1
            if pm.attributeQuery('imap_subdivs', n='vraySettings', ex=True):
                if not self.vraySettings.imap_subdivs.get(lock=True):
                    self.vraySettings.imap_subdivs.set(value)
            multiplier = (float(self.vraySettings_imap_interpSamplesM) - float(self.vraySettings_imap_interpSamplesH)) / 50
            minValue = float(self.vraySettings_imap_interpSamplesM) + multiplier * 50
            value = minValue - realQuality * multiplier
            if value <= 1:
                value = 1
            if pm.attributeQuery('imap_interpSamples', n='vraySettings', ex=True):
                if not self.vraySettings.imap_interpSamples.get(lock=True):
                    self.vraySettings.imap_interpSamples.set(value)
            multiplier = (float(eval(str(self.vraySettings_imap_detailRadiusH))) - float(self.vraySettings_imap_detailRadiusM)) / 50
            minValue = float(self.vraySettings_imap_detailRadiusM) - multiplier * 50
            value = minValue + realQuality * multiplier
            if value <= 1:
                value = 1
            n = math.log(307200.0 / resolution) / math.log(4.0) * -1
            radius = value * float(self.multiplicator_vraySettings_imap_detailRadius) ** n
            if pm.attributeQuery('imap_detailRadius', n='vraySettings', ex=True):
                if not self.vraySettings.imap_detailRadius.get(lock=True):
                    self.vraySettings.imap_detailRadius.set(radius)
            multiplier = (float(self.vraySettings_imap_detailSubdivsMultH) - float(self.vraySettings_imap_detailSubdivsMultM)) / 50
            minValue = float(self.vraySettings_imap_detailSubdivsMultM) - multiplier * 50
            value = minValue + realQuality * multiplier
            if value <= 0.001:
                value = 0.001
            if pm.attributeQuery('imap_detailSubdivsMult', n='vraySettings', ex=True):
                if not self.vraySettings.imap_detailSubdivsMult.get(lock=True):
                    self.vraySettings.imap_detailSubdivsMult.set(value)
        realQuality = self.deeXVrayFastLastQuality
        enable = True
        if dicoOptimizationChooser:
            if dicoOptimizationChooser['OptimizationChooserLightCacheInt'][0]:
                realQuality += dicoOptimizationChooser['OptimizationChooserLightCacheInt'][1]
        if enable:
            multiplier = (float(self.vraySettings_subdivsH) - float(self.vraySettings_subdivsM)) / 50
            minValue = float(self.vraySettings_subdivsM) - multiplier * 50
            value = minValue + realQuality * multiplier
            if value <= 388:
                value = 388
            if pm.attributeQuery('subdivs', n='vraySettings', ex=True):
                if not self.vraySettings.subdivs.get(lock=True):
                    self.vraySettings.subdivs.set(value)
            multiplier = (float(self.vraySettings_sampleSizeM) - float(self.vraySettings_sampleSizeH)) / 50
            minValue = float(self.vraySettings_sampleSizeM) + multiplier * 50
            value = minValue - realQuality * multiplier
            if value >= 0.02:
                value = 0.02
            if value <= 0.001:
                value = 0.001
            if pm.attributeQuery('sampleSize', n='vraySettings', ex=True):
                if not self.vraySettings.sampleSize.get(lock=True):
                    self.vraySettings.sampleSize.set(value)
            multiplier = (float(self.vraySettings_prefilterSamplesH) - float(self.vraySettings_prefilterSamplesM)) / 50
            minValue = float(self.vraySettings_prefilterSamplesM) - multiplier * 50
            value = minValue + realQuality * multiplier
            if value <= 11:
                value = 11
            if pm.attributeQuery('prefilter', n='vraySettings', ex=True):
                if not self.vraySettings.prefilter.get(lock=True):
                    self.vraySettings.prefilter.set(1)
            if pm.attributeQuery('prefilterSamples', n='vraySettings', ex=True):
                if not self.vraySettings.prefilterSamples.get(lock=True):
                    self.vraySettings.prefilterSamples.set(value)
            if pm.attributeQuery('useForGlossy', n='vraySettings', ex=True):
                if not self.vraySettings.useForGlossy.get(lock=True):
                    self.vraySettings.useForGlossy.set(1)
            if pm.attributeQuery('useRetraceThreshold', n='vraySettings', ex=True):
                if not self.vraySettings.useRetraceThreshold.get(lock=True):
                    self.vraySettings.useRetraceThreshold.set(1)
            multiplier = (float(self.vraySettings_filterSamplesH) - float(self.vraySettings_filterSamplesM)) / 50
            minValue = float(self.vraySettings_filterSamplesM) - multiplier * 50
            value = minValue + realQuality * multiplier
            if value <= 3:
                value = 3
            if pm.attributeQuery('filterSamples', n='vraySettings', ex=True):
                if not self.vraySettings.filterSamples.get(lock=True):
                    self.vraySettings.filterSamples.set(value)
            line = 'string $core[] = `hardware -npr`;\nvraySettings.numPasses = $core[0];'
            if not pm.objExists('deeXVrayFastExpression'):
                pm.expression(n='deeXVrayFastExpression', s=line)
            else:
                actualExpression = pm.expression('deeXVrayFastExpression', s=True, query=True)
                if line not in actualExpression:
                    pm.expression('deeXVrayFastExpression', edit=True, s=actualExpression + '\n' + line)
        else:
            line = 'string $core[] = `hardware -npr`;\nvraySettings.numPasses = $core[0];'
            if pm.objExists('deeXVrayFastExpression'):
                actualExpression = pm.expression('deeXVrayFastExpression', s=True, query=True)
                if line in actualExpression:
                    pm.expression('deeXVrayFastExpression', edit=True, s=actualExpression.replace(line, ''))
        realQuality = self.deeXVrayFastLastQuality
        enable = True
        if dicoOptimizationChooser:
            if dicoOptimizationChooser['OptimizationChooserDMCSamplerInt'][0]:
                realQuality += dicoOptimizationChooser['OptimizationChooserDMCSamplerInt'][1]
        if enable:
            multiplier = (float(self.vraySettings_dmcs_adaptiveAmountM) - float(self.vraySettings_dmcs_adaptiveAmountH)) / 50
            minValue = float(self.vraySettings_dmcs_adaptiveAmountM) + multiplier * 50
            value = minValue - realQuality * multiplier
            if value >= 1.0:
                value = 1.0
            if value <= 0.001:
                value = 0.001
            if pm.attributeQuery('dmcs_adaptiveAmount', n='vraySettings', ex=True):
                if not self.vraySettings.dmcs_adaptiveAmount.get(lock=True):
                    self.vraySettings.dmcs_adaptiveAmount.set(value)
            multiplier = (float(self.vraySettings_dmcs_adaptiveThresholdM) - float(self.vraySettings_dmcs_adaptiveThresholdH)) / 50
            minValue = float(self.vraySettings_dmcs_adaptiveThresholdM) + multiplier * 50
            value = minValue - realQuality * multiplier
            if value <= 0.001:
                value = 0.001
            if pm.attributeQuery('dmcs_adaptiveThreshold', n='vraySettings', ex=True):
                if not self.vraySettings.dmcs_adaptiveThreshold.get(lock=True):
                    self.vraySettings.dmcs_adaptiveThreshold.set(value)
            multiplier = (float(self.vraySettings_dmcs_adaptiveMinSamplesH) - float(self.vraySettings_dmcs_adaptiveMinSamplesM)) / 50
            minValue = float(self.vraySettings_dmcs_adaptiveMinSamplesM) - multiplier * 50
            value = minValue + realQuality * multiplier
            if value <= 8.0:
                value = 8.0
            if pm.attributeQuery('dmcs_adaptiveMinSamples', n='vraySettings', ex=True):
                if not self.vraySettings.dmcs_adaptiveMinSamples.get(lock=True):
                    self.vraySettings.dmcs_adaptiveMinSamples.set(value)
            multiplier = (float(self.vraySettings_dmcs_subdivsMultH) - float(self.vraySettings_dmcs_subdivsMultM)) / 50
            minValue = float(self.vraySettings_dmcs_subdivsMultM) - multiplier * 50
            value = minValue + realQuality * multiplier
            if value <= 0.5:
                value = 0.5
            if pm.attributeQuery('dmcs_subdivsMult', n='vraySettings', ex=True):
                if not self.vraySettings.dmcs_subdivsMult.get(lock=True):
                    self.vraySettings.dmcs_subdivsMult.set(value)
        realQuality = self.deeXVrayFastLastQuality
        enable = True
        if dicoOptimizationChooser:
            if dicoOptimizationChooser['OptimizationChooserSystemInt'][0]:
                realQuality += dicoOptimizationChooser['OptimizationChooserSystemInt'][1]
        if enable:
            if pm.attributeQuery('ddisplac_maxSubdivs', n='vraySettings', ex=True):
                if not self.vraySettings.ddisplac_maxSubdivs.get(lock=True):
                    self.vraySettings.ddisplac_maxSubdivs.set(23)
            if pm.attributeQuery('sys_regsgen_xylocked', n='vraySettings', ex=True):
                if not self.vraySettings.sys_regsgen_xylocked.get(lock=True):
                    self.vraySettings.sys_regsgen_xylocked.set(0)
            core = int(pm.hardware(npr=True)[0])
            count = 0
            value = 60
            for bucketSize in [self.vraySettings.width.get(), self.vraySettings.height.get()]:
                finalValue = 0
                lastValue = 80
                for i in range(40, 80):
                    if bucketSize % i <= lastValue:
                        lastValue = bucketSize % i
                        if lastValue == 0:
                            finalValue = i
                        else:
                            finalValue = i + 1

                if count == 0:
                    if self.vraySettings.width.get() <= 40 * core:
                        value = math.ceil(self.vraySettings.width.get() / int(core))
                        if value <= 1:
                            value = 1
                        if pm.attributeQuery('sys_regsgen_xc', n='vraySettings', ex=True):
                            if not self.vraySettings.sys_regsgen_xc.get(lock=True):
                                self.vraySettings.sys_regsgen_xc.set(value)
                    else:
                        value = finalValue
                        if value <= 1:
                            value = 1
                        if pm.attributeQuery('sys_regsgen_xc', n='vraySettings', ex=True):
                            if not self.vraySettings.sys_regsgen_xc.get(lock=True):
                                self.vraySettings.sys_regsgen_xc.set(value)
                elif self.vraySettings.height.get() <= 40 * core:
                    value = math.ceil(self.vraySettings.height.get() / int(core))
                    if value <= 1:
                        value = 1
                    if pm.attributeQuery('sys_regsgen_yc', n='vraySettings', ex=True):
                        if not self.vraySettings.sys_regsgen_yc.get(lock=True):
                            self.vraySettings.sys_regsgen_yc.set(value)
                else:
                    value = finalValue
                    if value <= 1:
                        value = 1
                    if pm.attributeQuery('sys_regsgen_yc', n='vraySettings', ex=True):
                        if not self.vraySettings.sys_regsgen_yc.get(lock=True):
                            self.vraySettings.sys_regsgen_yc.set(value)
                count += 1

            if pm.attributeQuery('sys_regsgen_seqtype', n='vraySettings', ex=True):
                if not self.vraySettings.sys_regsgen_seqtype.get(lock=True):
                    self.vraySettings.sys_regsgen_seqtype.set(3)
            line = 'python("import maya.cmds as cmds\\nvalue = cmds.memory(phy=True, megaByte=True)\\nif isinstance( value, int ):\\n\\tmemory = float(value)\\nelse:\\n\\tmemory = float(value[0])");\nfloat $memory = `python "memory"`;\nvraySettings.sys_rayc_dynMemLimit = $memory - 1500;'
            if not pm.objExists('deeXVrayFastExpression'):
                pm.expression(n='deeXVrayFastExpression', s=line)
            else:
                actualExpression = pm.expression('deeXVrayFastExpression', s=True, query=True)
                if line not in actualExpression:
                    pm.expression('deeXVrayFastExpression', edit=True, s=actualExpression + '\n' + line)
        else:
            line = 'python("import maya.cmds as cmds\\nvalue = cmds.memory(phy=True, megaByte=True)\\nif isinstance( value, int ):\\n\\tmemory = float(value)\\nelse:\\n\\tmemory = float(value[0])");\nfloat $memory = `python "memory"`;\nvraySettings.sys_rayc_dynMemLimit = $memory - 1500;'
            if pm.objExists('deeXVrayFastExpression'):
                actualExpression = pm.expression('deeXVrayFastExpression', s=True, query=True)
                if line in actualExpression:
                    pm.expression('deeXVrayFastExpression', edit=True, s=actualExpression.replace(line, ''))



    def changePresetPreComp(self):
        if not self.bashMode:
            value = pm.optionMenu(self.UI.preCompNuke_CB, query=True, value=True)
            pm.setAttr('vraySettings.deeXVrayFastLastPresetPreComp', value, type='string')
            self.actualPresetPrecomp = value
        else:
            pm.setAttr('vraySettings.deeXVrayFastLastPresetPreComp', self.actualPresetPrecomp, type='string')
        self.preCompInit()
        self.refresh()



    def getImageFiles(self):
        workspaceRoot = pm.workspace(q=True, rootDirectory=True)
        workspacePaths = pm.workspace(q=True, rt=True)
        imgPath = ''
        for i in range(0, len(workspacePaths)):
            if workspacePaths[i] == 'images':
                imgPath = workspacePaths[(i + 1)]
                break

        lastChar = workspaceRoot[-1]
        if lastChar != '/' and lastChar != '\\':
            workspaceRoot = workspaceRoot + '/'
        imagePath = workspaceRoot + imgPath + '/'
        imgExt = pm.getAttr('vraySettings.imageFormatStr')
        if imgExt == '' or imgExt is None:
            imgExt = 'png'
        imgExt = imgExt.split(' ')[0]
        prefix = pm.getAttr('vraySettings.fileNamePrefix')
        if prefix == '(not set; using filename)' or prefix == '' or prefix is None:
            prefix = pm.mel.eval('getSceneName')
        prefix = pm.mel.eval('vrayTransformFilename("' + prefix + '", "persp", "", 0);')
        separate = True
        if pm.getAttr('vraySettings.relements_separateFolders') == 0:
            separate = False
        finalImageName = [imagePath,
         prefix,
         imgExt,
         separate]
        framePadding = pm.getAttr('vraySettings.fileNamePadding')
        if pm.getAttr('defaultRenderGlobals.animation') == 1:
            finalImageName = [imagePath,
             prefix,
             '#' * framePadding + '.' + imgExt,
             separate]
        return finalImageName



    def deexVrayFastAutoUpdate(self):
        now = datetime.date.today()
        now2 = datetime.datetime.now()
        nowString = str(now.year) + ',' + str(now.month) + ',' + str(now.day)
        doUpdate = False
        if 'DEEX_VRAY_FAST_LASTUPDATE_DATE' in os.environ:
            lastUpdate = os.environ['DEEX_VRAY_FAST_LASTUPDATE_DATE']
            lastDatetime = datetime.datetime(int(lastUpdate.split(',')[0]), int(lastUpdate.split(',')[1]), int(lastUpdate.split(',')[2]))
            diff = now2 - lastDatetime
            OpenMaya.MGlobal.displayInfo('[Arsenal Quality] Your last update was at ' + lastUpdate + '.')
            if diff.days >= 15:
                OpenMaya.MGlobal.displayInfo("[Arsenal Quality] You doesn't update since " + str(diff.days) + ' days.')
                doUpdate = True
        else:
            doUpdate = True
        if doUpdate:
            if self.deexVrayFastUpdate():
                os.environ['DEEX_VRAY_FAST_LASTUPDATE_DATE'] = nowString



    def calculateAge(self, born):
        """Calculate the age of a user."""
        j = int(born.split(',')[0])
        m = int(born.split(',')[1])
        a = int(born.split(',')[2])
        today = datetime.date.today()
        birthday = datetime.date(a, m, j)
        if today.month < birthday.month:
            return str(today.year - a - 1) + ' years old'
        if today.month == birthday.month:
            if today.day > birthday.day:
                return str(today.year - a - 1) + ' years old'
            else:
                if today.day == birthday.day:
                    return str(today.year - a - 1) + ' years old.\nIt is my birthday today !\nSay happy birthday Damien'
                return str(today.year - a) + ' years old'
        else:
            return str(today.year - a) + ' years old'



    def deexVrayFastAbout(self):
        myAge = self.calculateAge('26,9,1986')
        aboutMessage = 'Deex Vray Fast was created by Damien Bataille, alias DeeX.\n'
        aboutMessage += 'This tool is Free and can be found on www.deex.info\n'
        aboutMessage += "If you like this tool, don't hesitate to say thank and encourage me by email.\n"
        aboutMessage += 'I am a french lighting TD and lookDev TD, ' + myAge + '.\n'
        aboutMessage += 'I will look for a job in VFX in Canada or USA in 2012.\n'
        aboutMessage += 'If you are interested to work with me, contact me.\n'
        aboutMessage += 'Deex'
        pm.confirmDialog(title='About', message=aboutMessage, button=['Close'], defaultButton='Close', cancelButton='Close', dismissString='Close')




