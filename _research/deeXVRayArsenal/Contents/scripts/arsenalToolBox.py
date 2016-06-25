import os
import pymel.all as pm
import maya.OpenMaya as OpenMaya
import hashlib

def arsenal_proxyMultiImporter(files = list()):
    if not files:
        vrmeshFilter = '*.vrmesh'
        selectedFile = pm.fileDialog2(fileFilter=vrmeshFilter, dialogStyle=2, okCaption='Load', fileMode=4, returnFilter=True, caption='Vray proxy multi importer')
    else:
        selectedFile = files
    if selectedFile is not None:
        for myFile in selectedFile:
            if myFile != '*.vrmesh':
                fileName = os.path.basename(myFile)
                pm.mel.eval('vrayCreateProxyExisting("' + fileName + '", "' + myFile + '")')
                print '[Arsenal ToolBox] Proxy ' + myFile + ' imported.'




def arsenal_proxyShaderAutoConnect(ignoreNamespace = False):
    if ignoreNamespace:
        print '[Arsenal ToolBox] Namespace ignored'
    else:
        print '[Arsenal ToolBox] Namespace not ignored'
    proxyMaterialNodes = pm.ls(type='VRayMeshMaterial')
    allMaterials = pm.ls(materials=True)
    materialClean = list(set(allMaterials) - set(proxyMaterialNodes))
    if len(proxyMaterialNodes) == 0:
        OpenMaya.MGlobal.displayWarning('No VRayMeshMaterial in the scene !')
    for proxyMaterialNode in proxyMaterialNodes:
        numberOfSlot = proxyMaterialNode.shaderNames.get(size=True)
        for i in range(numberOfSlot):
            nameSlot = pm.getAttr(proxyMaterialNode + '.shaderNames[' + str(i) + ']')
            if pm.connectionInfo(proxyMaterialNode + '.shaders[' + str(i) + ']', isDestination=True):
                connected = pm.connectionInfo(proxyMaterialNode + '.shaders[' + str(i) + ']', sourceFromDestination=True)
                pm.disconnectAttr(connected, proxyMaterialNode + '.shaders[' + str(i) + ']')
                print '[Arsenal ToolBox] Disconnect ' + proxyMaterialNode + '.shaders[' + str(i) + ']'
            for myMat in materialClean:
                okConnect = False
                if ignoreNamespace:
                    if myMat.split(':')[-1] == nameSlot.split(':')[-1]:
                        okConnect = True
                elif myMat == nameSlot:
                    okConnect = True
                if okConnect:
                    pm.connectAttr(myMat + '.outColor', proxyMaterialNode + '.shaders[' + str(i) + ']', f=True)
                    print '[Arsenal ToolBox] ' + proxyMaterialNode + '.shaders[' + str(i) + '] connected.'






def arsenal_materialIDaddSelection():
    selections = pm.ls(materials=True, type='shadingEngine', sl=True)
    arsenal_materialIDadd(selection=selections)



def arsenal_materialIDaddAllMat():
    selections = pm.ls(materials=True)
    arsenal_materialIDadd(selection=selections)



def arsenal_materialIDaddAllSG():
    selections = pm.ls(type='shadingEngine')
    arsenal_materialIDadd(selection=selections)



def arsenal_materialIDadd(selection = list()):
    if len(selection) == 0 or selection is None:
        OpenMaya.MGlobal.displayError('[Arsenal ToolBox] No material(s) node(s) or shading(s) engine node(s) selected or found.')
        return 
    for mySelect in selection:
        if pm.objectType(mySelect) in ('particleCloud', 'shaderGlow', 'hairTubeShader', 'layeredShader', 'oceanShader', 'useBackground'):
            print '[Arsenal ToolBox] ' + mySelect.name() + ' must not have materialID.'
            continue
        pm.mel.eval('vray addAttributesFromGroup ' + mySelect.name() + ' vray_material_id 1;')
        print '[Arsenal ToolBox] Add material ID attributes to ' + mySelect.name()




def arsenal_materialIDsetSelection():
    selections = pm.ls(materials=True, type='shadingEngine', sl=True)
    arsenal_materialIDset(selection=selections)



def arsenal_materialIDsetAllMat():
    selections = pm.ls(materials=True)
    arsenal_materialIDset(selection=selections)



def arsenal_materialIDsetAllSG():
    selections = pm.ls(type='shadingEngine')
    arsenal_materialIDset(selection=selections)



