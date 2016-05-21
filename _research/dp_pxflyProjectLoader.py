from functools import partial
import maya.cmds as cmds
import maya.mel as mel
import os
import sys


class projBoss:

	def __init__(self):

		projRoot_NAS = 'Z:/1-project'
		projRoot_LAN = (r'\\%s\1-project' % os.getenv('computername').lower()).replace('\\', '/')
		projRoot_LOC = 'D:/1-project'
		global projRootList
		global projRoot
		global pathTypeId
		global workTypeId
		projRootList = [projRoot_NAS, projRoot_LAN, projRoot_LOC]
		projRoot = ''
		pathTypeId = 1
		workTypeId = 1


	def projSetAndOpenFile(self, projName, *args):

		global projRoot
		global workTypeId
		projPath = projRoot + '/' + projName + '/03-cg'
		workPath = projPath + '/' + ['1-scenes', '1-shots'][workTypeId - 1]
		if cmds.file(workPath, q= 1, ex= 1):
			hasMayaScene = 0
			setProject = 0
			for root, dirs, files in os.walk(workPath):
				for file in files:
					if file.endswith(".ma") or file.endswith(".mb"):
						hasMayaScene = 1
			if hasMayaScene:
				fileName = cmds.fileDialog2(dir= (workPath), dialogStyle=2, fm=1)
				if fileName:
					setProject = 1
					cmds.file(mf= 0)
					cmds.file(fileName[0], open= 1)
					print 'file opened.'
					cmds.deleteUI('ProjectLoader') if cmds.window('ProjectLoader', ex= 1) else None
			else:
				setProject = 1
			if setProject:
				mel.eval('setProject \"' + projPath + '\"')
				cmds.workspace(fr= ['images', projPath.replace('1-project', '2-Render')])
				cmds.workspace(fr= ['movie', projPath.replace('1-project', '2-Render')])
				mel.eval('projectWindow;')					# create project folders
				mel.eval('np_editCurrentProjectCallback;')	# create project folders
				print 'project setted.'
				cmds.deleteUI('ProjectLoader') if cmds.window('ProjectLoader', ex= 1) else None
		else:
			sorryStr = 'Dose not exist \n' + workPath
			cmds.confirmDialog( title='Sorry', message=sorryStr, button=['Confirm'], defaultButton='Confirm', icon= 'information')



	def changePathType(self, *args):

		global projRoot
		global pathTypeId
		pathTypeId = cmds.radioButtonGrp('pathTypeRidBtn', q= 1, sl= 1)
		projRoot = projRootList[pathTypeId - 1]
		self.refreshProjList()



	def changeWorkType(self, *args):

		global workTypeId
		workTypeId = cmds.radioButtonGrp('workTypeRidBtn', q= 1, sl= 1)



	def openProjFolder(self, *args):

		global projRoot
		os.startfile(os.path.normcase(projRoot))



	def refreshProjList(self, *args):

		global projRoot
		window = 'ProjectLoader'
		height = cmds.window(window, q= 1, h= 1)
		for ctlBtn in cmds.columnLayout('projListColumn', q= 1, ca= 1):
			if ctlBtn.startswith('proj') or ctlBtn == 'justForGapBtn2' or ctlBtn == 'refreshBtn':
				cmds.deleteUI(ctlBtn)
				height = height - (2 if ctlBtn == 'justForGapBtn2' else 25)

		projList = os.listdir(projRoot)
		projList.sort()
		for counter, projFolderName in enumerate(projList):
			if not projFolderName.startswith('AA') and not projFolderName.startswith('ZZ') and '-' in projFolderName:
				projLabelName = projFolderName.split('-')[2:]
				cmds.button('proj' + str(counter) + 'Btn', l= ' - '.join(projLabelName), w= 240, h= 30, c= partial(self.projSetAndOpenFile, projFolderName))
				height = height + 25

		cmds.button('justForGapBtn2', l= '', h= 2, bgc= [.25,.25,.25], en= 0)
		cmds.button('refreshBtn', l= 'R E F R E S H', w= 240, h= 25, bgc= [0.6, 0.6, 0.4], c= self.projListWindow)
		height = height + 25 + 2
		cmds.window(window, e= 1, h= height)
		cmds.button('openPrjBtn', e= 1, l= projRoot)



	def projListWindow(self, *args):

		global projRoot
		global pathTypeId
		global projRootList
		window = 'ProjectLoader'
		cmds.deleteUI(window) if cmds.window(window, ex= 1) else None
		cmds.window(window, t= window, s= 0)

		cmds.columnLayout(adj= 1)
		rdBtnLabel = ['Z :/', '//' + os.getenv('computername').lower() + '/', 'D :/']
		cmds.radioButtonGrp('pathTypeRidBtn', l= 'Path Type : ', la3= rdBtnLabel, an1 = rdBtnLabel[0], an2= rdBtnLabel[1], an3 = rdBtnLabel[2], nrb= 3,cw4= [70, 40, 65, 50], sl= pathTypeId, cc= self.changePathType)
		cmds.radioButtonGrp('workTypeRidBtn', l= 'Work Type : ', la2= ['1-scenes', '1-shots'], nrb= 2,cw3= [70, 70, 50], sl= workTypeId, cc= self.changeWorkType)
		cmds.frameLayout('projListFrame', l= 'List', li= 106, w= 244)
		cmds.columnLayout('projListColumn', adj= 1)
		cmds.button('openPrjBtn', l= projRoot, w= 240, h= 25, bgc= [0.1, 0.5, 0.7], c= self.openProjFolder)
		cmds.button('justForGapBtn1', l= '', h= 2, bgc= [.25,.25,.25], en= 0)
		for i, p in reversed(list(enumerate(projRootList))):
			if cmds.file(p, q= 1, ex= 1):
				projRoot = p
				pathTypeId = i + 1
				mel.eval('radioButtonGrp -e -en' + str(i + 1) + ' 1 -sl ' + str(pathTypeId) + ' "pathTypeRidBtn";')
			else:
				mel.eval('radioButtonGrp -e -en' + str(i + 1) + ' 0 -sl ' + str(pathTypeId) + ' "pathTypeRidBtn";')
		if projRoot:
			self.refreshProjList()
		else:
			sorryStr = 'All project root path off-line.\n' + '\n'.join(projRootList)
			cmds.confirmDialog( title='Sorry', message=sorryStr, button=['Confirm'], defaultButton='Confirm', icon= 'information')
		cmds.window(window, e= 1, w= 10, h= 10)
		cmds.showWindow(window)