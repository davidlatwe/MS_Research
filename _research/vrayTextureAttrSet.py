import maya.utils

def setVrayTextureFilter(*args):

	def job(fileNode, method):
		mel.eval('vray addAttributesFromGroup "' + fileNode + '" vray_texture_filter 1;')
		cmds.setAttr(fileNode + '.vrayTextureSmoothType', method)

	method = cmds.optionMenu('VMF_menu', q= 1, sl= 1) - 1
	if cmds.ls(sl= 1, et= 'file'):
		for fileNode in cmds.ls(sl= 1, et= 'file'):
			job(fileNode, method)
	else:
		for fileNode in cmds.ls(type= 'file'):
			job(fileNode, method)

	closeUI()


def setVrayTextureGamma(*args):
	
	def job(fileNode, colorspace):
		mel.eval('vray addAttributesFromGroup "' + fileNode + '" vray_file_gamma 1;')
		cmds.setAttr(fileNode + '.vrayFileColorSpace', colorspace)
	
	colorspace = cmds.optionMenu('VMG_menu', q= 1, sl= 1) - 1
	if cmds.ls(sl= 1, et= 'file'):
		for fileNode in cmds.ls(sl= 1, et= 'file'):
			job(fileNode, colorspace)
	else:
		for fileNode in cmds.ls(type= 'file'):
			job(fileNode, colorspace)

	closeUI()


def fileNodeSelect():

	if cmds.ls(sl= 1, et= 'file'):
		cmds.text('selStatus', e= 1, l= '        ' + str(len(cmds.ls(sl= 1, et= 'file'))) + ' fileNode selected.')
	else:
		cmds.text('selStatus', e= 1, l= '        Nothing selected.   Do All.')


windowName = 'setVrayMapAttr'

def closeUI():
	if cmds.window(windowName, q= 1, ex= 1):
		maya.utils.executeDeferred('cmds.deleteUI("' + windowName + '")')


if cmds.window(windowName, q= 1, ex= 1):
	cmds.deleteUI(windowName)

cmds.window(windowName, s= 0)

cmds.scriptJob(e= ['SelectionChanged', 'fileNodeSelect()'], p= windowName)

cmds.columnLayout(adj= 1, rs= 5)

cmds.text(l= '  Selected fileNode : ', al= 'left')
cmds.text('selStatus', l= '', al= 'left', w= 120)

cmds.text('  Texture Filter - smooth method', al= 'left')
cmds.optionMenu('VMF_menu', w= 120, h= 25, cc= setVrayTextureFilter)
cmds.menuItem('Bilinear')
cmds.menuItem('Bicibuc')
cmds.menuItem('Biquadratic')

cmds.text('  Texture input gamma', al= 'left')
cmds.optionMenu('VMG_menu', w= 120, h= 25, cc= setVrayTextureGamma)
cmds.menuItem('Linear')
cmds.menuItem('Gamma')
cmds.menuItem('sRGB')

cmds.setParent('..')
cmds.window(windowName, e= 1, w= 230, h= 10)
cmds.showWindow(windowName)
fileNodeSelect()