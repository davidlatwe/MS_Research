import maya.cmds as cmds
import maya.OpenMaya as om
import os


def getTextureRes(imgPath):
	"""
	"""
	utilWidth = om.MScriptUtil()
	utilWidth.createFromInt(0)
	ptrWidth = utilWidth.asUintPtr()
	utilHeight = om.MScriptUtil()
	utilHeight.createFromInt(0)
	ptrHeight = utilHeight.asUintPtr()
	
	try:
		textureFile = om.MImage()
		textureFile.readFromFile ( imgPath )
		textureFile.getSize(ptrWidth, ptrHeight)
		width = om.MScriptUtil.getUint(ptrWidth)
		height = om.MScriptUtil.getUint(ptrHeight)

		return width, height

	except:
		cmds.warning( 'Texture Res error: ' + imgPath )
		
		return 1024, 1024


def resizeTexture(imgPath, sizeScale):
	"""
	"""
	sizeScaleChart = {	
						'original': 1,
						'half'    : 0.5,
						'third'   : 0.33333,
						'quarter' : 0.25
					 }
	notSupportList = ['exr', 'hdr', 'ptx', 'tx', 'iff']
	newPath = replaceTexture(imgPath, sizeScale)
	original = replaceTexture(imgPath, 'original')
	fileExt = newPath.split('.')[-1]
	if not fileExt.lower() in notSupportList:
		if not cmds.file(newPath, q= 1, ex= 1):
			try:
				textureFile = om.MImage()
				textureFile.readFromFile ( imgPath )
				width, height = getTextureRes(original)
				textureFile.resize( int(width * sizeScaleChart[sizeScale]), int(height * sizeScaleChart[sizeScale]), 1 )
				textureFile.writeToFile( newPath, fileExt)
				print 'processed ->  ' + imgPath
			except:
				#raise
				cmds.warning( 'image file error: ' + imgPath )
				return imgPath

		return newPath

	else:
		return imgPath


def replaceTexture(imgPath, sizeScale):
	"""
	"""
	keyWord = '_@Resized@_'

	nameSplit = [os.path.dirname(imgPath), os.path.basename(imgPath)]

	if len(nameSplit) == 2:
		fileName = nameSplit[1].split(keyWord)[0] + ('.' + nameSplit[1].split('.')[-1] if keyWord in nameSplit[1] else '')
		if sizeScale == 'original':
			imgPath = nameSplit[0] + '/' + fileName
		else:
			imgPath = nameSplit[0] + '/' + fileName + keyWord + sizeScale + '.' + nameSplit[1].split('.')[-1]
	else:
		print 'Wrong image path format. ' + imgPath

	return imgPath


def getImgPath():
	"""
	"""
	fileList = cmds.ls(sl= 1, et= 'file')
	if not len(fileList):
		fileList = cmds.ls(type= 'file')
	imgPathList = {}.fromkeys(fileList, '')
	for tex in imgPathList.keys():
		imgPathList[tex] = cmds.getAttr(tex + '.fileTextureName')

	return imgPathList


def batchResizeTexture(*args):

	imgPathList = getImgPath()
	sizeScale = cmds.optionMenu('TR_sizeScale', q= 1, v= 1)

	maxValue = len(imgPathList.keys())
	cmds.progressWindow( title= 'TextureResize', progress= 0, max= maxValue, status= 'Scaling...', isInterruptable= 1 )

	processStop = 0

	for i, tex in enumerate(imgPathList.keys()):
		if cmds.progressWindow( query= 1, isCancelled= 1 ):
			processStop = 1
			break
		
		newPath = resizeTexture(imgPathList[tex], sizeScale)
		#print newPath
		if not cmds.checkBox('TR_modify', q= 1, v= 1):
			cmds.setAttr(tex + '.fileTextureName', newPath, typ= 'string')

		cmds.progressWindow( e= 1, step= 1, status= str(i) + ' / ' + str(maxValue) )

	cmds.progressWindow(endProgress=1)

	# refresh
	fileNodeSelect()


def fileNodeSelect():

	fileList = cmds.ls(sl= 1, et= 'file')
	if fileList:
		cmds.text('TR_selStatus', e= 1, l= '        ' + str(len(fileList)) + ' fileNode selected.')
		imgPath = cmds.getAttr(fileList[-1] + '.fileTextureName')
		width, height = getTextureRes(imgPath)
		resInfo = str(width) + ' x ' + str(height)
		cmds.text('TR_textureRes', e= 1, l= resInfo)
	else:
		cmds.text('TR_selStatus', e= 1, l= '        Nothing selected.   Do All.')
		cmds.text('TR_textureRes', e= 1, l= '')


windowName = 'TextureResize'

def closeUI():
	if cmds.window(windowName, q= 1, ex= 1):
		maya.utils.executeDeferred('cmds.deleteUI("' + windowName + '")')


if cmds.window(windowName, q= 1, ex= 1):
	cmds.deleteUI(windowName)

cmds.window(windowName, s= 0)

cmds.scriptJob(e= ['SelectionChanged', 'fileNodeSelect()'], p= windowName)

cmds.columnLayout(adj= 1, rs= 5)

cmds.text(l= '  Selected fileNode : ', al= 'left')
cmds.text('TR_selStatus', l= '', al= 'left', w= 120)
cmds.text('TR_textureRes', l= '', al= 'left')

cmds.checkBox('TR_modify', l= 'resize only, do not change path.')

cmds.optionMenu('TR_sizeScale', w= 120, h= 25)
cmds.menuItem('original')
cmds.menuItem('half')
cmds.menuItem('third')
cmds.menuItem('quarter')

cmds.button('TR_doResize', h= 30, c= batchResizeTexture)

cmds.setParent('..')
cmds.window(windowName, e= 1, w= 230, h= 10)
cmds.showWindow(windowName)
fileNodeSelect()