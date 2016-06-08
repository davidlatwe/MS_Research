print 'colorSetIndices : ' + str(cmds.polyCompare(ic= 1))
print '      colorSets : ' + str(cmds.polyCompare(c= 1))
print '          edges : ' + str(cmds.polyCompare(e= 1))
print '       faceDesc : ' + str(cmds.polyCompare(fd= 1))
print '    userNormals : ' + str(cmds.polyCompare(un= 1))
print '   uvSetIndices : ' + str(cmds.polyCompare(iuv= 1))
print '         uvSets : ' + str(cmds.polyCompare(uv= 1))
print '       vertices : ' + str(cmds.polyCompare(v= 1))


import maya.api.OpenMaya as om2

selectionLs = om2.MGlobal.getActiveSelectionList()
mesh = []
for id in selectionLs:
    print id
    selObj = selectionLs.getDagPath(id)
    mfnObject = om2.MFnMesh(dag)
    vertexCount, vertexList = mfnObject.getVertices()
    mesh[len(mesh)] = vertexList

for id in len(mesh[0]):
    print id