import pymel.core as PM
import socket

def getShadingGroupMembership():
    '''
    Get a dictionary of shading group set information
    {'shadingGroup': [assignmnet1, assignment2...]}
    '''
    result = {}
    #sgs = PM.ls(sl= 1, et='shadingEngine')
    sgs = PM.listConnections(s= 1, t='shadingEngine')
    for sg in sgs:
        result[sg.name()] = sg.members(flatten=True)
    return result

def remoteMaye(msg):
    global maya
    maya.send(msg)

def vmtl_nameMap(name):
    whiteList = ['woman_Rig:surfaceShader1',
                 'lady_Rig:surfaceShader1',
                 'richman_rigging_master:richman_spot',
                 'oldman_Rig:surfaceShader1']
    if name == 'oldman_Rig:VRayMtl2':
        name = 'richPeopleSuck:oldman_cloth_vmtl'
    if name == 'oldman_Rig:VRayMtl3':
        name = 'richPeopleSuck:oldman_skin_vmtl'
    if name == 'oldman_Rig:VRayMtl4':
        name = 'richPeopleSuck:oldman_glass_vmtl'
    if name == 'lady_Rig:VRayMtl2':
        name = 'richPeopleSuck:lady_cloth_vmtl'
    if name == 'lady_Rig:VRayMtl1':
        name = 'richPeopleSuck:lady_skin_vmtl'
    if name == 'woman_Rig:VRayMtl1':
        name = 'richPeopleSuck:woman_cloth_vmtl'
    if name == 'woman_Rig:VRayMtl2':
        name = 'richPeopleSuck:woman_skin_vmtl'
    if name == 'richman_rigging_master:VRayMtl2':
        name = 'richPeopleSuck:richman_cloth_vmtl'
    if name == 'richman_rigging_master:VRayMtl1':
        name = 'richPeopleSuck:richman_skin_vmtl'
    if name == 'richman_rigging_master:surfaceShader3':
        name = 'richPeopleSuck:maneye_black_surface'
    if name in whiteList:
        name = 'richPeopleSuck:maneye_white_surface'

    return name


def doJob(port):

    host = "127.0.0.1"
    global maya
    maya = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    maya.connect( (host, port) )

    mtlDict = getShadingGroupMembership()

    for meshList in mtlDict.keys():
        vmtl = cmds.listConnections(meshList + '.surfaceShader', s= 1)[0]
        if mtlDict[meshList]:
            for mesh in mtlDict[meshList]:
                msg = ''
                target = ''
                if '.' in str(mesh):
                    faceList = []
                    faceStr = str(mesh).split('.f')[1].replace('[', '').replace(']', '')
                    if ',' in faceStr:
                        faceList = faceStr.split(',')
                    else:
                        faceList = [faceStr]
                    for face in faceList:
                        target = str(mesh).split('.')[0] + '.f[' + face + ']'
                        try:
                            msg += 'cmds.select("' + target + '", r= 1)\n'
                            msg += 'cmds.hyperShade(a= "' + vmtl_nameMap(vmtl) + '")\n'
                        except:
                            if len(target.split(':')) > 1:
                                target_1 = ':'.join(target.split(':')[0:2]) + ']'
                                target_2 = ':'.join([target.split(':')[0], target.split(':')[2]])
                                try:
                                    msg += 'cmds.select("' + target_1 + '", r= 1)\n'
                                    msg += 'cmds.hyperShade(a= "' + vmtl_nameMap(vmtl) + '")\n'
                                except:
                                    print '+++++++++++++++++++++++++++++++++++++\n+++++++++++++++++++++++++++++++++++++'
                else:
                    target = str(mesh)
                    msg += 'cmds.select("' + target + '", r= 1)\n'
                    msg += 'cmds.hyperShade(a= "' + vmtl_nameMap(vmtl) + '")\n'

                remoteMaye(msg)

    maya.close()