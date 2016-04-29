import sys
sys.path.insert(0, 'A:/script/maya_projectTools')
import mMaya.mOutliner as mOutliner
reload(mOutliner)
import mMaya.mGeneral as mGeneral
reload(mGeneral)


mGC_namespace = ':mGeoCache'

# 先檢查 list 是否為空的，再轉 set
def _set(mylist):
	return set(mylist) if mylist else None

''' remove mGC namespace '''
mGeneral.namespaceDel(mGC_namespace)

''' start procedure '''
# get selection's root transform node
for rootNode in mOutliner.findRoot('transform'):
	# meshes need to process
	anim_meshes = []
	# meshes have visible animation
	anim_viskey = []
	# intermediate objects
	itrm_meshes = []
	
	''' intermediate objects '''
	# list intermediate objects
	itrm_meshes = _set(mOutliner.findIMObj(rootNode))
	# remove intermediate objects
	anim_meshes = _set(cmds.listRelatives(rootNode, ad= 1, f= 1, typ= 'mesh')) - itrm_meshes

	''' object visibility '''
	# list hidden objects
	for obj in mOutliner.findHidden(rootNode):
		# check if visibility being connected
		if not cmds.listConnections(obj + '.visibility'):
			''' NONE visibility control '''
			# nothing connected to visibility, check if something parented with it
			if cmds.objectType(obj) == 'transform':
				hiddenChild = _set(cmds.listRelatives(obj, ad= 1, f= 1))
				if hiddenChild:
					anim_meshes = anim_meshes - hiddenChild
			if cmds.objectType(obj) == 'mesh':
				anim_meshes.remove(obj)
		else:
			''' HAVE visibility control '''
			# do something if has key or expression connected to visibility
			anim_viskey.append(obj)

	''' Add and Set namespace '''
	mGeneral.namespaceSet(mGC_namespace)
	
	''' polyUnite '''
	# create a group for polyUnite meshes
	ves_top = cmds.group(em= 1, n= rootNode.split(':')[-1])

	for child in anim_meshes:
		child_basename = child.split(':')[-1]
		ves = cmds.polyCube(n= child_basename, ch= 0)[0]
		namespace_source = ':'.join(rootNode.split(':')[:-1])
		child_source = namespace_source + ':' + child_basename
		cmds.parent(ves, ves_top)
		pUnite = 'polyUnite_' + child_basename
		pUnite = cmds.createNode('polyUnite', n= pUnite)
		cmds.connectAttr(child_source + '.worldMatrix', pUnite + '.inputMat[0]')
		cmds.connectAttr(child_source + '.worldMesh', pUnite + '.inputPoly[0]')
		cmds.connectAttr(pUnite + '.output', ves + '.inMesh')

	''' GeoCache '''


	''' remove mGC namespace '''
	#mGeneral.namespaceDel(mGC_namespace)