def arsenal_materialIDset(selection = list()):
    if len(selection) == 0 or selection is None:
        OpenMaya.MGlobal.displayError('[Arsenal ToolBox] No material(s) node(s) or shading(s) engine node(s) selected or found.')
        return 
    for mySelect in selection:
        if pm.objectType(mySelect) in ('particleCloud', 'shaderGlow', 'hairTubeShader', 'layeredShader', 'oceanShader', 'useBackground'):
            print '[Arsenal ToolBox] ' + mySelect.name() + ' must not have materialID.'
            continue
        if not pm.attributeQuery('vrayColorId', n=mySelect.name(), ex=True) or not pm.attributeQuery('vrayMaterialId', n=mySelect.name(), ex=True):
            print '[Arsenal ToolBox] Material ID attributes of ' + mySelect.name() + " doen't exist."
            continue
        if mySelect.vrayColorId.isLocked() or mySelect.vrayMaterialId.isLocked():
            print '[Arsenal ToolBox] Material ID attributes of ' + mySelect.name() + ' is locked.'
            continue
        (multimatteID, rgb,) = arsenal_generateNumberFromString(string=mySelect.name())
        if multimatteID is None:
            OpenMaya.MGlobal.displayError('[Arsenal ToolBox] Can set ID.')
            return 
        if not mySelect.vrayColorId.isLocked():
            mySelect.vrayColorId.set(rgb[0], rgb[1], rgb[2], type='double3')
            print '[Arsenal ToolBox] vrayColorId attributes of ' + mySelect.name() + ' setted.'
        else:
            print '[Arsenal ToolBox] vrayColorId attributes of ' + mySelect.name() + ' is locked. Skipped.'
        if not mySelect.vrayMaterialId.isLocked():
            mySelect.vrayMaterialId.set(multimatteID)
            print '[Arsenal ToolBox] vrayMaterialId attributes of ' + mySelect.name() + ' setted.'
        else:
            print '[Arsenal ToolBox] vrayMaterialId attributes of ' + mySelect.name() + ' is locked. Skipped.'




def arsenal_materialIDdeleteSelection():
    selections = pm.ls(materials=True, type='shadingEngine', sl=True)
    arsenal_materialIDdelete(selection=selections)



def arsenal_materialIDdeleteAllMat():
    selections = pm.ls(materials=True)
    arsenal_materialIDdelete(selection=selections)



def arsenal_materialIDdeleteAllSG():
    selections = pm.ls(type='shadingEngine')
    arsenal_materialIDdelete(selection=selections)



def arsenal_materialIDdelete(selection = list()):
    if len(selection) == 0 or selection is None:
        OpenMaya.MGlobal.displayError('[Arsenal ToolBox] No material(s) node(s) or shading(s) engine node(s) selected or found.')
        return 
    for mySelect in selection:
        if pm.objectType(mySelect) in ('particleCloud', 'shaderGlow', 'hairTubeShader', 'layeredShader', 'oceanShader', 'useBackground'):
            print '[Arsenal ToolBox] ' + mySelect.name() + ' must not have materialID.'
            continue
        if not pm.attributeQuery('vrayColorId', n=mySelect.name(), ex=True) or not pm.attributeQuery('vrayMaterialId', n=mySelect.name(), ex=True):
            print '[Arsenal ToolBox] Material ID attributes of ' + mySelect.name() + " doen't exist."
            continue
        if mySelect.vrayColorId.isLocked() or mySelect.vrayMaterialId.isLocked():
            print '[Arsenal ToolBox] Material ID attributes of ' + mySelect.name() + ' is locked.'
            continue
        pm.mel.eval('vray addAttributesFromGroup ' + mySelect.name() + ' vray_material_id 0;')
        print '[Arsenal ToolBox] Remove material ID attributes to ' + mySelect.name()




def arsenal_objectIDaddSelection():
    selections = pm.ls(geometry=True, sl=True)
    arsenal_objectIDaddAll(selection=selections)



def arsenal_objectIDaddAllMeshs():
    selections = pm.ls(geometry=True)
    arsenal_objectIDaddAll(selection=selections)



def arsenal_objectIDaddAll(selection = list()):
    if len(selection) == 0 or selection is None:
        OpenMaya.MGlobal.displayError('[Arsenal ToolBox] No mesh(s) selected or found. Select mesh(s), not transform(s).')
        return 
    for mySelect in selection:
        pm.mel.eval('vray addAttributesFromGroup ' + mySelect.name() + ' vray_objectID 1;')
        print '[Arsenal ToolBox] Add object ID attributes to ' + mySelect.name()




def arsenal_objectIDsetSelection():
    selections = pm.ls(geometry=True, sl=True)
    arsenal_objectIDset(selection=selections)



def arsenal_objectIDsetAllMeshs():
    selections = pm.ls(geometry=True)
    arsenal_objectIDset(selection=selections)



