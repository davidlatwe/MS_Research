
for mat in cmds.ls(sl= 1):
	fNode = cmds.listConnections(mat + '.color', p= 1)
	if fNode:
		cmds.connectAttr(fNode[0], mat + '.transparency')