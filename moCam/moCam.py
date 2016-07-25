# -*- coding:utf-8 -*-
'''
Created on 2016.06.18

@author: davidpower
'''

from pymel.core import *
import moSceneInfo; reload(moSceneInfo)
import mMaya.mGeneral as mGeneral; reload(mGeneral)
import logging
import os

logger = logging.getLogger('MayaOil.moCam.Main')

def _getSceneInfo():
	"""
	"""
	return moSceneInfo.SceneInfo()


def rWorkingNS():
	"""
	"""
	return ':moCamera'


def rCamDir():

	sInfo = _getSceneInfo()
	camDir = ''
	try:
		camDir = sInfo.dirRule['moCamera']
	except:
		logger.error('[moCamera] file rule missing.')

	return sInfo.workspaceRoot + sInfo.dirRule['moCamera'] + '/'



def exportCam(shotNum= None):

	sInfo = _getSceneInfo()
	sname = system.sceneName()
	shotNum = sInfo.shotNum if not shotNum else shotNum
	workingNS = rWorkingNS()

	if shotNum:
		# get selected camera
		sourceCamList = [dag for dag in ls(sl= 1) if dag.getShape().type() == 'camera' ]
		logger.info('Selected camera number: %d' % len(sourceCamList))
		if sourceCamList:
			# build namespace
			mGeneral.namespaceDel(workingNS)
			mGeneral.namespaceSet(workingNS)
			logger.info('Camera export start.')
			# duplicate to root
			resultCamList = parent(duplicate(sourceCamList, ic= 0), group(em= 1, w= 1, n= 'moCameraGrp'))
			
			for i, cam in enumerate(resultCamList):
				# unlock transform
				cam.tx.unlock();cam.ty.unlock();cam.tz.unlock()
				cam.rx.unlock();cam.ry.unlock();cam.rz.unlock()
				cam.sx.unlock();cam.sy.unlock();cam.sz.unlock()
				# make constrain
				constrainNode = parentConstraint(sourceCamList[i], cam, mo= 0)
				# bake animation
				bakeResults(cam, at= ['.t', '.r', '.s'], t= [sInfo.palybackStart, sInfo.palybackEnd], sm= 1, s= 0)
				# delete constrain node
				delete(constrainNode)
				# lock transform
				cam.t.lock()
				cam.r.lock()
				cam.s.lock()

			# remove namespace
			dags = namespaceInfo(workingNS, lod = 1)
			logger.info('workingNS content: \n' + '\n'.join([str(d) for d in dags]))
			namespace(f= 1, rm = workingNS, mnr = 1)

			camExportDir = rCamDir()
			logger.debug('Camera export folder: ' + camExportDir)

			if not os.path.exists(camExportDir):
				os.makedirs(camExportDir)

			# export MA
			maPath = camExportDir + 'shot_' + shotNum + '.ma'
			logger.debug('Camera export : ' + maPath)
			select(resultCamList, r= 1)
			system.exportSelected(maPath, f= 1)
			logger.info('Camera MA export done -> ' + maPath)

			# export ABC
			if not cmds.pluginInfo('AbcExport', q= 1, l= 1):
				cmds.loadPlugin('AbcExport')
			frameRange = '%d %d' % (cmds.playbackOptions(q= 1, min= 1), cmds.playbackOptions(q= 1, max= 1))
			select(resultCamList, r= 1)
			root = '|' + cmds.ls(sl= 1, l= 1)[0].split('|')[1]
			abcPath = camExportDir + 'shot_' + shotNum + '.abc'
			logger.debug('Camera export : ' + abcPath)

			AbcExportCMD = 'AbcExport -j "-frameRange ' + frameRange \
				+ ' -ro -stripNamespaces -worldSpace -dataFormat hdf -root ' + root \
				+ ' -file ' + abcPath + '";'
			logger.debug('Camera ABC export cmd : ' + AbcExportCMD)

			mel.eval(AbcExportCMD)
			logger.info('Camera ABC export done -> ' + abcPath)

			# clean up
			delete(dags)

			return maPath

		else:
			logger.warning('No camera selected.')
	else:
		logger.warning('Invaild shot number.')


def referenceCam(shotNum= None):

	sInfo = _getSceneInfo()
	sname = system.sceneName()
	shotNum = sInfo.shotNum if not shotNum else shotNum

	if shotNum:
		# get path
		camExportDir = rCamDir()
		logger.debug('Camera export folder: ' + camExportDir)
		
		maPath = camExportDir + 'shot_' + shotNum + '.ma'
		logger.debug('Camera export : ' + maPath)

		# reference
		system.createReference(maPath, defaultNamespace= 1)
		logger.info('Camera referenced from -> ' + maPath)
	else:
		logger.warning('Invaild shot number.')