def arsenal_objectIDset(selection = list()):
    if len(selection) == 0 or selection is None:
        OpenMaya.MGlobal.displayError('[Arsenal ToolBox] No mesh(s) selected or found. Select mesh(s), not transform(s).')
        return 
    for mySelect in selection:
        if not pm.attributeQuery('vrayObjectID', n=mySelect.name(), ex=True):
            print '[Arsenal ToolBox] Object ID attributes of ' + mySelect.name() + " doen't exist."
            continue
        if mySelect.vrayObjectID.isLocked():
            print '[Arsenal ToolBox] Object ID attributes of ' + mySelect.name() + ' is locked.'
            continue
        objectID = arsenal_generateNumberFromString(string=mySelect.name())
        if objectID is None:
            OpenMaya.MGlobal.displayError('[Arsenal ToolBox] Can set ID.')
            return 
        mySelect.vrayObjectID.set(objectID[0])
        print '[Arsenal ToolBox] Object ID attributes of ' + mySelect.name() + ' setted.'




def arsenal_objectIDremoveSelection():
    selections = pm.ls(geometry=True, sl=True)
    arsenal_objectIDremove(selection=selections)



def arsenal_objectIDremoveAllMeshs():
    selections = pm.ls(geometry=True)
    arsenal_objectIDremove(selection=selections)



def arsenal_objectIDremove(selection = list()):
    if len(selection) == 0 or selection is None:
        OpenMaya.MGlobal.displayError('[Arsenal ToolBox] No mesh(s) selected or found. Select mesh(s), not transform(s).')
        return 
    for mySelect in selection:
        if not pm.attributeQuery('vrayObjectID', n=mySelect.name(), ex=True):
            print '[Arsenal ToolBox] Object ID attributes of ' + mySelect.name() + " doen't exist."
            continue
        if mySelect.vrayObjectID.isLocked():
            print '[Arsenal ToolBox] Object ID attributes of ' + mySelect.name() + ' is locked.'
            continue
        pm.mel.eval('vray addAttributesFromGroup ' + mySelect.name() + ' vray_objectID 0;')
        print '[Arsenal ToolBox] Remove object ID attributes to ' + mySelect.name()




def arsenal_materialControl(arsenal = None, selectionAll = False, valueReflecSub = None, valueRefracSub = None, valueReflecInt = None, valueRefracInt = None, valueReflecDepth = None, valueRefracDepth = None, mode = None):
    if arsenal is None:
        OpenMaya.MGlobal.displayError('[Arsenal ToolBox] Arsenal not found.')
        return 
    if selectionAll:
        selection = pm.ls(materials=True)
    else:
        selection = pm.ls(materials=True, sl=True)
    if mode == 1:
        allAttr = {'subdivs': valueReflecSub,
         'traceDepth': valueReflecDepth,
         'reflectionSubdivs': valueReflecSub,
         'reflInterpolation': valueReflecInt,
         'reflectionsMaxDepth': valueReflecDepth}
    elif mode == 2:
        allAttr = {'refractionSubdivs': valueRefracSub,
         'refrInterpolation': valueRefracInt,
         'refractionsMaxDepth': valueRefracDepth}
    for attr in allAttr:
        arsenal.setSimpleValue(selection=selection, attribute=attr, value=allAttr[attr], message='Material : value ' + str(allAttr[attr]) + ' setted for attribute ' + attr)




def arsenal_lightControl(arsenal = None, selectionAll = False, value = None):
    if arsenal is None:
        OpenMaya.MGlobal.displayError('[Arsenal ToolBox] Arsenal not found.')
        return 
    selection = list()
    if selectionAll:
        selection = pm.ls(type=pm.listNodeTypes('light'))
    else:
        selectionTMP = pm.ls(sl=True)
        for sel in selectionTMP:
            if pm.objectType(sel) in pm.listNodeTypes('light'):
                selection.append(sel)
            else:
                shape = pm.listRelatives(sel, shapes=True)
                if len(shape) != 0:
                    selection.append(shape[0])

    allAttr = {'shadowRays': value,
     'subdivs': value}
    for attr in allAttr:
        arsenal.setSimpleValue(selection=selection, attribute=attr, value=allAttr[attr], message='Light : value ' + str(allAttr[attr]) + ' setted for attribute ' + attr)




def arsenal_generateNumberFromString(string = None):
    if string is None:
        OpenMaya.MGlobal.displayError('[Arsenal ToolBox] String name is None.')
        return 
    if ':' in string:
        striped = string.split(':')[-1]
    else:
        striped = string
    strToMd5 = hashlib.md5(str(striped)).hexdigest()
    finalNum = 0
    for letter in strToMd5:
        if letter.isdigit():
            finalNum += int(letter)
        else:
            finalNum += ord(letter)

    ID = pm.mel.eval('seed(' + str(finalNum) + ');')
    myVector = pm.mel.eval('sphrand(1);')
    rCol = float(abs(myVector[0]))
    gCol = float(abs(myVector[1]))
    bCol = float(abs(myVector[2]))
    return (ID, [rCol, gCol, bCol])



