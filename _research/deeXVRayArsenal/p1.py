
# arsenalUI.py 1148
def goAddLightSelectDiffuse(self):
	currentPass = self.ui.arsenal_listPass.selectedItems()
	currentSelection = pm.ls(sl=True, l=True, dag=True, fl=True, type=pm.listNodeTypes('light'))
	if not currentSelection:
	    OpenMaya.MGlobal.displayError('[Arsenal] Please select light(s).')
	    return 
	for selec in currentPass:
	    passName = pm.PyNode(str(selec.text()))
	    self.arsenal.addObjects(selection=currentSelection, renderPass=passName, attribute='lightSelectDiffuseMembers')

	self.refreshObjectsUI()




# arsenal.py 398
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