import os
import shutil
import re
import pymel.all as pm
import maya.OpenMaya as OpenMaya

class ArsenalPassMultiMatte(object):

    def __init__(self):
        self.multimatteMaskMembersRed = list()
        self.multimatteMaskMembersGreen = list()
        self.multimatteMaskMembersBlue = list()




class ArsenalPass(object):

    def __init__(self):
        self.passName = None
        self.passMembers = list()
        self.blackHoleMembers = list()
        self.blackHoleMembersReceiveShd = list()
        self.giMembersGenerate = list()
        self.giMembersReceive = list()
        self.primaryMembersOff = list()
        self.reflectionMembersOff = list()
        self.refractionMembersOff = list()
        self.shadowCastsMembersOff = list()
        self.lightSelectNormalMembers = list()
        self.lightSelectDiffuseMembers = list()
        self.lightSelectRawMembers = list()
        self.lightSelectSpecularMembers = list()
        self.lightSelectAllNormal = None
        self.lightSelectAllDiffuse = None
        self.lightSelectAllRaw = None
        self.lightSelectAllSpecular = None
        self.giOn = None
        self.primaryEngine = None
        self.secondaryEngine = None
        self.imap_detailEnhancement = None
        self.aoOn = None
        self.globopt_mtl_glossy = None
        self.globopt_mtl_reflectionRefraction = None
        self.globopt_mtl_doMaps = None
        self.globopt_light_doShadows = None
        self.aaFilterOn = None
        self.globopt_geom_displacement = None
        self.cam_mbOn = None
        self.cam_dofOn = None
        self.cam_overrideEnvtex = None
        self.vrayLambert = None
        self.sys_distributed_rendering_on = None
        self.vrayMaterialID = None
        self.vrayProxyObjectID = None
        self.multimatteMaskName = {}
        self.multimatteMaskMembers = {}




