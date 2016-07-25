import pymel.core as pm
pm.select(cl= 1)
for mesh in pm.ls(g= 1):
	if pm.objectType(mesh) == 'mesh' and pm.getAttr(mesh.name() + '.displaySmoothMesh'):
		pm.select(mesh, add= 1)