class Arsenal(object):

    def __init__(self, ui = None):
        self.ui = ui
        self.passName = {}
        self.progressBarValue = 0
        self.arsenalQuality = None



    def initialize(self):
        if pm.objExists('vraySettings'):
            if pm.getAttr('defaultRenderGlobals.currentRenderer') == 'vray':
                self.arsenalQuality.initializeSet()
                if not self.initializePythonScript():
                    OpenMaya.MGlobal.displayError('[Arsenal] You must to upgrade your Vray')
                    return False
                self.loadArsenalPlugin()
                return True
            else:
                result = pm.confirmDialog(title='Set Vray', message='Vray is not your current render engine, set Vray to the current engine ?\n', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
                if result == 'OK':
                    self.loadVray()
                    self.arsenalQuality.initializeSet()
                    if not self.initializePythonScript():
                        OpenMaya.MGlobal.displayError('[Arsenal] You must to upgrade your Vray')
                        return False
                    self.loadArsenalPlugin()
                    return True
                OpenMaya.MGlobal.displayError('[Arsenal] Can not switch to Vray engine')
                return False
        elif pm.getAttr('defaultRenderGlobals.currentRenderer') == 'vray':
            result = pm.confirmDialog(title='Vray setting', message='Vray settings not found, reload Vray properly ?\n', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
            if result == 'OK':
                self.loadVray()
                self.arsenalQuality.initializeSet()
                if not self.initializePythonScript():
                    OpenMaya.MGlobal.displayError('[Arsenal] You must to upgrade your Vray')
                    return False
                self.loadArsenalPlugin()
                return True
            else:
                OpenMaya.MGlobal.displayError('[Arsenal] vraySetting not found')
                return False
        else:
            result = pm.confirmDialog(title='Load Vray', message='Vray is not your current render engine, load Vray ?\n(take some seconds)', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
            if result == 'OK':
                self.loadVray()
                self.arsenalQuality.initializeSet()
                if not self.initializePythonScript():
                    OpenMaya.MGlobal.displayError('[Arsenal] You must to upgrade your Vray')
                    return False
                self.loadArsenalPlugin()
                return True
            else:
                OpenMaya.MGlobal.displayError('[Arsenal] Vray not loaded')
                return False



    def initializePythonScript(self):
        if not pm.objExists('vraySettings.postTranslatePython'):
            return False
        pm.setAttr('vraySettings.postTranslatePython', lock=False)
        actualValue = pm.getAttr('vraySettings.postTranslatePython')
        toAdd = ''
        if 'import arsenalFunction;' not in actualValue:
            toAdd += 'import arsenalFunction;'
        if 'reload(arsenalFunction);' not in actualValue:
            toAdd += 'reload(arsenalFunction);'
        if 'arsenalFunction.arsenalFunction();' not in actualValue:
            toAdd += 'arsenalFunction.arsenalFunction();'
        pm.setAttr('vraySettings.postTranslatePython', toAdd + actualValue)
        if pm.control('vrayPostTranslatePythonCallbackControl', query=True, ex=True):
            pm.scrollField('vrayPostTranslatePythonCallbackControl', edit=True, text=toAdd)
        return True



    def loadArsenalPlugin(self):
        pm.loadPlugin('arsenalPass.mll', quiet=True)



    def loadVray(self):
        pm.loadPlugin('vrayformaya.mll', quiet=True)
        pm.setAttr('defaultRenderGlobals.currentRenderer', 'vray', type='string')
        pm.mel.eval('vrayCreateVRaySettingsNode();')



    def initAttributes(self, attribut = None, renderPass = None, connection = False, fromRenderGlobal = False):
        if attribut is None and renderPass is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select a pass')
            return 
        arsenalPass = pm.PyNode(renderPass + '_arsenalPass')
        if not connection:
            if fromRenderGlobal:
                value = pm.getAttr('vraySettings.' + attribut)
            else:
                value = pm.getAttr(arsenalPass.name() + '.' + attribut)
        elif fromRenderGlobal:
            value = pm.listConnections('vraySettings.' + attribut, destination=False, source=True)
        else:
            value = pm.listConnections(arsenalPass.name() + '.' + attribut, destination=False, source=True)
        if renderPass not in self.passName:
            self.passName[renderPass] = ArsenalPass()
            self.passName[renderPass].passName = renderPass
            self.multiMatteAttributes(myRenderLayer=renderPass)
        cmd = 'self.passName[renderPass].' + str(attribut) + ' = ' + str(value).replace('nt.', 'pm.nt.')
        exec cmd



    def exportPass(self, layers = list(), path = None):
        if not layers:
            OpenMaya.MGlobal.displayError('[Arsenal] Please select pass')
            return 
        if not path:
            return 
        splited = os.path.basename(path[0]).split('__')
        director = os.path.dirname(path[0])
        if '.arpass' in splited[-1] and len(splited) != 1:
            splited.pop(-1)
        cleaned = '_'.join(splited)
        for layer in layers:
            renderLayer = pm.PyNode(layer)
            suffix = '__' + renderLayer.name()
            finalPath = os.path.join(director, cleaned.split('.')[0] + suffix + '.arpass')
            toExport = layer + '_arsenalPass'
            pm.select(toExport, r=True)
            pm.exportSelected(finalPath, force=True, options='v=0;', type='mayaAscii', pr=True, constructionHistory=False, channels=False, constraints=False, expressions=False, shader=False)
            shutil.move(finalPath + '.ma', finalPath)
            pm.select(cl=True)
            objConnected = pm.listConnections(toExport, plugs=True, c=True)
            if not objConnected:
                continue
            info = {}
            dicConnect = {}
            infoLayer = {}
            infoLayer['name'] = layer
            infoLayer['global'] = renderLayer.g.get()
            listMembersLayer = {}
            for strMember in renderLayer.listMembers(fullNames=True):
                member = pm.PyNode(strMember)
                shortName = member.name()
                longName = member.longName()
                longNameWithoutNameSpace = pm.NameParser(longName).stripNamespace()
                shortNameWithoutNamespace = member.stripNamespace()
                listMembersLayer[str(longName)] = [str(longName),
                 str(shortName),
                 str(longNameWithoutNameSpace),
                 str(shortNameWithoutNamespace)]

            infoLayer['members'] = listMembersLayer
            dicConnect['layer'] = infoLayer
            for connect in objConnected:
                dst = connect[0].name()
                src = connect[1]
                srcNodeName = src.nodeName()
                srcAttrName = src.attrName(longName=True)
                srcShort = src.name()
                srcAttr = src.longName(fullPath=True)
                srcShortWithoutNamespace = src.node().stripNamespace() + '.' + srcAttr
                srcLong = src.node().longName() + '.' + srcAttr
                srcLongWithoutNamespace = pm.NameParser(srcLong).stripNamespace()
                if str(srcLong) in info:
                    actualDst = info[str(srcLong)]['destination']
                    actualDst.append(dst)
                    info[str(srcLong)] = {'destination': actualDst,
                     'sources': [str(srcLong),
                                 str(srcShort),
                                 str(srcLongWithoutNamespace),
                                 str(srcShortWithoutNamespace)]}
                else:
                    info[str(srcLong)] = {'destination': [dst],
                     'sources': [str(srcLong),
                                 str(srcShort),
                                 str(srcLongWithoutNamespace),
                                 str(srcShortWithoutNamespace)]}

            dicConnect['connections'] = info
            path = os.path.join(director, cleaned.split('.')[0] + suffix + '.arpassinfo')
            if self.writeTxtFile(path=path, text=str(dicConnect)):
                print '[Arsenal] ' + path + ' writed.'
            else:
                OpenMaya.MGlobal.displayError('[Arsenal] Can not write ' + path)
                return 




    def importPass(self, paths = list()):
        if not paths:
            return 
        for path in paths:
            splited = path.split('.')
            splited.pop(-1)
            arpassinfo = '.'.join(splited) + '.arpassinfo'
            strFile = self.readTxtFile(path=arpassinfo)
            objectsNotFound = []
            if strFile:
                dico = eval(strFile)
                if not pm.objExists(dico['layer']['name']):
                    renderLayer = pm.createRenderLayer(name=dico['layer']['name'], g=dico['layer']['global'])
                else:
                    renderLayer = pm.PyNode(dico['layer']['name'])
                arsenalPassName = renderLayer.name() + '_arsenalPass'
                if pm.objExists(arsenalPassName):
                    pm.lockNode(arsenalPassName, lock=False)
                    pm.delete(arsenalPassName)
                pm.importFile(path, defaultNamespace=True)
                if renderLayer.name() != 'defaultRenderLayer':
                    for member in dico['layer']['members']:
                        listMembers = dico['layer']['members'][member]
                        if pm.objExists(listMembers[0]):
                            renderLayer.addMembers(listMembers[0])
                        elif pm.objExists(listMembers[1]):
                            if len(pm.ls(listMembers[1])) == 1:
                                renderLayer.addMembers(listMembers[1])
                        elif pm.objExists(listMembers[2]):
                            if len(pm.ls(listMembers[2])) == 1:
                                renderLayer.addMembers(listMembers[2])
                        elif pm.objExists(listMembers[3]):
                            if len(pm.ls(listMembers[3])) == 1:
                                renderLayer.addMembers(listMembers[3])
                        else:
                            objectsNotFound.append(listMembers[0])

                for member in dico['connections']:
                    dicoMembers = dico['connections'][member]
                    dsts = dicoMembers['destination']
                    listMembers = dicoMembers['sources']
                    if pm.objExists(listMembers[0]):
                        for dst in dsts:
                            pm.connectAttr(listMembers[0], dst, f=True)

                    elif pm.objExists(listMembers[1]):
                        if len(pm.ls(listMembers[1])) == 1:
                            for dst in dsts:
                                pm.connectAttr(listMembers[1], dst, f=True)

                    elif pm.objExists(listMembers[2]):
                        if len(pm.ls(listMembers[2])) == 1:
                            for dst in dsts:
                                pm.connectAttr(listMembers[2], dst, f=True)

                    elif pm.objExists(listMembers[3]):
                        if len(pm.ls(listMembers[3])) == 1:
                            for dst in dsts:
                                pm.connectAttr(listMembers[3], dst, f=True)


            else:
                OpenMaya.MGlobal.displayError('[Arsenal] Can not open ' + arpassinfo)
                return 
            if objectsNotFound:
                OpenMaya.MGlobal.displayError('[Arsenal] Object(s) not found in the scene : \n' + '\n'.join(objectsNotFound))
                return 
            self.refreshArsenalPass()




    def createPass(self, name, g = False):
        if not self.checkStringName(text=name):
            OpenMaya.MGlobal.displayError('[Arsenal] You must to choose a valid name')
            return 
        if not pm.objExists(name):
            pm.createRenderLayer(name=name, g=g)
        pm.editRenderLayerGlobals(currentRenderLayer=name)
        pynode = pm.PyNode(name)
        if pynode not in self.passName:
            self.passName[pynode] = ArsenalPass()
            self.passName[pynode].passName = name
        return pynode



    def deletePass(self, layer = None):
        if layer is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select a pass')
            return 
        pm.editRenderLayerGlobals(currentRenderLayer='defaultRenderLayer')
        for dependance in pm.listConnections(layer + '.message', destination=True, source=False, type='arsenalPass'):
            pm.lockNode(dependance, lock=False)
            print '[Arsenal] ' + dependance + ' deleted.'
            pm.delete(dependance)

        if pm.objExists(layer):
            pm.delete(layer)
            print '[Arsenal] ' + layer + ' deleted.'
        if layer in self.passName:
            del self.passName[layer]



    def duplicatePass(self, layer = None, name = None):
        if layer is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select a pass')
            return 
        if name is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to enter a name')
            return 
        if not self.checkStringName(text=name):
            OpenMaya.MGlobal.displayError('[Arsenal] You must to choose a valid name')
            return 
        newLayer = pm.mel.eval('duplicate -ic -n ' + name + ' ' + self.passName[layer].passName)[0]
        pm.lockNode(self.passName[layer].passName + '_arsenalPass', lock=False)
        newArsenalPass = pm.mel.eval('duplicate -ic -n ' + name + '_arsenalPass ' + self.passName[layer].passName + '_arsenalPass')[0]
        pm.lockNode(self.passName[layer].passName + '_arsenalPass', lock=True)
        pm.lockNode(newArsenalPass, lock=True)
        pm.connectAttr(newLayer + '.message', newArsenalPass + '.passName', f=True)
        if pm.PyNode(newLayer) not in self.passName:
            self.passName[pm.PyNode(newLayer)] = ArsenalPass()
            self.passName[pm.PyNode(newLayer)].passName = newLayer
            self.selectPass(layer=pm.PyNode(newLayer))



    def changePropertyPass(self, layer = None, renderable = False):
        if layer is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select a pass')
            return 
        layer.renderable.set(renderable)



    def selectPass(self, layer = None):
        if layer is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select a pass')
            return 
        pm.editRenderLayerGlobals(currentRenderLayer=self.passName[layer].passName)



    def addObjects(self, selection = None, renderPass = None, attribute = None):
        if selection is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select some poly object(s)')
            return 
        if renderPass is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select a pass')
            return 
        self.multiMatteAttributes(myRenderLayer=renderPass)
        cmd = 'self.passName[renderPass].' + str(attribute) + ' = ' + str(selection).replace('nt.', 'pm.nt.')
        exec cmd
        exec 'newValue = self.passName[renderPass].' + str(attribute)
        arsenalPass = pm.PyNode(renderPass + '_arsenalPass.' + attribute)
        for mySelect in newValue:
            arrayList = arsenalPass.getArrayIndices()
            finalNumber = 0
            if arrayList:
                finalNumber = arrayList[-1] + 1
            if mySelect not in pm.listConnections(renderPass + '_arsenalPass.' + attribute, destination=False, source=True):
                pm.connectAttr(mySelect + '.message', renderPass + '_arsenalPass.' + attribute + '[' + str(finalNumber) + ']', f=True)

        print '[Arsenal] Object(s) add done.'



    def deleteObjects(self, selection = None, node = None, attribute = None):
        if selection is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select some poly object(s)')
            return 
        if node is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select a pass')
            return 
        for mySel in selection:
            for myConnected in pm.listConnections(node + '.' + attribute, shapes=True, connections=True):
                if mySel in myConnected:
                    pm.disconnectAttr(mySel + '.message', myConnected[0])


        print '[Arsenal] Object(s) delete done.'



    def selectObjects(self, node = None, attribute = None):
        if node is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select a pass')
            return 
        pm.select(cl=True)
        for myConnected in pm.listConnections(node + '.' + attribute, destination=False, source=True):
            pm.select(myConnected, add=True)

        print '[Arsenal] Object(s) selection done.'



    def checkStringName(self, text = ''):
        if re.match('^[A-Za-z0-9_-]*$', text) and text != '':
            return True
        else:
            return False



    def removeMultimatteMask(self, layer = None, number = None):
        if layer is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select a pass')
            return 
        actualList = pm.getAttr(layer + '_arsenalPass.multimatteMaskName')
        if actualList in ('default', '', ' '):
            actualList = '{}'
        actualList = eval(actualList)
        if number in actualList:
            actualList.pop(number)
        pm.setAttr(layer + '_arsenalPass.multimatteMaskName', str(actualList))



    def writeMultimatteMask(self, name = None, layer = None, number = None):
        if layer is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select a pass')
            return 
        actualList = pm.getAttr(layer + '_arsenalPass.multimatteMaskName')
        if actualList in ('default', '', ' '):
            actualList = '{}'
        actualList = eval(actualList)
        if len(actualList) != 0:
            if name in actualList.values() and number not in actualList:
                OpenMaya.MGlobal.displayError('[Arsenal] You must to choose an another name')
                return False
            if not self.checkStringName(text=name):
                OpenMaya.MGlobal.displayError('[Arsenal] You must to choose a valid name')
                return False
        actualList[number] = name
        pm.setAttr(layer + '_arsenalPass.multimatteMaskName', str(actualList))
        self.passName[pm.PyNode(layer)].multimatteMaskName = actualList
        return True



    def writeTxtFile(self, path = None, text = None):
        try:
            f = open(path, 'w')
            try:
                f.write(text)
            finally:
                f.close()
                return True
        except IOError:
            return False



    def readTxtFile(self, path = None):
        try:
            f = open(path, 'r')
            try:
                string = f.read()
            finally:
                f.close()
                return string
        except IOError:
            return False



    def setValue(self, renderPass = None, attribute = None, value = None):
        if renderPass is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select a pass')
            return 
        if attribute is None:
            OpenMaya.MGlobal.displayError('[Arsenal] Attribute not found on the pass')
            return 
        if value is None:
            OpenMaya.MGlobal.displayError('[Arsenal] No value gave to the pass')
            return 
        pm.setAttr(renderPass + '_arsenalPass.' + attribute, value)
        if pm.objExists('vraySettings.' + attribute):
            pm.setAttr('vraySettings.' + attribute, value)
            self.initAttributes(attribut=attribute, renderPass=renderPass, fromRenderGlobal=True)
        else:
            self.initAttributes(attribut=attribute, renderPass=renderPass)



    def setSimpleValue(self, selection = list(), attribute = None, value = None, message = None):
        if len(selection) == 0:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to have a selection')
            return 
        if attribute is None:
            OpenMaya.MGlobal.displayError('[Arsenal] Attribute not found')
            return 
        if value is None:
            OpenMaya.MGlobal.displayError('[Arsenal] No value gave')
            return 
        for sel in selection:
            if pm.objExists(sel + '.' + attribute):
                con = pm.listConnections(sel + '.' + attribute, d=False, s=True)
                if con:
                    if len(con) != 0:
                        return 
                print '[Arsenal] ' + str(sel) + ' :'
                pm.setAttr(sel + '.' + attribute, value)
                if message is not None:
                    print '         ' + message




    def overrideAttribute(self, renderPass = None, node = None, attribute = None, always = None):
        if renderPass is None:
            OpenMaya.MGlobal.displayError('[Arsenal] You must to select a pass')
            return 
        if attribute is None:
            OpenMaya.MGlobal.displayError('[Arsenal] Attribute not found on the pass')
            return 
        if node is None:
            OpenMaya.MGlobal.displayError('[Arsenal] Node not found')
            return 
        if always:
            pm.editRenderLayerAdjustment(node + '.' + attribute, layer=renderPass, remove=True)
        else:
            pm.editRenderLayerAdjustment(node + '.' + attribute, layer=renderPass)



    def isNotEmpty(self, value):
        return value is not None and len(value.strip()) > 0



    def refreshArsenalPassMember(self, myRenderLayer = None, progressBarUpdate = None):
        if myRenderLayer.name() != 'defaultRenderLayer':
            if pm.getAttr(myRenderLayer.name() + '.global') == 0:
                myMemberRenderLayer = myRenderLayer.listMembers(fullNames=True)
                if myMemberRenderLayer is None:
                    return 
                myMemberRenderLayer = list(set(myMemberRenderLayer))
                myMemberArsenalPass = pm.PyNode(myRenderLayer.name() + '_arsenalPass.passMembers').inputs(shapes=True)
                difference = list(set(myMemberRenderLayer).symmetric_difference(set(myMemberArsenalPass)))
                if difference:
                    for (i, myMember,) in enumerate(difference):
                        if not pm.PyNode(myMember + '.message').isConnectedTo(myRenderLayer.name() + '_arsenalPass.passMembers', checkOtherArray=True):
                            if progressBarUpdate is not None:
                                progressBarUpdate(numStep=len(difference), value=i, text='Pass ' + myRenderLayer.name() + ' step 1 : connect passMembers %v of %m ...')
                            pm.connectAttr(myMember + '.message', myRenderLayer.name() + '_arsenalPass.passMembers', force=True, nextAvailable=True)
                        else:
                            if progressBarUpdate is not None:
                                progressBarUpdate(numStep=len(difference), value=i, text='Pass ' + myRenderLayer.name() + ' step 1 : disconnect passMembers %v of %m ...')
                            pm.PyNode(myMember + '.message').disconnect(destination=myRenderLayer.name() + '_arsenalPass.passMembers', nextAvailable=True)




    def multiMatteAttributes(self, myRenderLayer = None, attributesConnectionArsenal = list()):
        if myRenderLayer in self.passName:
            for numMask in self.passName[myRenderLayer].multimatteMaskName.keys():
                self.passName[myRenderLayer].multimatteMaskMembers[numMask] = ArsenalPassMultiMatte()
                attributesConnectionArsenal.append('multimatteMaskMembers[' + str(numMask) + '].multimatteMaskMembersRed')
                attributesConnectionArsenal.append('multimatteMaskMembers[' + str(numMask) + '].multimatteMaskMembersGreen')
                attributesConnectionArsenal.append('multimatteMaskMembers[' + str(numMask) + '].multimatteMaskMembersBlue')




    def refreshArsenalPass(self, progressBarUpdate = None):
        allRenderLayers = pm.RenderLayer.listAllRenderLayers()
        for myRenderLayer in allRenderLayers:
            arsenalPassName = myRenderLayer.name() + '_arsenalPass'
            aresenalConnected = myRenderLayer.listConnections(destination=True, source=False, type='arsenalPass')
            ajustements = pm.editRenderLayerAdjustment(myRenderLayer, query=True, layer=True)
            if len(aresenalConnected) == 0:
                if not pm.objExists(arsenalPassName):
                    pm.createNode('arsenalPass', name=arsenalPassName)
                    pm.lockNode(arsenalPassName, lock=True)
                pm.connectAttr(myRenderLayer.name() + '.message', arsenalPassName + '.passName', force=True)
            elif str(aresenalConnected[0]) != arsenalPassName:
                pm.lockNode(aresenalConnected[0], lock=False)
                pm.rename(aresenalConnected[0], arsenalPassName)
                pm.lockNode(arsenalPassName, lock=True)
                self.passName[myRenderLayer].passName = myRenderLayer.name()
            attributesFastArsenal = ['lightSelectAllNormal',
             'lightSelectAllDiffuse',
             'lightSelectAllRaw',
             'lightSelectAllSpecular',
             'vrayLambert',
             'multimatteMaskName',
             'vrayMaterialID',
             'vrayProxyObjectID']
            attributesFastVray = ['giOn',
             'primaryEngine',
             'secondaryEngine',
             'imap_detailEnhancement',
             'aoOn',
             'globopt_mtl_glossy',
             'globopt_mtl_reflectionRefraction',
             'globopt_mtl_doMaps',
             'globopt_light_doShadows',
             'aaFilterOn',
             'globopt_geom_displacement',
             'cam_mbOn',
             'cam_dofOn',
             'cam_overrideEnvtex',
             'sys_distributed_rendering_on']
            attributesConnectionArsenal = ['passMembers',
             'blackHoleMembers',
             'blackHoleMembersReceiveShd',
             'giMembersGenerate',
             'giMembersReceive',
             'primaryMembersOff',
             'reflectionMembersOff',
             'refractionMembersOff',
             'shadowCastsMembersOff',
             'lightSelectNormalMembers',
             'lightSelectDiffuseMembers',
             'lightSelectRawMembers',
             'lightSelectSpecularMembers']
            self.multiMatteAttributes(myRenderLayer=myRenderLayer, attributesConnectionArsenal=attributesConnectionArsenal)
            for (i, attribut,) in enumerate(attributesFastArsenal):
                if progressBarUpdate is not None:
                    progressBarUpdate(numStep=100, value=i, text='Pass ' + myRenderLayer.name() + ' step 2 : init FastArsenal %v of %m ...')
                self.initAttributes(attribut=attribut, renderPass=myRenderLayer)

            for (i, attribut,) in enumerate(attributesFastVray):
                self.initAttributes(attribut=attribut, renderPass=myRenderLayer, fromRenderGlobal=True)
                if progressBarUpdate is not None:
                    progressBarUpdate(numStep=100, value=i, text='Pass ' + myRenderLayer.name() + ' step 3 : init FastVray %v of %m ...')
                if myRenderLayer.name() != 'defaultRenderLayer':
                    if ajustements is None or 'vraySettings.' + attribut not in ajustements:
                        self.overrideAttribute(renderPass=myRenderLayer, node=arsenalPassName, attribute=attribut, always=True)
                    else:
                        self.overrideAttribute(renderPass=myRenderLayer, node=arsenalPassName, attribute=attribut, always=False)

            for (i, attribut,) in enumerate(attributesConnectionArsenal):
                if progressBarUpdate is not None:
                    progressBarUpdate(numStep=100, value=i, text='Pass ' + myRenderLayer.name() + ' step 4 : init FastConnection %v of %m ...')
                self.initAttributes(attribut=attribut, renderPass=myRenderLayer, connection=True)

            if progressBarUpdate is not None:
                progressBarUpdate(numStep=100, value=100, text='Done...')





