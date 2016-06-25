###########################################################################################
###
### Procedure Name :	deeXVrayFast
###
### Updated :	September 20, 2011
###
### Author :	Damien BATAILLE
### Contact :	deex@deex.info
###
### History :
###		v0.9	Bug Fix  : add  Maya 2014x64
###		v0.8	Bug Fix  : fix UI crash on Maya 2012x64
###		v0.7	Bug Fix  : fix the fast control UI
###				Bug Fix  : fix the vraySettings lockNode
###				Bug Fix  : fix add material ID on all materials button
###				Modified : use hashlib module and remove deprecated md5 module
###				Features : add a full API to use the tool without interface
###						   doc here : http://deex.info/deeXVrayFast/doc/html/
###				Features : add auto update checker (each 15 days)
###				Features : add automatic preCompositing generator for Nuke
###		v0.65	Modified : shader auto connect : shader must have the same name
###						   like the slot name
###				Modified : image resolution slider removed
###				Features : add API to use the tool without interface
###						   import deeXVrayFast
###						   deeXVrayFast.deeXVrayFastUtils(quality = 10, preset = "deeX_exterior", saveSettings = True)
###						   Will set the quality to 10 with preset deeX_exterior, saveSettings before
###						   deeXVrayFast.deeXVrayFastUtils(backSettings = True)
###						   Will reset your setting
###				Features : add automatic multimatte ID generation on material ID
###				Features : object ID tool. Generate objectID automatically on mesh.
###						   The generated ID is unique, based of the md5
###						   of the name of the mesh.
###						   Name space is supported.
###				Bug Fix  : fix the UI resize
###				Bug Fix  : fix material ID on selection
###		v0.6	Features : you can "dock" the window
###				Features : UI optimization
###				Features : material ID tool. Generate materialID automatically.
###						   The generated color is unique, based of the md5
###						   of the name of the shader or shading engine.
###						   Name space is supported.
###		v0.55	Bug fix : skip locked attributes on "back to my saved settings"
###				Bug fix : found the correct VRAY_TOOLS environment
###				Bug fix : interface : correct fast control GI menu 
###				Features : textures to tiled exr, add revert option
###		v0.5	First release
###
### Description :
###
###		Deex Vray Fast is a tool which help the user to work quickly and easily with Vray For Maya.
###
###    * Set the quality automatically with one slider (image sampler quality, GI quality, etc etc...)
###    * All qualities are controled by presets
###    * 2 DeeX presets builded by default (for exterior and interior)
###    * Edit/delete/save/share your presets qualities with all users
###    * Optimization chooser : choose what do you want to control (Image sampler, irradiance map, light cache, system, etc etc...)
###    * Optimization chooser : add differente quality for each render option (Image sampler, irradiance map, light cache, system, etc etc...)
###    * Lock an attribute and the tool will keep the user value
###    * Change resolution in one click (quality is linked to resolution)
###    * Fast control : choose the best "combo" for GI, quickly control the rendering options (Motion blur, displacement, ambient occlusion, DOF, etc etc...)
###    * Tool : import multiple proxies in one click
###    * Tool : connect automatically all shaders to proxies materials (correspondence between proxy slot name and shader name. Work with name space/references)
###    * Tool : convert all (or selection) your textures into tiled exr. Color space for each texture is preserved automatically.
###    * Update your tool in one click
###
### How to use :
###
###		Put the script in your python scripts folder then start Maya.
###		Type and execute:
###			import deeXVrayFast
###   		reload(deeXVrayFast)
###      	deeXVrayFast.deeXVrayFastUI()
###      		
###		Editor, an UI window will appear.
###
### All Rights Reserved .
###########################################################################################

import maya.cmds 					as cmds
import maya.OpenMaya 				as OpenMaya
import maya.mel						as mel
import os
import subprocess
import math
import pymel.core 					as pm
import re
import sys
import shutil
import hashlib
import datetime
import time
from functools import partial

class deexVrayFastUpdater(object):
	def __init__(self, parent):
		self.parent = parent
		
	def update(self, *args):
		import httplib
		import platform
		import urllib2
		
		print '[deeXVrayFast] Checking if there is a new version';
		
		# Get the latest version info
		try:
			#url like http://deex.info/deeXVrayFast/deeXVrayFastUpdate.html
			request = urllib2.urlopen(self.parent.updatePage)
			response = request.read()
			
		except urllib2.HTTPError, e:
			print '[deeXVrayFast] Unable to get latest version info - HTTPError = ' + str(e)
			return False
			
		except urllib2.URLError, e:
			print '[deeXVrayFast] Unable to get latest version info - URLError = ' + str(e)
			return False
			
		except httplib.HTTPException, e:
			print '[deeXVrayFast] Unable to get latest version info - HTTPException'
			return False
			
		except Exception, e:
			import traceback
			print '[deeXVrayFast]Unable to get latest version info - Exception = ' + traceback.format_exc()
			return False
		
		print('[deeXVrayFast] Update: importing json/minjson')
		
		# We need to return the data using JSON. As of Python 2.6+, there is a core JSON
		# module. We have a 2.4/2.5 compatible lib included with the agent but if we're
		# on 2.6 or above, we should use the core module which will be faster
		pythonVersion = platform.python_version_tuple()
		
		# Decode the JSON
		if int(pythonVersion[1]) >= 6: # Don't bother checking major version since we only support v2 anyway
			import json

			print('[deeXVrayFast] Update: decoding JSON (json)')
			
			try:
				updateInfo = json.loads(response)
			except Exception, e:
				print '[deeXVrayFast] Unable to get latest version info. Try again later.'
				return False
			
		else:
			import minjson
			
			print('[deeXVrayFast] Update: decoding JSON (minjson)')
			
			try:
				updateInfo = minjson.safeRead(response)
			except Exception, e:
				print '[deeXVrayFast] Unable to get latest version info. Try again later.'
				return False
		
		# Do the version check	
		#if updateInfo['version'] != agentConfig['version']:
		if str(updateInfo['version']) != str(self.parent.version):
			result = cmds.confirmDialog(title='Found update', message='Your version is : '+ str(self.parent.version) +'\nThe last version is : '+ str(updateInfo['version']) +'\nDo you want to update ?\n', button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
			if result == 'Yes':#update
				import md5 # I know this is depreciated, but we still support Python 2.4 and hashlib is only in 2.5. Case 26918
				import urllib
				
				print '[deeXVrayFast] A new version is available.'
				
				def downloadFile(agentFile, recursed = False):				
					print '[deeXVrayFast] Downloading ' + agentFile['name']
					
					downloadedFile = urllib.urlretrieve(self.parent.website + agentFile['link'])
					
					# Do md5 check to make sure the file downloaded properly
					checksum = md5.new()
					f = file(downloadedFile[0], 'rb')
					
					# Although the files are small, we can't guarantee the available memory nor that there
					# won't be large files in the future, so read the file in small parts (1kb at time)
					while True:
						part = f.read(1024)
						
						if not part: 
							break # end of file
					
						checksum.update(part)
						
					f.close()
					
					# Do we have a match?
					if checksum.hexdigest() == agentFile['md5']:
						return downloadedFile[0]
						
					else:
						# Try once more
						if recursed == False:
							downloadFile(agentFile, True)
						
						else:
							print '[deeXVrayFast] ' + agentFile['name'] + ' did not match its checksum - it is corrupted. This may be caused by network issues so please try again in a moment.'
							return False
				
				# Loop through the new files and call the download function
				for agentFile in updateInfo['files']:
					agentFile['tempFile'] = downloadFile(agentFile)			
				
				# If we got to here then everything worked out fine. However, all the files are still in temporary locations so we need to move them
				# This is to stop an update breaking a working agent if the update fails halfway through
				for agentFile in updateInfo['files']:
					print '[deeXVrayFast] Updating ' + agentFile['name']
					
					try:
						
						if os.path.exists(agentFile['name']):
							os.remove(agentFile['name'])
						print agentFile['tempFile'], self.parent.dir + agentFile['name']
						shutil.move(agentFile['tempFile'], self.parent.dir + agentFile['name'])
					
					except OSError:
						print '[deeXVrayFast] An OS level error occurred. You will need to manually re-install deexVrayFast tool by downloading the latest version from http://deex.info/.'
						return False
				
				result = cmds.confirmDialog( title='Update completed', message='Update completed. Restart the tool ?', button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
				print '[deeXVrayFast] Update completed.'
				if result == 'Yes':
					import deeXVrayFast
					reload(deeXVrayFast)
					deeXVrayFast.deeXVrayFastUI()
					return True
			else:
				print '[deeXVrayFast]deexVrayFast tool not updated.'
				return False
		else:
			cmds.confirmDialog( title='No update', message='deexVrayFast tool is already up to date\nLast version is : ' + str(self.parent.version), button=['Ok'], defaultButton='Ok', cancelButton='Ok', dismissString='Ok' )
			print '[deeXVrayFast] deexVrayFast tool is already up to date\nLast version is : ' + str(self.parent.version)
			return True

class deexVrayFastPresetType(object):
	def __init__(self, parent, actualPresetType):
		self.parent = parent
		self.actualPreset = actualPresetType
		
		####Global option Start####
		self.vraySettings_globopt_mtl_maxDepthM 		= 1.0
		self.vraySettings_globopt_mtl_maxDepthH 		= 1.0	
		####Global option End####
		
		####DMC AA Start####
		self.vraySettings_dmcMaxSubdivsM 				= 1.0
		self.vraySettings_dmcMaxSubdivsH 				= 1.0
		self.vraySettings_dmcMinSubdivsM				= 1.0
		self.vraySettings_dmcMinSubdivsH				= 1.0
		self.vraySettings_dmcThresholdM					= 1.0
		self.vraySettings_dmcThresholdH					= 1.0
		####DMC AA End####
		
		####Irradiance MAP Start####
		self.vraySettings_imap_minRateM					= 1.0
		self.vraySettings_imap_minRateH					= 1.0
		self.vraySettings_imap_maxRateM					= 1.0
		self.vraySettings_imap_maxRateH					= 1.0
		self.vraySettings_imap_colorThresholdM			= 1.0
		self.vraySettings_imap_colorThresholdH			= 1.0
		self.vraySettings_imap_normalThresholdM			= 1.0
		self.vraySettings_imap_normalThresholdH			= 1.0
		self.vraySettings_imap_distanceThresholdM		= 1.0
		self.vraySettings_imap_distanceThresholdH		= 1.0
		self.vraySettings_imap_subdivsM					= 1.0
		self.vraySettings_imap_subdivsH					= 1.0
		self.vraySettings_imap_interpSamplesM			= 1.0
		self.vraySettings_imap_interpSamplesH			= 1.0
		self.vraySettings_imap_detailRadiusM			= 1.0
		self.vraySettings_imap_detailRadiusH			= 1.0
		self.vraySettings_imap_detailSubdivsMultM		= 1.0
		self.vraySettings_imap_detailSubdivsMultH		= 1.0
		####Irradiance MAP End####
		
		####Light cache Start####
		self.vraySettings_subdivsM						= 1.0
		self.vraySettings_subdivsH						= 1.0
		self.vraySettings_sampleSizeM					= 1.0
		self.vraySettings_sampleSizeH					= 1.0
		self.vraySettings_prefilterSamplesM				= 1.0
		self.vraySettings_prefilterSamplesH				= 1.0
		self.vraySettings_filterSamplesM				= 1.0
		self.vraySettings_filterSamplesH				= 1.0
		####Light cache End####
		
		####DMC Sampler start####
		self.vraySettings_dmcs_adaptiveAmountM			= 1.0
		self.vraySettings_dmcs_adaptiveAmountH			= 1.0
		self.vraySettings_dmcs_adaptiveThresholdM		= 1.0
		self.vraySettings_dmcs_adaptiveThresholdH		= 1.0
		self.vraySettings_dmcs_adaptiveMinSamplesM		= 1.0
		self.vraySettings_dmcs_adaptiveMinSamplesH		= 1.0
		self.vraySettings_dmcs_subdivsMultM				= 1.0
		self.vraySettings_dmcs_subdivsMultH				= 1.0
		####DMC Sampler end####
		
		####Multiplicator start####
		self.multiplicator_vraySettings_dmcMaxSubdivs	= 1.0
		self.multiplicator_vraySettings_imap_minRate	= 1.0
		self.multiplicator_vraySettings_imap_maxRate	= 1.0
		self.multiplicator_vraySettings_imap_detailRadius	= 1.0
		####Multiplicator end####
		
		####Info###
		self.presetComment								= None

	#============================================
	#
	# Show the preset editor
	#
	#============================================
	def show(self):
		#kill windows id exist
		if cmds.window ("deexVrayFastPresetType", exists = True):
			cmds.deleteUI ("deexVrayFastPresetType", window=True)
		cmds.loadUI(uiFile= self.parent.dir + '/deexVrayFastPresetType.ui', verbose = False)
		cmds.showWindow('deexVrayFastPresetType')
		
		#command
		cmds.optionMenu( 'presetType_edit_CB', edit = True, changeCommand = self.init )
		cmds.button( 'deexVrayFastPresetType_saveButton', edit = True, command= self.save)
		cmds.button( 'deexVrayFastPresetType_deleteButton', edit = True, command= self.delete)
		
		#insertion maya command
		cmds.floatField('vraySettings_globopt_mtl_maxDepthM', p = 'deexVrayFastPresetType_horizontalLayout_3', changeCommand = self.update)
		cmds.floatField('vraySettings_globopt_mtl_maxDepthH', p = 'deexVrayFastPresetType_horizontalLayout_4', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcMaxSubdivsM', p = 'deexVrayFastPresetType_horizontalLayout_7', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcMaxSubdivsH', p = 'deexVrayFastPresetType_horizontalLayout_8', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcMinSubdivsM', p = 'deexVrayFastPresetType_horizontalLayout_5', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcMinSubdivsH', p = 'deexVrayFastPresetType_horizontalLayout_6', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcThresholdM', p = 'deexVrayFastPresetType_horizontalLayout_9', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcThresholdH', p = 'deexVrayFastPresetType_horizontalLayout_10', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_minRateM', p = 'deexVrayFastPresetType_horizontalLayout_11', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_minRateH', p = 'deexVrayFastPresetType_horizontalLayout_28', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_maxRateM', p = 'deexVrayFastPresetType_horizontalLayout_12', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_maxRateH', p = 'deexVrayFastPresetType_horizontalLayout_29', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_colorThresholdM', p = 'deexVrayFastPresetType_horizontalLayout_13', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_colorThresholdH', p = 'deexVrayFastPresetType_horizontalLayout_30', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_normalThresholdM', p = 'deexVrayFastPresetType_horizontalLayout_14', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_normalThresholdH', p = 'deexVrayFastPresetType_horizontalLayout_31', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_distanceThresholdM', p = 'deexVrayFastPresetType_horizontalLayout_15', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_distanceThresholdH', p = 'deexVrayFastPresetType_horizontalLayout_32', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_subdivsM', p = 'deexVrayFastPresetType_horizontalLayout_16', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_subdivsH', p = 'deexVrayFastPresetType_horizontalLayout_33', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_interpSamplesM', p = 'deexVrayFastPresetType_horizontalLayout_17', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_interpSamplesH', p = 'deexVrayFastPresetType_horizontalLayout_34', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_detailRadiusM', p = 'deexVrayFastPresetType_horizontalLayout_18', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_detailRadiusH', p = 'deexVrayFastPresetType_horizontalLayout_35', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_detailSubdivsMultM', p = 'deexVrayFastPresetType_horizontalLayout_19', changeCommand = self.update)
		cmds.floatField('vraySettings_imap_detailSubdivsMultH', p = 'deexVrayFastPresetType_horizontalLayout_36', changeCommand = self.update)
		cmds.floatField('vraySettings_subdivsM', p = 'deexVrayFastPresetType_horizontalLayout_20', changeCommand = self.update)
		cmds.floatField('vraySettings_subdivsH', p = 'deexVrayFastPresetType_horizontalLayout_37', changeCommand = self.update)
		cmds.floatField('vraySettings_sampleSizeM', p = 'deexVrayFastPresetType_horizontalLayout_21', changeCommand = self.update)
		cmds.floatField('vraySettings_sampleSizeH', p = 'deexVrayFastPresetType_horizontalLayout_38', changeCommand = self.update)
		cmds.floatField('vraySettings_prefilterSamplesM', p = 'deexVrayFastPresetType_horizontalLayout_22', changeCommand = self.update)
		cmds.floatField('vraySettings_prefilterSamplesH', p = 'deexVrayFastPresetType_horizontalLayout_44', changeCommand = self.update)
		cmds.floatField('vraySettings_filterSamplesM', p = 'deexVrayFastPresetType_horizontalLayout_23', changeCommand = self.update)
		cmds.floatField('vraySettings_filterSamplesH', p = 'deexVrayFastPresetType_horizontalLayout_43', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcs_adaptiveAmountM', p = 'deexVrayFastPresetType_horizontalLayout_24', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcs_adaptiveAmountH', p = 'deexVrayFastPresetType_horizontalLayout_42', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcs_adaptiveThresholdM', p = 'deexVrayFastPresetType_horizontalLayout_25', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcs_adaptiveThresholdH', p = 'deexVrayFastPresetType_horizontalLayout_41', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcs_adaptiveMinSamplesM', p = 'deexVrayFastPresetType_horizontalLayout_26', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcs_adaptiveMinSamplesH', p = 'deexVrayFastPresetType_horizontalLayout_40', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcs_subdivsMultM', p = 'deexVrayFastPresetType_horizontalLayout_27', changeCommand = self.update)
		cmds.floatField('vraySettings_dmcs_subdivsMultH', p = 'deexVrayFastPresetType_horizontalLayout_39', changeCommand = self.update)
		#multiplicator
		cmds.floatField('multiplicator_vraySettings_dmcMaxSubdivs', p = 'deexVrayFastPresetType_horizontalLayout_45', changeCommand = self.update)
		cmds.floatField('multiplicator_vraySettings_imap_minRate', p = 'deexVrayFastPresetType_horizontalLayout_46', changeCommand = self.update)
		cmds.floatField('multiplicator_vraySettings_imap_maxRate', p = 'deexVrayFastPresetType_horizontalLayout_47', changeCommand = self.update)
		cmds.floatField('multiplicator_vraySettings_imap_detailRadius', p = 'deexVrayFastPresetType_horizontalLayout_48', changeCommand = self.update)
		#info
		cmds.scrollField('commentTextEdit_TE', p = 'verticalLayout_comment', editable=True, wordWrap=True, changeCommand = self.update )
		
		listPreset = self.parent.listFile(dir = self.parent.dir, start = 'deeXVrayFastPresetType_', end = '.txt')
		for myPreset in listPreset:
			#get the preset name without extension
			presetName = myPreset.split('deeXVrayFastPresetType_')[-1][:-4]
			cmds.menuItem( label=presetName, parent = 'presetType_edit_CB' )
		
		#set the actual preset
		cmds.optionMenu( 'presetType_edit_CB', edit = True, value = self.actualPreset )
		self.init()
	
	#============================================
	#
	# Update self values
	#
	#============================================
	def update(self, *args):
		self.vraySettings_globopt_mtl_maxDepthM = cmds.floatField('vraySettings_globopt_mtl_maxDepthM', query = True, value = True)
		self.vraySettings_globopt_mtl_maxDepthH = cmds.floatField('vraySettings_globopt_mtl_maxDepthH', query = True, value = True)
		self.vraySettings_dmcMaxSubdivsM = cmds.floatField('vraySettings_dmcMaxSubdivsM', query = True, value = True)
		self.vraySettings_dmcMaxSubdivsH = cmds.floatField('vraySettings_dmcMaxSubdivsH', query = True, value = True)
		self.vraySettings_dmcMinSubdivsM = cmds.floatField('vraySettings_dmcMinSubdivsM', query = True, value = True)
		self.vraySettings_dmcMinSubdivsH = cmds.floatField('vraySettings_dmcMinSubdivsH', query = True, value = True)
		self.vraySettings_dmcThresholdM = cmds.floatField('vraySettings_dmcThresholdM', query = True, value = True)
		self.vraySettings_dmcThresholdH = cmds.floatField('vraySettings_dmcThresholdH', query = True, value = True)
		self.vraySettings_imap_minRateM = cmds.floatField('vraySettings_imap_minRateM', query = True, value = True)
		self.vraySettings_imap_minRateH = cmds.floatField('vraySettings_imap_minRateH', query = True, value = True)
		self.vraySettings_imap_maxRateM = cmds.floatField('vraySettings_imap_maxRateM', query = True, value = True)
		self.vraySettings_imap_maxRateH = cmds.floatField('vraySettings_imap_maxRateH', query = True, value = True)
		self.vraySettings_imap_colorThresholdM = cmds.floatField('vraySettings_imap_colorThresholdM', query = True, value = True)
		self.vraySettings_imap_colorThresholdH = cmds.floatField('vraySettings_imap_colorThresholdH', query = True, value = True)
		self.vraySettings_imap_normalThresholdM = cmds.floatField('vraySettings_imap_normalThresholdM', query = True, value = True)
		self.vraySettings_imap_normalThresholdH = cmds.floatField('vraySettings_imap_normalThresholdH', query = True, value = True)
		self.vraySettings_imap_distanceThresholdM = cmds.floatField('vraySettings_imap_distanceThresholdM', query = True, value = True)
		self.vraySettings_imap_distanceThresholdH = cmds.floatField('vraySettings_imap_distanceThresholdH', query = True, value = True)
		self.vraySettings_imap_subdivsM = cmds.floatField('vraySettings_imap_subdivsM', query = True, value = True)
		self.vraySettings_imap_subdivsH = cmds.floatField('vraySettings_imap_subdivsH', query = True, value = True)
		self.vraySettings_imap_interpSamplesM = cmds.floatField('vraySettings_imap_interpSamplesM', query = True, value = True)
		self.vraySettings_imap_interpSamplesH = cmds.floatField('vraySettings_imap_interpSamplesH', query = True, value = True)
		self.vraySettings_imap_detailRadiusM = cmds.floatField('vraySettings_imap_detailRadiusM', query = True, value = True)
		self.vraySettings_imap_detailRadiusH = cmds.floatField('vraySettings_imap_detailRadiusH', query = True, value = True)
		self.vraySettings_imap_detailSubdivsMultM = cmds.floatField('vraySettings_imap_detailSubdivsMultM', query = True, value = True)
		self.vraySettings_imap_detailSubdivsMultH = cmds.floatField('vraySettings_imap_detailSubdivsMultH', query = True, value = True)
		self.vraySettings_subdivsM = cmds.floatField('vraySettings_subdivsM', query = True, value = True)
		self.vraySettings_subdivsH = cmds.floatField('vraySettings_subdivsH', query = True, value = True)
		self.vraySettings_sampleSizeM = cmds.floatField('vraySettings_sampleSizeM', query = True, value = True)
		self.vraySettings_sampleSizeH = cmds.floatField('vraySettings_sampleSizeH', query = True, value = True)
		self.vraySettings_prefilterSamplesM = cmds.floatField('vraySettings_prefilterSamplesM', query = True, value = True)
		self.vraySettings_prefilterSamplesH = cmds.floatField('vraySettings_prefilterSamplesH', query = True, value = True)
		self.vraySettings_filterSamplesM = cmds.floatField('vraySettings_filterSamplesM', query = True, value = True)
		self.vraySettings_filterSamplesH = cmds.floatField('vraySettings_filterSamplesH', query = True, value = True)
		self.vraySettings_dmcs_adaptiveAmountM = cmds.floatField('vraySettings_dmcs_adaptiveAmountM', query = True, value = True)
		self.vraySettings_dmcs_adaptiveAmountH = cmds.floatField('vraySettings_dmcs_adaptiveAmountH', query = True, value = True)
		self.vraySettings_dmcs_adaptiveThresholdM = cmds.floatField('vraySettings_dmcs_adaptiveThresholdM', query = True, value = True)
		self.vraySettings_dmcs_adaptiveThresholdH = cmds.floatField('vraySettings_dmcs_adaptiveThresholdH', query = True, value = True)
		self.vraySettings_dmcs_adaptiveMinSamplesM = cmds.floatField('vraySettings_dmcs_adaptiveMinSamplesM', query = True, value = True)
		self.vraySettings_dmcs_adaptiveMinSamplesH = cmds.floatField('vraySettings_dmcs_adaptiveMinSamplesH', query = True, value = True)
		self.vraySettings_dmcs_subdivsMultM = cmds.floatField('vraySettings_dmcs_subdivsMultM', query = True, value = True)
		self.vraySettings_dmcs_subdivsMultH = cmds.floatField('vraySettings_dmcs_subdivsMultH', query = True, value = True)
		
		####Multiplicator start####
		self.multiplicator_vraySettings_dmcMaxSubdivs	= cmds.floatField('multiplicator_vraySettings_dmcMaxSubdivs', query = True, value = True)
		self.multiplicator_vraySettings_imap_minRate	= cmds.floatField('multiplicator_vraySettings_imap_minRate', query = True, value = True)
		self.multiplicator_vraySettings_imap_maxRate	= cmds.floatField('multiplicator_vraySettings_imap_maxRate', query = True, value = True)
		self.multiplicator_vraySettings_imap_detailRadius	= cmds.floatField('multiplicator_vraySettings_imap_detailRadius', query = True, value = True)
		####Multiplicator end####
		
		####Info####
		self.presetComment					= cmds.scrollField('commentTextEdit_TE', query = True, text = True)
	
	#============================================
	#
	# Update table values
	#
	#============================================
	def init(self, *args):
		self.actualPreset = cmds.optionMenu( 'presetType_edit_CB', query = True, value = True )
		#get value from file
		dico, dicoMultiplicator, commentString = self.parent.presetTypeInitGetValue(self.actualPreset)
		for myAttr in dico:
			if myAttr == 'vraySettings.globopt_mtl_maxDepth':
				####Global option Start####
				cmds.floatField('vraySettings_globopt_mtl_maxDepthM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_globopt_mtl_maxDepthH', edit = True, value = float(dico[myAttr][1]))	
				####Global option End####
			
			if myAttr == 'vraySettings.dmcMaxSubdivs':
				####DMC AA Start####
				cmds.floatField('vraySettings_dmcMaxSubdivsM', edit = True, value = float(dico[myAttr][0]))	
				cmds.floatField('vraySettings_dmcMaxSubdivsH', edit = True, value = float(dico[myAttr][1]))
				
			if myAttr == 'vraySettings.dmcMinSubdivs':
				cmds.floatField('vraySettings_dmcMinSubdivsM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_dmcMinSubdivsH', edit = True, value = float(dico[myAttr][1]))
			
			if myAttr == 'vraySettings.dmcThreshold':	
				cmds.floatField('vraySettings_dmcThresholdM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_dmcThresholdH', edit = True, value = float(dico[myAttr][1]))
				####DMC AA End####
			
			if myAttr == 'vraySettings.imap_minRate':	
				####Irradiance MAP Start####
				cmds.floatField('vraySettings_imap_minRateM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_imap_minRateH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.imap_maxRate':	
				cmds.floatField('vraySettings_imap_maxRateM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_imap_maxRateH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.imap_colorThreshold':	
				cmds.floatField('vraySettings_imap_colorThresholdM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_imap_colorThresholdH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.imap_normalThreshold':	
				cmds.floatField('vraySettings_imap_normalThresholdM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_imap_normalThresholdH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.imap_distanceThreshold':	
				cmds.floatField('vraySettings_imap_distanceThresholdM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_imap_distanceThresholdH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.imap_subdivs':	
				cmds.floatField('vraySettings_imap_subdivsM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_imap_subdivsH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.imap_interpSamples':	
				cmds.floatField('vraySettings_imap_interpSamplesM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_imap_interpSamplesH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.imap_detailRadius':	
				cmds.floatField('vraySettings_imap_detailRadiusM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_imap_detailRadiusH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.imap_detailSubdivsMult':	
				cmds.floatField('vraySettings_imap_detailSubdivsMultM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_imap_detailSubdivsMultH', edit = True, value = float(dico[myAttr][1]))
			####Irradiance MAP End####
			
			if myAttr == 'vraySettings.subdivs':	
				####Light cache Start####
				cmds.floatField('vraySettings_subdivsM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_subdivsH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.sampleSize':	
				cmds.floatField('vraySettings_sampleSizeM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_sampleSizeH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.prefilterSamples':	
				cmds.floatField('vraySettings_prefilterSamplesM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_prefilterSamplesH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.filterSamples':	
				cmds.floatField('vraySettings_filterSamplesM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_filterSamplesH', edit = True, value = float(dico[myAttr][1]))
				####Light cache End####
			
			if myAttr == 'vraySettings.dmcs_adaptiveAmount':	
				####DMC Sampler start####
				cmds.floatField('vraySettings_dmcs_adaptiveAmountM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_dmcs_adaptiveAmountH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.dmcs_adaptiveThreshold':	
				cmds.floatField('vraySettings_dmcs_adaptiveThresholdM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_dmcs_adaptiveThresholdH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.dmcs_adaptiveMinSamples':
				cmds.floatField('vraySettings_dmcs_adaptiveMinSamplesM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_dmcs_adaptiveMinSamplesH', edit = True, value = float(dico[myAttr][1]))
			if myAttr == 'vraySettings.dmcs_subdivsMult':	
				cmds.floatField('vraySettings_dmcs_subdivsMultM', edit = True, value = float(dico[myAttr][0]))
				cmds.floatField('vraySettings_dmcs_subdivsMultH', edit = True, value = float(dico[myAttr][1]))
				####DMC Sampler end####
				
		#multiplicator	
		for myAttr in dicoMultiplicator:
			if myAttr == 'vraySettings.dmcMaxSubdivs':
				cmds.floatField('multiplicator_vraySettings_dmcMaxSubdivs', edit = True, value = float(dicoMultiplicator[myAttr][0]))
			if myAttr == 'vraySettings.imap_minRate':
				cmds.floatField('multiplicator_vraySettings_imap_minRate', edit = True, value = float(dicoMultiplicator[myAttr][0]))
			if myAttr == 'vraySettings.imap_maxRate':
				cmds.floatField('multiplicator_vraySettings_imap_maxRate', edit = True, value = float(dicoMultiplicator[myAttr][0]))
			if myAttr == 'vraySettings.imap_detailRadius':
				cmds.floatField('multiplicator_vraySettings_imap_detailRadius', edit = True, value = float(dicoMultiplicator[myAttr][0]))
		
		####info####
		if commentString is not None or commentString != "":
			cmds.scrollField('commentTextEdit_TE', edit = True, text = commentString)
		else:
			cmds.scrollField('commentTextEdit_TE', edit = True, text = "No comment")
		
		self.update()
	
	#============================================
	#
	# delete the file
	#
	#============================================
	def delete(self, *args):
		fileName = self.parent.dir + 'deeXVrayFastPresetType_' + self.actualPreset + '.txt'
		result = cmds.confirmDialog(title='Are you sure ?', message='Do you want to delete the preset file ?\n', button=['Ok', 'Cancel'], defaultButton='Cancel', cancelButton='Cancel', dismissString='Cancel')
		if result == 'Ok':#delete the file
			os.remove(fileName)
			valueIntIntem = cmds.optionMenu('presetType_edit_CB', select = True, query = True )
			itemList = cmds.optionMenu('presetType_edit_CB', query = True, itemListLong = True )
			cmds.deleteUI(itemList[valueIntIntem-1], menuItem = True )
			
			if cmds.optionMenu(self.UI.presetType_CB , query = True, exists = True):
				valueIntIntem = cmds.optionMenu(self.UI.presetType_CB, select = True, query = True )
				itemList = cmds.optionMenu(self.UI.presetType_CB, query = True, itemListLong = True )
				cmds.deleteUI(itemList[valueIntIntem-1], menuItem = True )
			self.init()
	
	#============================================
	#
	# Save the file
	#
	#============================================
	def save(self, *args):
		self.update()
		####################################get value from file
		fileName = self.parent.dir + 'deeXVrayFastPresetType_' + self.actualPreset + '.txt'
		
		textString = "#### value is like 4|12. First value (10) is medium value. 30 is the very high value.\n"
		textString += "\n"
		textString += "####Global option Start####\n"
		textString += "vraySettings.globopt_mtl_maxDepth 			= " + str(self.vraySettings_globopt_mtl_maxDepthM) + "|" + str(self.vraySettings_globopt_mtl_maxDepthH) + "\n"
		textString += "####Global option End####\n"
		textString += "\n"
		textString += "####DMC AA Start####\n"
		textString += "vraySettings.dmcMaxSubdivs 					= " + str(self.vraySettings_dmcMaxSubdivsM) + "|" + str(self.vraySettings_dmcMaxSubdivsH) + "\n"
		textString += "vraySettings.dmcMinSubdivs 					= " + str(self.vraySettings_dmcMinSubdivsM) + "|" + str(self.vraySettings_dmcMinSubdivsH) + "\n"
		textString += "vraySettings.dmcThreshold					= " + str(self.vraySettings_dmcThresholdM) + "|" + str(self.vraySettings_dmcThresholdH) + "\n"
		textString += "####DMC AA End####\n"
		textString += "\n"
		textString += "####Irradiance MAP Start####\n"
		textString += "vraySettings.imap_minRate					= " + str(self.vraySettings_imap_minRateM) + "|" + str(self.vraySettings_imap_minRateH) + "\n"
		textString += "vraySettings.imap_maxRate					= " + str(self.vraySettings_imap_maxRateM) + "|" + str(self.vraySettings_imap_maxRateH) + "\n"
		textString += "vraySettings.imap_colorThreshold				= " + str(self.vraySettings_imap_colorThresholdM) + "|" + str(self.vraySettings_imap_colorThresholdH) + "\n"
		textString += "vraySettings.imap_normalThreshold			= " + str(self.vraySettings_imap_normalThresholdM) + "|" + str(self.vraySettings_imap_normalThresholdH) + "\n"
		textString += "vraySettings.imap_distanceThreshold			= " + str(self.vraySettings_imap_distanceThresholdM) + "|" + str(self.vraySettings_imap_distanceThresholdH) + "\n"
		textString += "vraySettings.imap_subdivs					= " + str(self.vraySettings_imap_subdivsM) + "|" + str(self.vraySettings_imap_subdivsH) + "\n"
		textString += "vraySettings.imap_interpSamples				= " + str(self.vraySettings_imap_interpSamplesM) + "|" + str(self.vraySettings_imap_interpSamplesH) + "\n"
		textString += "vraySettings.imap_detailRadius				= " + str(self.vraySettings_imap_detailRadiusM) + "|" + str(self.vraySettings_imap_detailRadiusH) + "\n"
		textString += "vraySettings.imap_detailSubdivsMult			= " + str(self.vraySettings_imap_detailSubdivsMultM) + "|" + str(self.vraySettings_imap_detailSubdivsMultH) + "\n"
		textString += "####Irradiance MAP End####\n"
		textString += "\n"
		textString += "####Light cache Start####\n"
		textString += "vraySettings.subdivs							= " + str(self.vraySettings_subdivsM) + "|" + str(self.vraySettings_subdivsH) + "\n"
		textString += "vraySettings.sampleSize						= " + str(self.vraySettings_sampleSizeM) + "|" + str(self.vraySettings_sampleSizeH) + "\n"
		textString += "vraySettings.prefilterSamples				= " + str(self.vraySettings_prefilterSamplesM) + "|" + str(self.vraySettings_prefilterSamplesH) + "\n"
		textString += "vraySettings.filterSamples					= " + str(self.vraySettings_filterSamplesM) + "|" + str(self.vraySettings_filterSamplesH) + "\n"
		textString += "####Light cache End####\n"
		textString += "\n"
		textString += "####DMC Sampler start####\n"
		textString += "vraySettings.dmcs_adaptiveAmount				= " + str(self.vraySettings_dmcs_adaptiveAmountM) + "|" + str(self.vraySettings_dmcs_adaptiveAmountH) + "\n"
		textString += "vraySettings.dmcs_adaptiveThreshold			= " + str(self.vraySettings_dmcs_adaptiveThresholdM) + "|" + str(self.vraySettings_dmcs_adaptiveThresholdH) + "\n"
		textString += "vraySettings.dmcs_adaptiveMinSamples			= " + str(self.vraySettings_dmcs_adaptiveMinSamplesM) + "|" + str(self.vraySettings_dmcs_adaptiveMinSamplesH) + "\n"
		textString += "vraySettings.dmcs_subdivsMult				= " + str(self.vraySettings_dmcs_subdivsMultM) + "|" + str(self.vraySettings_dmcs_subdivsMultH) + "\n"
		textString += "####DMC Sampler end####\n"
		textString += "\n"
		textString += "####Multiplicator start####\n"
		textString += "multiplicator|vraySettings.dmcMaxSubdivs	= " + str(self.multiplicator_vraySettings_dmcMaxSubdivs) + "\n"
		textString += "multiplicator|vraySettings.imap_minRate		= " + str(self.multiplicator_vraySettings_imap_minRate) + "\n"
		textString += "multiplicator|vraySettings.imap_maxRate		= " + str(self.multiplicator_vraySettings_imap_maxRate) + "\n"
		textString += "multiplicator|vraySettings.imap_detailRadius	= " + str(self.multiplicator_vraySettings_imap_detailRadius) + "\n"
		textString += "####Multiplicator end####"
		textString += "\n"
		textString += "####Info####\n"
		textString += "presetComment								=" + str(self.presetComment).replace("\\", "\\\\").replace("\n", "\\n")
		
		result = cmds.confirmDialog(title='File always exist', message='This preset file always exist. Overwrite the file or create a new file ?\n', button=['Overwrite', 'New file', 'Cancel'], defaultButton='New file', cancelButton='Cancel', dismissString='Cancel')
		if result == 'New file':#create new file
			NameOk = False
			messageString = 'Enter Name like "deeX_exterior" :'
			while NameOk == False:
				result = cmds.promptDialog(title='New file name', message=messageString, button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
				if result == 'OK':
					#check if preset is nit always used
					actualList = cmds.optionMenu('presetType_edit_CB', query = True, itemListLong = True)
					actualListString = list()
					if actualList is not None:
						for item in actualList:
							itemString = cmds.menuItem( item, label=True, query = True )
							actualListString.append(itemString)
							
					currentName = cmds.promptDialog(query=True, text=True)
					
					if currentName not in actualListString:
						self.actualPreset = currentName
						cmds.menuItem( label=self.actualPreset, parent = 'presetType_edit_CB' )
						cmds.optionMenu('presetType_edit_CB' , edit = True, value = self.actualPreset)
						if cmds.optionMenu(self.UI.presetType_CB , query = True, exists = True):
							cmds.menuItem( label=self.actualPreset, parent = self.UI.presetType_CB )
						fileName = self.parent.dir + 'deeXVrayFastPresetType_' + self.actualPreset + '.txt'
						NameOk = True
					else:
						messageString = 'This preset name always exist, enter a new name :'
						NameOk = False
				elif result == 'Cancel':
					print "[deeXVrayFast] Canceled"
					NameOk = True
		
		file = open(fileName, "w")
		file.write(textString)
		file.close()
			
class deeXVrayFastUi(object):
	def __init__(self, parent):
		self.parent = parent
		self.width = 620
		self.height = 710
		self.ui = cmds.loadUI(uiFile=self.parent.dir + '/deeXVrayFast.ui', verbose = False)

		################################################################################################
		#insertion maya command
		self.pixelW_SB = cmds.intField('pixelW_SB', p = 'verticalLayout_6', changeCommand = self.parent.changeResolutionpixelW_SB)
		self.pixelH_SB = cmds.intField('pixelH_SB', p = 'verticalLayout_7', changeCommand = self.parent.changeResolutionpixelH_SB)
		self.presetComment_LB = cmds.scrollField('presetComment_LB', p = 'horizontalLayout_16', editable=False, wordWrap=True, h = 50 )
		self.preCompComment_LB = cmds.scrollField('preCompComment_LB', p = 'verticalLayout_11', editable=False, wordWrap=True, h = 50 )
		
		#command
		self.dock_PB = cmds.button( 'dock_PB', edit = True, command= self.parent.deexVrayFastDockWindow)
		self.optimization_chooser_MB = cmds.menuItem( 'optimization_chooser_MB', edit = True, command = self.parent.optimizationChooser )
		self.presetTypeCreateEditDelete_MB = cmds.menuItem( 'presetTypeCreateEditDelete_MB', edit = True, command = self.parent.deexVrayFastPresetType )
		self.multiImporter_MB = cmds.menuItem( 'multiImporter_MB', edit = True, command = self.parent.deexVrayFastProxyMultiImporter )
		self.shaderAutoConnect_MB = cmds.menuItem( 'shaderAutoConnect_MB', edit = True, command = self.parent.deexVrayFastProxyShaderAutoConnect )
		self.textureToTiledExrOnSelection_MB = cmds.menuItem( 'textureToTiledExrOnSelection_MB', edit = True, command = self.parent.deexVrayFastTextureToTiledExrSelection )
		self.textureToTiledExrOnAll_MB = cmds.menuItem( 'textureToTiledExrOnAll_MB', edit = True, command = self.parent.deexVrayFastTextureToTiledExrAll )
		self.textureToTiledExrbackToTexturesOnSelection_MB = cmds.menuItem( 'textureToTiledExrbackToTexturesOnSelection_MB', edit = True, command = self.parent.deexVrayFastTextureToTiledExrBackSelection )
		self.textureToTiledExrbackToTexturesOnAll_MB = cmds.menuItem( 'textureToTiledExrbackToTexturesOnAll_MB', edit = True, command = self.parent.deexVrayFastTextureToTiledExrBackAll )
		self.addMaterialIDOnSelection_MB = cmds.menuItem( 'addMaterialIDOnSelection_MB', edit = True, command = self.parent.deexVrayFastMaterialIDaddSelection )
		self.addMaterialIDOnAllMat_MB = cmds.menuItem( 'addMaterialIDOnAllMat_MB', edit = True, command = self.parent.deexVrayFastMaterialIDaddAllMat )
		self.addMaterialIDOnAllSG_MB = cmds.menuItem( 'addMaterialIDOnAllSG_MB', edit = True, command = self.parent.deexVrayFastMaterialIDaddAllSG )
		self.setMaterialIDOnSelection_MB = cmds.menuItem( 'setMaterialIDOnSelection_MB', edit = True, command = self.parent.deexVrayFastMaterialIDsetSelection )
		self.setMaterialIDOnAllMat_MB = cmds.menuItem( 'setMaterialIDOnAllMat_MB', edit = True, command = self.parent.deexVrayFastMaterialIDsetAllMat )
		self.setMaterialIDOnAllSG_MB = cmds.menuItem( 'setMaterialIDOnAllSG_MB', edit = True, command = self.parent.deexVrayFastMaterialIDsetAllSG )
		self.removeMaterialIDOnSelection_MB = cmds.menuItem( 'removeMaterialIDOnSelection_MB', edit = True, command = self.parent.deexVrayFastMaterialIDdeleteSelection )
		self.removeMaterialIDOnAllMat_MB = cmds.menuItem( 'removeMaterialIDOnAllMat_MB', edit = True, command = self.parent.deexVrayFastMaterialIDdeleteAllMat )
		self.removeMaterialIDOnAllSG_MB = cmds.menuItem( 'removeMaterialIDOnAllSG_MB', edit = True, command = self.parent.deexVrayFastMaterialIDdeleteAllSG )
		self.addObjectIDOnSelection_MB = cmds.menuItem( 'addObjectIDOnSelection_MB', edit = True, command = self.parent.deexVrayFastObjectIDaddSelection )
		self.addObjectIDOnAllMeshs_MB = cmds.menuItem( 'addObjectIDOnAllMeshs_MB', edit = True, command = self.parent.deexVrayFastObjectIDaddAllMeshs )
		self.setObjectIDOnSelection_MB = cmds.menuItem( 'setObjectIDOnSelection_MB', edit = True, command = self.parent.deexVrayFastObjectIDsetSelection )
		self.setObjectIDOnAllMeshs_MB = cmds.menuItem( 'setObjectIDOnAllMeshs_MB', edit = True, command = self.parent.deexVrayFastObjectIDsetAllMeshs )
		self.removeObjectIDOnSelection_MB = cmds.menuItem( 'removeObjectIDOnSelection_MB', edit = True, command = self.parent.deexVrayFastObjectIDremoveSelection )
		self.removeObjectIDOnAllMeshs_MB = cmds.menuItem( 'removeObjectIDOnAllMeshs_MB', edit = True, command = self.parent.deexVrayFastObjectIDremoveAllMeshs )
		self.goWebsite_MB = cmds.menuItem( 'goWebsite_MB', edit = True, command = lambda *args: cmds.showHelp( 'http://deex.info/', absolute=True ) )
		self.update_MB = cmds.menuItem( 'update_MB', edit = True, command = self.parent.deexVrayFastUpdate )
		self.about_MB = cmds.menuItem( 'about_MB', edit = True, command = self.parent.deexVrayFastAbout )
		self.saveSetting_BT = cmds.button( 'saveSetting_BT', edit = True, command= self.parent.saveSetting)
		self.optimize_BT = cmds.button( 'optimize_BT', edit = True, command= self.parent.optimize)
		self.backSetting_BT = cmds.button( 'backSetting_BT', edit = True, command= self.parent.backSetting)
		#cmds.intSlider('width_SD', edit = True, changeCommand = self.parent.changeResolutionwidth_SD)
		#cmds.intSlider('height_SD', edit = True, changeCommand = self.parent.changeResolutionheight_SD)
		self.quality_SD = cmds.intSlider('quality_SD', edit = True, changeCommand = self.parent.refresh)
		self.preset01_PB = cmds.button( 'preset01_PB', edit = True, command= self.parent.changeResolutionPreset01)
		self.preset02_PB = cmds.button( 'preset02_PB', edit = True, command= self.parent.changeResolutionPreset02)
		self.preset03_PB = cmds.button( 'preset03_PB', edit = True, command= self.parent.changeResolutionPreset03)
		self.preset04_PB = cmds.button( 'preset04_PB', edit = True, command= self.parent.changeResolutionPreset04)
		self.preset05_PB = cmds.button( 'preset05_PB', edit = True, command= self.parent.changeResolutionPreset05)
		self.preset06_PB = cmds.button( 'preset06_PB', edit = True, command= self.parent.changeResolutionPreset06)
		self.preset07_PB = cmds.button( 'preset07_PB', edit = True, command= self.parent.changeResolutionPreset07)
		self.preset08_PB = cmds.button( 'preset08_PB', edit = True, command= self.parent.changeResolutionPreset08)
		self.preset09_PB = cmds.button( 'preset09_PB', edit = True, command= self.parent.changeResolutionPreset09)
		self.preset10_PB = cmds.button( 'preset10_PB', edit = True, command= self.parent.changeResolutionPreset10)
		self.resolutionC1_PB = cmds.button( 'resolutionC1_PB', edit = True, command= self.parent.changeResolutionC1)
		self.resolutionC2_PB = cmds.button( 'resolutionC2_PB', edit = True, command= self.parent.changeResolutionC2)
		self.resolutionC3_PB = cmds.button( 'resolutionC3_PB', edit = True, command= self.parent.changeResolutionC3)
		self.resolutionC4_PB = cmds.button( 'resolutionC4_PB', edit = True, command= self.parent.changeResolutionC4)
		#fast control command
		self.GIType_CB = cmds.optionMenu( 'GIType_CB', edit = True, changeCommand= self.parent.fastControlGIType )
		
		'''
		cmds.checkBox( 'displacement_CB', edit = True, changeCommand= self.parent.fastControldisplacement )
		cmds.checkBox( 'reflectionrefraction_CB', edit = True, changeCommand= self.parent.fastControlreflectionrefraction )
		cmds.checkBox( 'maps_CB', edit = True, changeCommand= self.parent.fastControlmaps)
		cmds.checkBox( 'glossyEffects_CB', edit = True, changeCommand= self.parent.fastControlglossyEffects )
		cmds.checkBox( 'shadows_CB', edit = True, changeCommand= self.parent.fastControlshadows )
		cmds.checkBox( 'antialiasingFilter_CB', edit = True, changeCommand= self.parent.fastControlantialiasingFilter )
		cmds.checkBox( 'overrideEnvironment_CB', edit = True, changeCommand= self.parent.fastControloverrideEnvironment )
		cmds.checkBox( 'dof_CB', edit = True, changeCommand= self.parent.fastControldof )
		cmds.checkBox( 'motionBlur_CB', edit = True, changeCommand= self.parent.fastControlmotionBlur )
		cmds.checkBox( 'distributedRendering_CB', edit = True, changeCommand= self.parent.fastControldistributedRendering )
		'''
		
		self.colorMapping_SD = cmds.intSlider('colorMapping_SD', edit = True, changeCommand = self.parent.fastControlColorMapping)
		
		self.presetType_CB = cmds.optionMenu('presetType_CB', edit = True, changeCommand= self.parent.changePresetType)
		self.optimizeMat_BT = cmds.button( 'optimizeMat_BT', edit = True, command= self.parent.optimizeMat)
		self.optimizeLights_BT = cmds.button( 'optimizeLights_BT', edit = True, command= self.parent.optimizeLights)
		self.resolutionVisible_CB = cmds.checkBox( 'resolutionVisible_CB', edit = True, changeCommand= self.parent.sizeWindowsResolution )
		self.fastControlVisible_CB = cmds.checkBox( 'fastControlVisible_CB', edit = True, changeCommand= self.parent.sizeWindowsFastControl )
		self.preCompVisible_CB = cmds.checkBox( 'preCompVisible_CB', edit = True, changeCommand= self.parent.sizeWindowsPreComp )
		self.qualityVisible_CB = cmds.checkBox( 'qualityVisible_CB', edit = True, changeCommand= self.parent.sizeWindowsQuality )
		
		self.preCompNuke_CB = cmds.optionMenu('preCompNuke_CB', edit = True, changeCommand= self.parent.changePresetPreComp)
		self.generateRenderElements_BT = cmds.button( 'generateRenderElements_BT', edit = True, command= self.parent.generateRenderElementsInMaya)
		self.generateNukeScene_BT = cmds.button( 'generateNukeScene_BT', edit = True, command= self.parent.generateNuke)
		
		self.goWebsite_BT = cmds.button( 'goWebsite_BT', edit = True, command = lambda *args: cmds.showHelp( 'http://deex.info/', absolute=True ) )

		#default value
		cmds.checkBox( self.fastControlVisible_CB, edit = True, value=False )
		self.fastControl_GB = cmds.control( 'fastControl_GB', edit=True, visible=False)
		cmds.checkBox( self.preCompVisible_CB, edit = True, value=False )
		self.preCompNuke_GB = cmds.control( 'preComp_GB', edit=True, visible=False)

class deeXVrayFastTool(object):
	def __init__(self, bashMode = False):
		self.dir = str(os.path.abspath(os.path.dirname(__file__))) + '/'
		self.version = 0.9
		self.UI = None
		self.bashMode = bashMode
		self.mayaVersion = cmds.about(v=True).split()[0]
		self.osSystemType = cmds.about(operatingSystem=True)
		self.updatePage = "http://deex.info/deeXVrayFast/deeXVrayFastUpdate.html"
		self.website = "http://deex.info/"
		self.valueQuality = 50
		self.alwaysFastInserted = False
		self.actualPresetType = ''
		self.actualPresetPrecomp = ''
		self.environVRAY_TOOLS = None
		for myEnv in os.environ:
			if "VRAY_TOOLS_MAYA" in myEnv:
				self.environVRAY_TOOLS = os.environ[myEnv]
		self.materialIDexcludeType = ["particleCloud", "shaderGlow", "hairTubeShader", "layeredShader", "oceanShader", "useBackground"]
		####Global option Start####
		self.vraySettings_globopt_mtl_maxDepthM 		= 1.0
		self.vraySettings_globopt_mtl_maxDepthH 		= 1.0	
		####Global option End####
		
		####DMC AA Start####
		self.vraySettings_dmcMaxSubdivsM 				= 1.0
		self.vraySettings_dmcMaxSubdivsH 				= 1.0
		self.vraySettings_dmcMinSubdivsM				= 1.0
		self.vraySettings_dmcMinSubdivsH				= 1.0
		self.vraySettings_dmcThresholdM					= 1.0
		self.vraySettings_dmcThresholdH					= 1.0
		####DMC AA End####
		
		####Irradiance MAP Start####
		self.vraySettings_imap_minRateM					= 1.0
		self.vraySettings_imap_minRateH					= 1.0
		self.vraySettings_imap_maxRateM					= 1.0
		self.vraySettings_imap_maxRateH					= 1.0
		self.vraySettings_imap_colorThresholdM			= 1.0
		self.vraySettings_imap_colorThresholdH			= 1.0
		self.vraySettings_imap_normalThresholdM			= 1.0
		self.vraySettings_imap_normalThresholdH			= 1.0
		self.vraySettings_imap_distanceThresholdM		= 1.0
		self.vraySettings_imap_distanceThresholdH		= 1.0
		self.vraySettings_imap_subdivsM					= 1.0
		self.vraySettings_imap_subdivsH					= 1.0
		self.vraySettings_imap_interpSamplesM			= 1.0
		self.vraySettings_imap_interpSamplesH			= 1.0
		self.vraySettings_imap_detailRadiusM			= 1.0
		self.vraySettings_imap_detailRadiusH			= 1.0
		self.vraySettings_imap_detailSubdivsMultM		= 1.0
		self.vraySettings_imap_detailSubdivsMultH		= 1.0
		####Irradiance MAP End####
		
		####Light cache Start####
		self.vraySettings_subdivsM						= 1.0
		self.vraySettings_subdivsH						= 1.0
		self.vraySettings_sampleSizeM					= 1.0
		self.vraySettings_sampleSizeH					= 1.0
		self.vraySettings_prefilterSamplesM				= 1.0
		self.vraySettings_prefilterSamplesH				= 1.0
		self.vraySettings_filterSamplesM				= 1.0
		self.vraySettings_filterSamplesH				= 1.0
		####Light cache End####
		
		####DMC Sampler start####
		self.vraySettings_dmcs_adaptiveAmountM			= 1.0
		self.vraySettings_dmcs_adaptiveAmountH			= 1.0
		self.vraySettings_dmcs_adaptiveThresholdM		= 1.0
		self.vraySettings_dmcs_adaptiveThresholdH		= 1.0
		self.vraySettings_dmcs_adaptiveMinSamplesM		= 1.0
		self.vraySettings_dmcs_adaptiveMinSamplesH		= 1.0
		self.vraySettings_dmcs_subdivsMultM				= 1.0
		self.vraySettings_dmcs_subdivsMultH				= 1.0
		####DMC Sampler end####
		
		####Multiplicator start####
		self.multiplicator_vraySettings_dmcMaxSubdivs	= 1.0
		self.multiplicator_vraySettings_imap_minRate	= 1.0
		self.multiplicator_vraySettings_imap_maxRate	= 1.0
		self.multiplicator_vraySettings_imap_detailRadius	= 1.0
		####Multiplicator end####
		
		####Info###
		self.presetComment								= None
		
		###PreComp###
		self.preCompString								= None
		self.preCompComment								= None
		self.preCompRenderElements						= None

	#============================================
	#
	# Dock the windows
	#
	#============================================
	def deexVrayFastDockWindow(self, *args):
		buttonLabel = cmds.button( self.UI.dock_PB, query = True, label = True)
		if buttonLabel == "Dock the window":
			cmds.dockControl("deeXVrayFastDock", allowedArea = "all", area = "left", content = self.UI.ui)

			cmds.button( self.UI.dock_PB, edit = True, label = 'Undock the window')
		else:
			if cmds.dockControl('deeXVrayFastDock', q = True, ex = True):
				cmds.deleteUI ('deeXVrayFastDock', control = True)
			deeXVrayFastUI()
	
	#============================================
	#
	# Initialize Vray
	#
	#============================================
	def initialize(self):
		if cmds.objExists('vraySettings'):#vray settings exist
			if cmds.getAttr ('defaultRenderGlobals.currentRenderer') == "vray":#vray is the engine
				self.initializeSet()
				return True
			else:#vray is not the engine
				#bashmode
				if not self.bashMode:
					result = cmds.confirmDialog(title='Set Vray', message='Vray is not your current render engine, set Vray to the current engine ?\n', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
				else:
					result = 'OK'
				if result == 'OK':#load vray
					self.loadVray()
					self.initializeSet()
					return True
				else:#return false
					return False
		else:#vray setting not exist
			if cmds.getAttr ('defaultRenderGlobals.currentRenderer') == "vray":#but we have the vray engine
				if not self.bashMode:
					result = cmds.confirmDialog(title='Vray setting', message='Vray settings not found, reload Vray properly ?\n', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
				else:
					result = 'OK'
				if result == 'OK':#load vray
					self.loadVray()
					self.initializeSet()
					return True
				else:#return false
					return False
			else:#we have another engine
				if not self.bashMode:
					result = cmds.confirmDialog(title='Load Vray', message='Vray is not your current render engine, load Vray ?\n(take some seconds)', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
				else:
					result = 'OK'
				if result == 'OK':#load vray
					self.loadVray()
					self.initializeSet()
					return True
				else:#return false
					return False
	
	#============================================
	#
	# Initialize Vray, set and get default option
	#
	#============================================
	def initializeSet(self, *args):
		#resolution
		actualWidth = cmds.getAttr ("vraySettings.width")
		actualHeight= cmds.getAttr ("vraySettings.height")
		#cmds.intSlider('width_SD', edit = True, value = actualWidth)
		#cmds.intSlider('height_SD', edit = True, value = actualHeight)
		if not self.bashMode:
			cmds.intField(self.UI.pixelW_SB, edit = True, value = actualWidth)
			cmds.intField(self.UI.pixelH_SB, edit = True, value = actualHeight)
		#Sample type
		cmds.setAttr('vraySettings.samplerType', 1)
		if cmds.attributeQuery( 'deeXVrayFastOptimized', n='vraySettings', ex=True ):
			if not self.bashMode:
				cmds.control('menuSettings', enable=True, edit = True)
				cmds.control('menuPreset_Type', enable=True, edit = True)
				cmds.button( self.UI.saveSetting_BT, enable=False, edit = True)
				cmds.button( self.UI.optimize_BT, enable=True, edit = True)
				if cmds.attributeQuery( 'deeXVrayFastActualSettings', n='vraySettings', ex=True ):
					cmds.button( self.UI.backSetting_BT, enable=True, edit = True)
				cmds.control( 'resolution_GB', enable=True, edit=True )
				cmds.control( self.UI.fastControl_GB, enable=True, edit=True )
				cmds.control( 'quality_GB', enable=True, edit=True )
				cmds.button( self.UI.optimizeMat_BT, enable=True,edit = True)
				cmds.button( self.UI.optimizeLights_BT, enable=True, edit = True)
				cmds.control( 'preComp_GB', enable=True, edit=True )
			#vraySetting last quality
			if not cmds.attributeQuery( 'deeXVrayFastLastQuality', n='vraySettings', ex=True ):
				locked = False
				if cmds.lockNode( 'vraySettings', query=True, lock=True )[0]:
					locked = True
					cmds.lockNode( 'vraySettings', lock=False )
				cmds.addAttr('vraySettings', ln = "deeXVrayFastLastQuality", at = 'long')
				if locked:
					cmds.lockNode( 'vraySettings', lock=True )
				
				cmds.setAttr('vraySettings.deeXVrayFastLastQuality', 50)
				if not self.bashMode:
					cmds.text('quality_LB', edit = True, label = 'Quality : ' + str(50))
			else:
				actualValue = cmds.getAttr('vraySettings.deeXVrayFastLastQuality')
				if not self.bashMode:
					cmds.text('quality_LB', edit = True, label = 'Quality : ' + str(actualValue))
					cmds.intSlider(self.UI.quality_SD, edit = True, value = actualValue)
			
			#vray fast control
			if not self.bashMode:
				self.fastControlInit()
			
			#vraySetting last preset type
			self.presetTypeInit()
			self.preCompInit()
			if not self.bashMode:
				self.refresh()
	
	def fastControlInit(self, *args):
		#insertion fast control
		if self.alwaysFastInserted == False:
			self.alwaysFastInserted = True
			#GI
			if cmds.attributeQuery( 'giOn', n='vraySettings', ex=True ):
				#insertion fast control
				cmds.columnLayout( p = 'horizontalLayout_14', columnWidth = 40, columnAttach = ['right', 1], w = 40)
				#cmds.attrControlGrp( label = 'GI', attribute='vraySettings.giOn' , changeCommand = fastControlGI())
				cmds.attrControlGrp( label = 'GI', attribute='vraySettings.giOn' )
				giScriptJob = cmds.scriptJob( attributeChange=['vraySettings.giOn', self.fastControlGI] )
				#Ambient occlusion
				if cmds.attributeQuery( 'aoOn', n='vraySettings', ex=True ):
					if not self.bashMode:
						cmds.columnLayout( p = 'horizontalLayout_13', columnWidth = 115, columnAttach = ['right', 1], w = 115)
					self.fastControlAOCheckBox = cmds.attrControlGrp( label = 'Ambient Occlusion', attribute='vraySettings.aoOn' )
				actualValue = cmds.getAttr('vraySettings.giOn')
				if actualValue:
					#cmds.checkBox( 'GI_CB', edit = True, value= True )
					cmds.optionMenu( self.UI.GIType_CB, edit = True, enable = True )
					#cmds.checkBox( 'AO_CB', edit = True, enable= True )
					cmds.attrControlGrp( self.fastControlAOCheckBox, edit = True, enable = True )
					self.fastControlGI_optionMenu()	
				else:
					#cmds.checkBox( 'GI_CB', edit = True, value= False )
					cmds.optionMenu( self.UI.GIType_CB, edit = True, enable = False )
					cmds.attrControlGrp( self.fastControlAOCheckBox, edit = True, enable = False )

			#Displacement
			if cmds.attributeQuery( 'globopt_geom_displacement', n='vraySettings', ex=True ):
				cmds.columnLayout( p = 'horizontalLayout_26', columnAttach=('right', 1), columnWidth = 90 )
				cmds.attrControlGrp( label = 'Displacement', attribute='vraySettings.globopt_geom_displacement' )
			#Reflection Refraction
			if cmds.attributeQuery( 'globopt_mtl_reflectionRefraction', n='vraySettings', ex=True ):
				cmds.columnLayout( p = 'horizontalLayout_2', columnAttach=('right', 1), columnWidth = 140 )
				cmds.attrControlGrp( label = 'Reflection / Refraction', attribute='vraySettings.globopt_mtl_reflectionRefraction' )
			#Maps
			if cmds.attributeQuery( 'globopt_mtl_doMaps', n='vraySettings', ex=True ):
				cmds.columnLayout( p = 'horizontalLayout_17', columnAttach=('right', 1), columnWidth = 60 )
				cmds.attrControlGrp( label = 'Maps', attribute='vraySettings.globopt_mtl_doMaps' )
			#Glossy Maps
			if cmds.attributeQuery( 'globopt_mtl_glossy', n='vraySettings', ex=True ):
				cmds.columnLayout( p = 'horizontalLayout_19', columnAttach=('right', 1), columnWidth = 110 )
				cmds.attrControlGrp( label = 'Glossy effects', attribute='vraySettings.globopt_mtl_glossy' )
			#Shadows
			if cmds.attributeQuery( 'globopt_light_doShadows', n='vraySettings', ex=True ):
				cmds.columnLayout( p = 'horizontalLayout_20', columnAttach=('right', 1), columnWidth = 72 )
				cmds.attrControlGrp( label = 'Shadows', attribute='vraySettings.globopt_light_doShadows' )
			#Antialiasing filter
			if cmds.attributeQuery( 'aaFilterOn', n='vraySettings', ex=True ):
				cmds.columnLayout( p = 'horizontalLayout_25', columnAttach=('right', 1), columnWidth = 68 )
				cmds.attrControlGrp( label = 'AA Filter', attribute='vraySettings.aaFilterOn' )
			#Override environment
			if cmds.attributeQuery( 'cam_overrideEnvtex', n='vraySettings', ex=True ):
				cmds.columnLayout( p = 'horizontalLayout_21', columnAttach=('right', 1), columnWidth = 137 )
				cmds.attrControlGrp( label = 'Override environment', attribute='vraySettings.cam_overrideEnvtex' )
			#DOF
			if cmds.attributeQuery( 'cam_dofOn', n='vraySettings', ex=True ):
				cmds.columnLayout( p = 'horizontalLayout_22', columnAttach=('right', 1), columnWidth = 56 )
				cmds.attrControlGrp( label = 'DOF', attribute='vraySettings.cam_dofOn' )
			#Motion blur
			if cmds.attributeQuery( 'cam_mbOn', n='vraySettings', ex=True ):
				cmds.columnLayout( p = 'horizontalLayout_23', columnAttach=('right', 1), columnWidth = 95 )
				cmds.attrControlGrp( label = 'Motion blur', attribute='vraySettings.cam_mbOn' )
			#Distributed rendering
			if cmds.attributeQuery( 'sys_distributed_rendering_on', n='vraySettings', ex=True ):
				cmds.columnLayout( p = 'horizontalLayout_24', columnAttach=('right', 1), columnWidth = 130 )
				cmds.attrControlGrp( label = 'Distributed rendering', attribute='vraySettings.sys_distributed_rendering_on' )
		'''
		#Ambient occlusion
		if cmds.attributeQuery( 'aoOn', n='vraySettings', ex=True ):
			actualValue = cmds.getAttr('vraySettings.aoOn')
			if actualValue:
				cmds.checkBox( 'AO_CB', edit = True, value= True )
			else:
				cmds.checkBox( 'AO_CB', edit = True, value= False )
		#Displacement
		if cmds.attributeQuery( 'globopt_geom_displacement', n='vraySettings', ex=True ):
			actualValue = cmds.getAttr('vraySettings.globopt_geom_displacement')
			if actualValue:
				cmds.checkBox( 'displacement_CB', edit = True, value= True )
			else:
				cmds.checkBox( 'displacement_CB', edit = True, value= False )
		#Reflection Refraction
		if cmds.attributeQuery( 'globopt_mtl_reflectionRefraction', n='vraySettings', ex=True ):
			actualValue = cmds.getAttr('vraySettings.globopt_mtl_reflectionRefraction')
			if actualValue:
				cmds.checkBox( 'reflectionrefraction_CB', edit = True, value= True )
			else:
				cmds.checkBox( 'reflectionrefraction_CB', edit = True, value= False )
		#Maps
		if cmds.attributeQuery( 'globopt_mtl_doMaps', n='vraySettings', ex=True ):
			actualValue = cmds.getAttr('vraySettings.globopt_mtl_doMaps')
			if actualValue:
				cmds.checkBox( 'maps_CB', edit = True, value= True )
			else:
				cmds.checkBox( 'maps_CB', edit = True, value= False )
		#Glossy Maps
		if cmds.attributeQuery( 'globopt_mtl_glossy', n='vraySettings', ex=True ):
			actualValue = cmds.getAttr('vraySettings.globopt_mtl_glossy')
			if actualValue:
				cmds.checkBox( 'glossyEffects_CB', edit = True, value= True )
			else:
				cmds.checkBox( 'glossyEffects_CB', edit = True, value= False )
		#Shadows
		if cmds.attributeQuery( 'globopt_light_doShadows', n='vraySettings', ex=True ):
			actualValue = cmds.getAttr('vraySettings.globopt_light_doShadows')
			if actualValue:
				cmds.checkBox( 'shadows_CB', edit = True, value= True )
			else:
				cmds.checkBox( 'shadows_CB', edit = True, value= False )
		#Antialiasing filter
		if cmds.attributeQuery( 'aaFilterOn', n='vraySettings', ex=True ):
			actualValue = cmds.getAttr('vraySettings.aaFilterOn')
			if actualValue:
				cmds.checkBox( 'antialiasingFilter_CB', edit = True, value= True )
			else:
				cmds.checkBox( 'antialiasingFilter_CB', edit = True, value= False )
		#Override environment
		if cmds.attributeQuery( 'cam_overrideEnvtex', n='vraySettings', ex=True ):
			actualValue = cmds.getAttr('vraySettings.cam_overrideEnvtex')
			if actualValue:
				cmds.checkBox( 'overrideEnvironment_CB', edit = True, value= True )
			else:
				cmds.checkBox( 'overrideEnvironment_CB', edit = True, value= False )
		#DOF
		if cmds.attributeQuery( 'cam_dofOn', n='vraySettings', ex=True ):
			actualValue = cmds.getAttr('vraySettings.cam_dofOn')
			if actualValue:
				cmds.checkBox( 'dof_CB', edit = True, value= True )
			else:
				cmds.checkBox( 'dof_CB', edit = True, value= False )
		#Motion blur
		if cmds.attributeQuery( 'cam_mbOn', n='vraySettings', ex=True ):
			actualValue = cmds.getAttr('vraySettings.cam_mbOn')
			if actualValue:
				cmds.checkBox( 'motionBlur_CB', edit = True, value= True )
			else:
				cmds.checkBox( 'motionBlur_CB', edit = True, value= False )
		#Distributed rendering
		if cmds.attributeQuery( 'sys_distributed_rendering_on', n='vraySettings', ex=True ):
			actualValue = cmds.getAttr('vraySettings.sys_distributed_rendering_on')
			if actualValue:
				cmds.checkBox( 'distributedRendering_CB', edit = True, value= True )
			else:
				cmds.checkBox( 'distributedRendering_CB', edit = True, value= False )
		'''
		#color mapping
		if cmds.attributeQuery( 'cmap_brightMult', n='vraySettings', ex=True ):
			#set to reinhard
			if not cmds.getAttr('vraySettings.cmap_type', lock = True):
				cmds.setAttr("vraySettings.cmap_type", 6)
			actualValue = cmds.getAttr('vraySettings.cmap_brightMult')
			cmds.intSlider(self.UI.colorMapping_SD, edit = True, value = actualValue*100.0)
			cmds.text('exponential_LB', edit = True, label = 'Exponential : ' + str(int(100 - (actualValue*100))) + '%')
			cmds.text('linear_LB', edit = True, label = 'Linear : ' + str(int(actualValue*100)) + '%')
			
	#============================================
	#
	# Check if file existe on disk and create
	#
	#============================================
	def createFile(self, file):
		if os.path.exists(self.dir + file):
			OpenMaya.MGlobal.displayInfo("[deeXVrayFast] File "+ file +" exists.")
		else:
			fichier = open(self.dir + file, 'w')
			fichier.close()
		return self.dir + file
	
	#============================================
	#
	# Check if dir existe on disk and create
	#
	#============================================
	def createDir(self, dir):
		if os.path.exists(self.dir + dir):
			OpenMaya.MGlobal.displayInfo("[deeXVrayFast] Dir "+ dir +" exists.")
		else:
			os.makedirs(self.dir + dir)
			OpenMaya.MGlobal.displayInfo("[deeXVrayFast] Dir "+ self.dir + dir +" created.")
		return self.dir + dir
	
	#============================================
	#
	# List all files on the disk
	#
	#============================================
	def listFile(self, dir = '', start = '', end =''):
		dirList = os.listdir(dir)
		listFile = list()
		for fname in dirList:
			if fname.startswith(start) and fname.endswith(end):
				listFile.append(fname)
		return listFile
	
	#============================================
	#
	# Settings, deexVrayFastPresetType
	#
	#============================================
	def deexVrayFastPresetType(self, *args):
		windows = deexVrayFastPresetType(self, self.actualPresetType)
		windows.show()

	#============================================
	#
	# Settings, optimization chooser
	#
	#============================================
	def optimizationChooser(self, *args):
		if cmds.window ("deexVrayFastOptimizationChooserWindows", exists = True):
			cmds.deleteUI ("deexVrayFastOptimizationChooserWindows", window=True)
		cmds.loadUI(uiFile=self.dir + '/deeXVrayFastOptimizationChooser.ui', verbose = False)
		cmds.showWindow('deexVrayFastOptimizationChooserWindows')
		
		#command
		cmds.button( 'OptimizationChooserSave_PB', edit = True, command= self.optimizationChooserSave)
		cmds.checkBox( 'OptimizationChooserGlobalOption_CB' , edit = True, changeCommand= self.optimizationChooserDisable1)
		cmds.checkBox( 'OptimizationChooserIrradianceMap_CB' , edit = True, changeCommand= self.optimizationChooserDisable2)
		cmds.checkBox( 'OptimizationChooserImageSampler_CB' , edit = True, changeCommand= self.optimizationChooserDisable3)
		cmds.checkBox( 'OptimizationChooserLightCache_CB' , edit = True, changeCommand= self.optimizationChooserDisable4)
		cmds.checkBox( 'OptimizationChooserDMCSampler_CB' , edit = True, changeCommand= self.optimizationChooserDisable5)
		cmds.checkBox( 'OptimizationChooserSystem_CB' , edit = True, changeCommand= self.optimizationChooserDisable6)
		
		#insertion maya command
		cmds.intField('OptimizationChooserGlobalOptionInt', p = 'OptimizationChooserverticalLayout_2')
		cmds.intField('OptimizationChooserIrradianceMapInt', p = 'OptimizationChooserverticalLayout_3')
		cmds.intField('OptimizationChooserImageSamplerInt', p = 'OptimizationChooserverticalLayout_4')
		cmds.intField('OptimizationChooserLightCacheInt', p = 'OptimizationChooserverticalLayout_5')
		cmds.intField('OptimizationChooserDMCSamplerInt', p = 'OptimizationChooserverticalLayout_6')
		cmds.intField('OptimizationChooserSystemInt', p = 'OptimizationChooserverticalLayout_7')
		
		#add setting
		if not cmds.attributeQuery( 'deeXVrayFastoptimizationChooserSettings', n='vraySettings', ex=True ):
			OpenMaya.MGlobal.displayInfo("[deeXVrayFast] Info : deeXVrayFastoptimizationChooserSettings use default settings.")
			dicoOptimizationChooser = None
		else:
			lines = cmds.getAttr('vraySettings.deeXVrayFastoptimizationChooserSettings')
			dicoOptimizationChooser = eval(lines)
		
		if dicoOptimizationChooser:
			cmds.checkBox( 'OptimizationChooserGlobalOption_CB' , value = dicoOptimizationChooser['OptimizationChooserGlobalOptionInt'][0] ,edit = True)
			cmds.intField('OptimizationChooserGlobalOptionInt', value = dicoOptimizationChooser['OptimizationChooserGlobalOptionInt'][1], enable = dicoOptimizationChooser['OptimizationChooserGlobalOptionInt'][0],  edit = True)
		
			cmds.checkBox( 'OptimizationChooserIrradianceMap_CB' , value = dicoOptimizationChooser['OptimizationChooserIrradianceMapInt'][0] ,edit = True)
			cmds.intField('OptimizationChooserIrradianceMapInt', value = dicoOptimizationChooser['OptimizationChooserIrradianceMapInt'][1], enable = dicoOptimizationChooser['OptimizationChooserIrradianceMapInt'][0], edit = True)
			
			cmds.checkBox( 'OptimizationChooserImageSampler_CB' , value = dicoOptimizationChooser['OptimizationChooserImageSamplerInt'][0] ,edit = True)
			cmds.intField('OptimizationChooserImageSamplerInt', value = dicoOptimizationChooser['OptimizationChooserImageSamplerInt'][1],  enable = dicoOptimizationChooser['OptimizationChooserImageSamplerInt'][0], edit = True)
			
			cmds.checkBox( 'OptimizationChooserLightCache_CB' , value = dicoOptimizationChooser['OptimizationChooserLightCacheInt'][0] ,edit = True)
			cmds.intField('OptimizationChooserLightCacheInt', value = dicoOptimizationChooser['OptimizationChooserLightCacheInt'][1], enable = dicoOptimizationChooser['OptimizationChooserLightCacheInt'][0],edit = True)
			
			cmds.checkBox( 'OptimizationChooserDMCSampler_CB' , value = dicoOptimizationChooser['OptimizationChooserDMCSamplerInt'][0] ,edit = True)
			cmds.intField('OptimizationChooserDMCSamplerInt', value = dicoOptimizationChooser['OptimizationChooserDMCSamplerInt'][1], enable = dicoOptimizationChooser['OptimizationChooserDMCSamplerInt'][0], edit = True)
			
			cmds.checkBox( 'OptimizationChooserSystem_CB' , value = dicoOptimizationChooser['OptimizationChooserSystemInt'][0] ,edit = True)
			cmds.intField('OptimizationChooserSystemInt', value = dicoOptimizationChooser['OptimizationChooserSystemInt'][1], enable = dicoOptimizationChooser['OptimizationChooserSystemInt'][0],edit = True)
	
	def optimizationChooserDisable1(self, *args):
		cmds.intField('OptimizationChooserGlobalOptionInt', edit = True, enable = cmds.checkBox( 'OptimizationChooserGlobalOption_CB' , query = True, value = True))
	
	def optimizationChooserDisable2(self, *args):
		cmds.intField('OptimizationChooserIrradianceMapInt', edit = True, enable = cmds.checkBox( 'OptimizationChooserIrradianceMap_CB' , query = True, value = True))
	
	def optimizationChooserDisable3(self, *args):
		cmds.intField('OptimizationChooserImageSamplerInt', edit = True, enable = cmds.checkBox( 'OptimizationChooserImageSampler_CB' , query = True, value = True))
	
	def optimizationChooserDisable4(self, *args):
		cmds.intField('OptimizationChooserLightCacheInt', edit = True, enable = cmds.checkBox( 'OptimizationChooserLightCache_CB' , query = True, value = True))
		
	def optimizationChooserDisable5(self, *args):
		cmds.intField('OptimizationChooserDMCSamplerInt', edit = True, enable = cmds.checkBox( 'OptimizationChooserDMCSampler_CB' , query = True, value = True))
	
	def optimizationChooserDisable6(self, *args):
		cmds.intField('OptimizationChooserSystemInt', edit = True, enable = cmds.checkBox( 'OptimizationChooserSystem_CB' , query = True, value = True))

	def optimizationChooserSave(self, *args):
		dico = {}
		dico['OptimizationChooserGlobalOptionInt'] = [cmds.intField('OptimizationChooserGlobalOptionInt', query = True, enable = True), cmds.intField('OptimizationChooserGlobalOptionInt', query = True, value = True)]
		dico['OptimizationChooserIrradianceMapInt'] = [cmds.intField('OptimizationChooserIrradianceMapInt', query = True, enable = True),cmds.intField('OptimizationChooserIrradianceMapInt', query = True, value = True)]
		dico['OptimizationChooserImageSamplerInt'] = [cmds.intField('OptimizationChooserImageSamplerInt', query = True, enable = True),cmds.intField('OptimizationChooserImageSamplerInt', query = True, value = True)]
		dico['OptimizationChooserLightCacheInt'] = [cmds.intField('OptimizationChooserLightCacheInt', query = True, enable = True),cmds.intField('OptimizationChooserLightCacheInt', query = True, value = True)]
		dico['OptimizationChooserDMCSamplerInt'] = [cmds.intField('OptimizationChooserDMCSamplerInt', query = True, enable = True),cmds.intField('OptimizationChooserDMCSamplerInt', query = True, value = True)]
		dico['OptimizationChooserSystemInt'] = [cmds.intField('OptimizationChooserSystemInt', query = True, enable = True),cmds.intField('OptimizationChooserSystemInt', query = True, value = True)]
		if not cmds.attributeQuery( 'deeXVrayFastoptimizationChooserSettings', n='vraySettings', ex=True ):
			locked = False
			if cmds.lockNode( 'vraySettings', query=True, lock=True )[0]:
				locked = True
				cmds.lockNode( 'vraySettings', lock=False )
			cmds.addAttr('vraySettings', ln = "deeXVrayFastoptimizationChooserSettings", dt = 'string')
			if locked:
				cmds.lockNode( 'vraySettings', lock=True )
			
		cmds.setAttr('vraySettings.deeXVrayFastoptimizationChooserSettings', str(dico), type = 'string')
		self.refresh()
	
	#============================================
	#
	# Back settings button
	#
	#============================================
	def backSetting(self, *args):
		if cmds.attributeQuery( 'deeXVrayFastActualSettings', n='vraySettings', ex=True ):
			#delete expression
			if cmds.objExists('deeXVrayFastExpression'):
				cmds.delete('deeXVrayFastExpression')
				OpenMaya.MGlobal.displayInfo('[deeXVrayFast] OdeeXVrayFastExpression deleted.')
			
			lines = cmds.getAttr('vraySettings.deeXVrayFastActualSettings')
			dico = eval(lines)
			for myAttr in dico:
				value = dico[myAttr]
				if type(dico[myAttr]) == list:
					value = dico[myAttr][0]
				if value:
					try:
						locked = 0
						if cmds.getAttr('vraySettings.' + myAttr,lock=True) == 1:
							pm.setAttr('vraySettings.' + myAttr, lock=False)
							locked = 1
						#set
						pm.setAttr('vraySettings.' + myAttr, value)
						if locked == 1:
							pm.setAttr('vraySettings.' + myAttr, lock=True)
					except:
						OpenMaya.MGlobal.displayInfo('[deeXVrayFast] ' + myAttr + " value can not be setted.")
			if not self.bashMode:
				cmds.control('menuSettings', enable=False, edit = True)
				cmds.control('menuPreset_Type', enable=False, edit = True)
				cmds.button( self.UI.optimize_BT, enable=False, edit = True)
				cmds.button( self.UI.backSetting_BT, enable=False, edit = True)
				cmds.control( 'resolution_GB', enable=False, edit=True )
				cmds.control( self.UI.fastControl_GB, enable=False, edit=True )
				cmds.control( 'quality_GB', enable=False, edit=True )
				cmds.button( self.UI.optimizeMat_BT, enable=False,edit = True)
				cmds.button( self.UI.optimizeLights_BT, enable=False, edit = True)
				cmds.button( self.UI.saveSetting_BT, enable=True, edit = True)
				cmds.control( 'preComp_GB', enable=False, edit=True )
			#delete attributs
			locked = False
			if cmds.lockNode( 'vraySettings', query=True, lock=True )[0]:
				locked = True
				cmds.lockNode( 'vraySettings', lock=False )
			attToDelete = ['deeXVrayFastLastQuality', 'deeXVrayFastOptimized', 'deeXVrayFastActualSettings', 'deeXVrayFastoptimizationChooserSettings', 'deeXVrayFastLastTypePreset', 'deeXVrayFastLastPresetPreComp']
			for myAttr in attToDelete:
				if cmds.attributeQuery( myAttr, n='vraySettings', ex=True ):
					cmds.deleteAttr( 'vraySettings.' + myAttr )
			if locked:
				cmds.lockNode( 'vraySettings', lock=True )
			OpenMaya.MGlobal.displayInfo('[deeXVrayFast] Original settings applied.')
		else:
			OpenMaya.MGlobal.displayError("[deeXVrayFast] deeXVrayFastActualSettings attribute not found")
		

	#============================================
	#
	# Save settings button
	#
	#============================================
	def saveSetting(self, *args):

		dicoAttr = {}
		for myAttr in cmds.listAttr('vraySettings'):
			try:
				dicoAttr[myAttr] = cmds.getAttr('vraySettings.' + myAttr)
			except:
				OpenMaya.MGlobal.displayInfo('[deeXVrayFast] ' + myAttr + " value can not be saved or have not value.")
		if not cmds.attributeQuery( 'deeXVrayFastActualSettings', n='vraySettings', ex=True ):
			locked = False
			if cmds.lockNode( 'vraySettings', query=True, lock=True )[0]:
				locked = True
				cmds.lockNode( 'vraySettings', lock=False )
			cmds.addAttr('vraySettings', ln = "deeXVrayFastActualSettings", dt = 'string')
			if locked:
				cmds.lockNode( 'vraySettings', lock=True )
		
		cmds.setAttr('vraySettings.deeXVrayFastActualSettings', str(dicoAttr), type = 'string')
		if not self.bashMode:
			cmds.button( self.UI.optimize_BT, enable=True, edit = True)
			cmds.button( self.UI.saveSetting_BT, enable=False, edit = True)
	
	#============================================
	#
	# Preset type get value
	#
	#============================================
	def presetTypeInitGetValue(self, preset):
		####################################get value from file
		fileName = self.dir + 'deeXVrayFastPresetType_' + preset + '.txt'
		dico = {}
		dicoMultiplicator = {}
		commentString = ""
		if os.path.exists(fileName):
			file = open(fileName, "r")
			lines = file.readlines()
			for line in lines:
				if re.search("vraySettings", line) and not re.search("multiplicator\|vraySettings", line):
					attribut = line.split("=")[0].strip()
					mediumValue = line.split("=")[1].split("|")[0].strip()
					veryHighValue = line.split("=")[1].split("|")[1].strip()
					dico[attribut] = [mediumValue, veryHighValue]
				elif re.search("multiplicator\|vraySettings", line):
					attribut = line.split("=")[0].strip().split("|")[1].strip()
					multiplicator = line.split("=")[1].strip()
					dicoMultiplicator[attribut] = [multiplicator]
				elif re.search("presetComment", line):
					commentString = str(line.split("=")[1].replace("\\\\", "\\").replace("\\n", "\n"))
			file.close()
		return dico, dicoMultiplicator, commentString
	
	#============================================
	#
	# PreComp get value
	#
	#============================================
	def preCompInitGetValue(self, preset):
		####################################get value from file
		fileName = self.dir + 'deeXVrayFastPresetPreComp_' + preset + '.txt'
		commentString = ""
		renderElements = ""
		nukeString = ""
		if os.path.exists(fileName):
			file = open(fileName, "r")
			lines = file.readlines()
			nukeFileStart = False
			for line in lines:
				if re.search("actualPresetPrecomp =", line):
					commentString = line.split("=")[1].strip()
				elif re.search("presetPass =", line):
					renderElements = line.split("=")[1].strip()
				elif re.search("###preComp###", line):#we start nuke file
					nukeFileStart = True
				elif nukeFileStart:
					nukeString += line
			file.close()
		return commentString, renderElements, nukeString
	
	#============================================
	#
	# PreComp add in combo box
	#
	#============================================
	def preCompInit(self, *args):
		#vraySetting last preComp
		#actual label in the menu
		if not self.bashMode:
			actualList = cmds.optionMenu(self.UI.preCompNuke_CB, query = True, itemListLong = True)
			actualListString = list()
			if actualList is not None:
				for item in actualList:
					itemString = cmds.menuItem( item, label=True, query = True )
					if itemString not in actualListString:
						actualListString.append(str(itemString))
		if not cmds.attributeQuery( 'deeXVrayFastLastPresetPreComp', n='vraySettings', ex=True ):
			#if scene not already optimized, add 'interior' to default value
			locked = False
			if cmds.lockNode( 'vraySettings', query=True, lock=True )[0]:
				locked = True
				cmds.lockNode( 'vraySettings', lock=False )
			cmds.addAttr('vraySettings', ln = "deeXVrayFastLastPresetPreComp", dt = 'string')
			if locked:
				cmds.lockNode( 'vraySettings', lock=True )
			
			cmds.setAttr('vraySettings.deeXVrayFastLastPresetPreComp', 'deeX_basic', type = 'string')
			if not self.bashMode:
				cmds.menuItem( label='deeX_basic', parent = self.UI.preCompNuke_CB )
				cmds.optionMenu(self.UI.preCompNuke_CB, edit = True, value = 'deeX_basic')
				actualListString.append('deeX_basic')
			self.actualPresetPrecomp = 'deeX_basic'
		else:
			#else get last preset type
			self.actualPresetPrecomp = cmds.getAttr('vraySettings.deeXVrayFastLastPresetPreComp')
			if not os.path.isfile(self.dir + 'deeXVrayFastPresetPreComp_' + self.actualPresetPrecomp + '.txt'):
				self.actualPresetPrecomp = 'deeX_basic'
			if not self.bashMode:
				if self.actualPresetPrecomp not in actualListString:
					cmds.menuItem( label=self.actualPresetPrecomp, parent = self.UI.preCompNuke_CB )
				cmds.optionMenu(self.UI.preCompNuke_CB, edit = True, value = self.actualPresetPrecomp)
				actualListString.append(self.actualPresetPrecomp)
		
		#check what preset type exist on the disk
		listPreset = self.listFile(dir = self.dir, start = 'deeXVrayFastPresetPreComp_', end = '.txt')
		for myPreset in listPreset:
			#get the preset name without extension
			presetName = myPreset.split('deeXVrayFastPresetPreComp_')[-1][:-4]
			if not self.bashMode:
				if presetName not in actualListString:
					cmds.menuItem( label=presetName, parent = self.UI.preCompNuke_CB )
		
		####################################get value from file
		commentString, renderElements, nukeString = self.preCompInitGetValue(self.actualPresetPrecomp)
		
		self.preCompString = nukeString
		self.preCompRenderElements = renderElements
		self.preCompComment = commentString

	#============================================
	#
	# Preset type add in combo box
	#
	#============================================
	def presetTypeInit(self, *args):
		#vraySetting last preset type
		#actual label in the menu
		if not self.bashMode:
			actualList = cmds.optionMenu(self.UI.presetType_CB, query = True, itemListLong = True)
			actualListString = list()
			if actualList is not None:
				for item in actualList:
					itemString = cmds.menuItem( item, label=True, query = True )
					if itemString not in actualListString:
						actualListString.append(str(itemString))
		if not cmds.attributeQuery( 'deeXVrayFastLastTypePreset', n='vraySettings', ex=True ):
			#if scene not already optimized, add 'interior' to default value
			locked = False
			if cmds.lockNode( 'vraySettings', query=True, lock=True )[0]:
				locked = True
				cmds.lockNode( 'vraySettings', lock=False )
			cmds.addAttr('vraySettings', ln = "deeXVrayFastLastTypePreset", dt = 'string')
			if locked:
				cmds.lockNode( 'vraySettings', lock=True )
			
			cmds.setAttr('vraySettings.deeXVrayFastLastTypePreset', 'deeX_interior', type = 'string')
			if not self.bashMode:
				cmds.menuItem( label='deeX_interior', parent = self.UI.presetType_CB )
				cmds.optionMenu(self.UI.presetType_CB, edit = True, value = 'deeX_interior')
				actualListString.append('deeX_interior')
			self.actualPresetType = 'deeX_interior'
		else:
			#else get last preset type
			self.actualPresetType = cmds.getAttr('vraySettings.deeXVrayFastLastTypePreset')
			if not os.path.isfile(self.dir + 'deeXVrayFastPresetType_' + self.actualPresetType + '.txt'):
				self.actualPresetType = 'deeX_interior'
			if not self.bashMode:
				if self.actualPresetType not in actualListString:
					cmds.menuItem( label=self.actualPresetType, parent = self.UI.presetType_CB )
				cmds.optionMenu(self.UI.presetType_CB, edit = True, value = self.actualPresetType)
				actualListString.append(self.actualPresetType)
			
		#check what preset type exist on the disk
		listPreset = self.listFile(dir = self.dir, start = 'deeXVrayFastPresetType_', end = '.txt')
		for myPreset in listPreset:
			#get the preset name without extension
			presetName = myPreset.split('deeXVrayFastPresetType_')[-1][:-4]
			if not self.bashMode:
				if presetName not in actualListString:
					cmds.menuItem( label=presetName, parent = self.UI.presetType_CB )
			
		####################################get value from file
		dico, dicoMultiplicator, commentString = self.presetTypeInitGetValue(self.actualPresetType)
	
		for myAttr in dico:
			if myAttr == 'vraySettings.globopt_mtl_maxDepth':
				####Global option Start####
				self.vraySettings_globopt_mtl_maxDepthM 		= dico[myAttr][0]
				self.vraySettings_globopt_mtl_maxDepthH 		= dico[myAttr][1]	
				####Global option End####
			
			if myAttr == 'vraySettings.dmcMaxSubdivs':
				####DMC AA Start####
				self.vraySettings_dmcMaxSubdivsM 				= dico[myAttr][0]
				self.vraySettings_dmcMaxSubdivsH 				= dico[myAttr][1]
				
			if myAttr == 'vraySettings.dmcMinSubdivs':
				self.vraySettings_dmcMinSubdivsM				= dico[myAttr][0]
				self.vraySettings_dmcMinSubdivsH				= dico[myAttr][1]
			
			if myAttr == 'vraySettings.dmcThreshold':	
				self.vraySettings_dmcThresholdM					= dico[myAttr][0]
				self.vraySettings_dmcThresholdH					= dico[myAttr][1]
				####DMC AA End####
			
			if myAttr == 'vraySettings.imap_minRate':	
				####Irradiance MAP Start####
				self.vraySettings_imap_minRateM					= dico[myAttr][0]
				self.vraySettings_imap_minRateH					= dico[myAttr][1]
			if myAttr == 'vraySettings.imap_maxRate':	
				self.vraySettings_imap_maxRateM					= dico[myAttr][0]
				self.vraySettings_imap_maxRateH					= dico[myAttr][1]
			if myAttr == 'vraySettings.imap_colorThreshold':	
				self.vraySettings_imap_colorThresholdM			= dico[myAttr][0]
				self.vraySettings_imap_colorThresholdH			= dico[myAttr][1]
			if myAttr == 'vraySettings.imap_normalThreshold':	
				self.vraySettings_imap_normalThresholdM			= dico[myAttr][0]
				self.vraySettings_imap_normalThresholdH			= dico[myAttr][1]
			if myAttr == 'vraySettings.imap_distanceThreshold':	
				self.vraySettings_imap_distanceThresholdM		= dico[myAttr][0]
				self.vraySettings_imap_distanceThresholdH		= dico[myAttr][1]
			if myAttr == 'vraySettings.imap_subdivs':	
				self.vraySettings_imap_subdivsM					= dico[myAttr][0]
				self.vraySettings_imap_subdivsH					= dico[myAttr][1]
			if myAttr == 'vraySettings.imap_interpSamples':	
				self.vraySettings_imap_interpSamplesM			= dico[myAttr][0]
				self.vraySettings_imap_interpSamplesH			= dico[myAttr][1]
			if myAttr == 'vraySettings.imap_detailRadius':	
				self.vraySettings_imap_detailRadiusM			= dico[myAttr][0]
				self.vraySettings_imap_detailRadiusH			= dico[myAttr][1]
			if myAttr == 'vraySettings.imap_detailSubdivsMult':	
				self.vraySettings_imap_detailSubdivsMultM		= dico[myAttr][0]
				self.vraySettings_imap_detailSubdivsMultH		= dico[myAttr][1]
			####Irradiance MAP End####
			
			if myAttr == 'vraySettings.subdivs':	
				####Light cache Start####
				self.vraySettings_subdivsM						= dico[myAttr][0]
				self.vraySettings_subdivsH						= dico[myAttr][1]
			if myAttr == 'vraySettings.sampleSize':	
				self.vraySettings_sampleSizeM					= dico[myAttr][0]
				self.vraySettings_sampleSizeH					= dico[myAttr][1]
			if myAttr == 'vraySettings.prefilterSamples':	
				self.vraySettings_prefilterSamplesM				= dico[myAttr][0]
				self.vraySettings_prefilterSamplesH				= dico[myAttr][1]
			if myAttr == 'vraySettings.filterSamples':	
				self.vraySettings_filterSamplesM				= dico[myAttr][0]
				self.vraySettings_filterSamplesH				= dico[myAttr][1]
				####Light cache End####
			
			if myAttr == 'vraySettings.dmcs_adaptiveAmount':	
				####DMC Sampler start####
				self.vraySettings_dmcs_adaptiveAmountM			= dico[myAttr][0]
				self.vraySettings_dmcs_adaptiveAmountH			= dico[myAttr][1]
			if myAttr == 'vraySettings.dmcs_adaptiveThreshold':	
				self.vraySettings_dmcs_adaptiveThresholdM		= dico[myAttr][0]
				self.vraySettings_dmcs_adaptiveThresholdH		= dico[myAttr][1]
			if myAttr == 'vraySettings.dmcs_adaptiveMinSamples':
				self.vraySettings_dmcs_adaptiveMinSamplesM		= dico[myAttr][0]
				self.vraySettings_dmcs_adaptiveMinSamplesH		= dico[myAttr][1]
			if myAttr == 'vraySettings.dmcs_subdivsMult':	
				self.vraySettings_dmcs_subdivsMultM				= dico[myAttr][0]
				self.vraySettings_dmcs_subdivsMultH				= dico[myAttr][1]
				####DMC Sampler end####
		
		#multiplicator	
		for myAttr in dicoMultiplicator:
			if myAttr == 'vraySettings.dmcMaxSubdivs':
				self.multiplicator_vraySettings_dmcMaxSubdivs	= dicoMultiplicator[myAttr][0]
			if myAttr == 'vraySettings.imap_minRate':
				self.multiplicator_vraySettings_imap_minRate	= dicoMultiplicator[myAttr][0]
			if myAttr == 'vraySettings.imap_maxRate':
				self.multiplicator_vraySettings_imap_maxRate	= dicoMultiplicator[myAttr][0]
			if myAttr == 'vraySettings.imap_detailRadius':
				self.multiplicator_vraySettings_imap_detailRadius	= dicoMultiplicator[myAttr][0]
				
		#preset comment
		self.presetComment = commentString
		
	#============================================
	#
	# Optimize button
	#
	#============================================
	def optimize(self, valueQuality = None):
		if valueQuality is not None:
			self.valueQuality = valueQuality

		locked = False
		if cmds.lockNode( 'vraySettings', query=True, lock=True )[0]:
			locked = True
			cmds.lockNode( 'vraySettings', lock=False )
		if not cmds.attributeQuery( 'deeXVrayFastOptimized', n='vraySettings', ex=True ):
			cmds.addAttr('vraySettings', ln = "deeXVrayFastOptimized", at = 'bool')
			cmds.setAttr('vraySettings.deeXVrayFastOptimized', 1)
		#vraySetting last quality
		if not cmds.attributeQuery( 'deeXVrayFastLastQuality', n='vraySettings', ex=True ):
			cmds.addAttr('vraySettings', ln = "deeXVrayFastLastQuality", at = 'long')
			cmds.setAttr('vraySettings.deeXVrayFastLastQuality', 50)
			if not self.bashMode:
				cmds.text('quality_LB', edit = True, label = 'Quality : ' + str(50))
		else:
			if not self.bashMode:
				actualValue = cmds.getAttr('vraySettings.deeXVrayFastLastQuality')
				cmds.text('quality_LB', edit = True, label = 'Quality : ' + str(actualValue))
				cmds.intSlider(self.UI.quality_SD, edit = True, value = actualValue)
		
		if locked:
			cmds.lockNode( 'vraySettings', lock=True )
		
		if not self.bashMode:
			cmds.control('menuSettings', enable=True, edit = True)
			cmds.control('menuPreset_Type', enable=True, edit = True)
			if cmds.attributeQuery( 'deeXVrayFastActualSettings', n='vraySettings', ex=True ):
				cmds.button( self.UI.backSetting_BT, enable=True, edit = True)
			cmds.button( self.UI.optimizeMat_BT, enable=True,edit = True)
			cmds.button( self.UI.optimizeLights_BT, enable=True, edit = True)
			cmds.control( 'resolution_GB', enable=True, edit=True )
			cmds.control( self.UI.fastControl_GB, enable=True, edit=True )
			cmds.control( 'quality_GB', enable=True, edit=True )
			cmds.control( 'preComp_GB', enable=True, edit=True )

		#vray fast control
		if not self.bashMode:
			self.fastControlInit()
		
		#vraySetting last preset type
		self.presetTypeInit()
		self.preCompInit()
		self.refresh()

	#============================================
	#
	# Optimize lights
	#
	#============================================	
	def optimizeLights(self, *args):
		allLights = cmds.ls(type = ['VRayLightIESShape', 'VRayLightRectShape', 'VRayLightSphereShape', 'VRayLightDomeShape', 'directionalLight', 'pointLight', 'spotLight', 'areaLight'])
		for myLight in allLights:
			if cmds.attributeQuery( 'subdivs', n=myLight, ex=True ):
				if not cmds.getAttr(myLight + '.subdivs', lock = True):
					if cmds.objectType(myLight) == 'VRayLightDomeShape':
						cmds.setAttr(myLight +".subdivs", 5*10)
					else:
						cmds.setAttr(myLight +".subdivs", 5)
			if cmds.attributeQuery( 'shadowRays', n=myLight, ex=True ):
				if not cmds.getAttr(myLight + '.shadowRays', lock = True):
					cmds.setAttr(myLight +".shadowRays", 5)
		OpenMaya.MGlobal.displayInfo('[deeXVrayFast] All lights optimized.')
	
	#============================================
	#
	# Optimize materials
	#
	#============================================	
	def optimizeMat(self, *args):
		allMaterials = cmds.ls(type = ['VRayCarPaintMtl', 'VRayFastSSS2', 'VRayMtl'])
		for myMat in allMaterials:
			if cmds.attributeQuery( 'subdivs', n=myMat, ex=True ):
				if not cmds.getAttr(myMat + '.subdivs', lock = True):
					cmds.setAttr(myMat +".subdivs", 7)
			if cmds.attributeQuery( 'reflectionSubdivs', n=myMat, ex=True ):
				if not cmds.getAttr(myMat + '.reflectionSubdivs', lock = True):
					cmds.setAttr(myMat +".reflectionSubdivs", 7)
			if cmds.attributeQuery( 'refractionSubdivs', n=myMat, ex=True ):
				if not cmds.getAttr(myMat + '.refractionSubdivs', lock = True):
					cmds.setAttr(myMat +".refractionSubdivs", 7)
		OpenMaya.MGlobal.displayInfo('[deeXVrayFast] All materials optimized.')
	#============================================
	#
	# Refresh Vray optimized setting
	#
	#============================================
	def refresh(self, *args):
		#never put 0 to the quality
		if not self.bashMode:
			if cmds.intSlider(self.UI.quality_SD, query = True, value = True) == 0:
				cmds.intSlider(self.UI.quality_SD, edit = True, value = 1)

		#optimization chooser
		if not cmds.attributeQuery( 'deeXVrayFastoptimizationChooserSettings', n='vraySettings', ex=True ):
			OpenMaya.MGlobal.displayInfo("[deeXVrayFast] Info : deeXVrayFastoptimizationChooserSettings use default settings.")
			dicoOptimizationChooser = None
		else:
			lines = cmds.getAttr('vraySettings.deeXVrayFastoptimizationChooserSettings')
			dicoOptimizationChooser = eval(lines)

		#resolution
		actualWidth = cmds.getAttr("vraySettings.width")
		actualHeight = cmds.getAttr("vraySettings.height")
		#cmds.intSlider('width_SD', edit = True, value = actualWidth)
		#cmds.intSlider('height_SD', edit = True, value = actualHeight)
		
		if not self.bashMode:
			cmds.intField(self.UI.pixelW_SB, edit = True, value = actualWidth)
			cmds.intField(self.UI.pixelH_SB, edit = True, value = actualHeight)
		valueAs = float((actualWidth*1.0)/(actualHeight*1.0))
		mel.eval('vrayUpdateAspectRatio;')
		cmds.setAttr("vraySettings.aspectRatio", valueAs)
		mel.eval('vrayChangeResolution();')
		
		resolution = actualWidth*actualHeight
		
		#=====================================Quality
		if not self.bashMode:
			self.valueQuality = cmds.intSlider(self.UI.quality_SD, query = True, value = True)
		if self.valueQuality is None:
			OpenMaya.MGlobal.displayError("You use Utils API. Please set a value for the quality.")
			return
		
		cmds.setAttr('vraySettings.deeXVrayFastLastQuality', self.valueQuality)
		####comment
		if not self.bashMode:
			cmds.text('quality_LB', edit = True, label = 'Quality : ' + str(self.valueQuality))
			if self.presetComment is not None or self.presetComment != "":
				cmds.scrollField(self.UI.presetComment_LB, edit = True, text = self.presetComment)
			else:
				cmds.scrollField(self.UI.presetComment_LB, edit = True, text = "No comment")
		#=====change slider color start
		biasValue = 0.3
		maxValue = 0.3
		#red
		tmpValue = 1.0 + (((self.valueQuality-50.0)/(100.0-50.0)) * (100.0-1.0))
		if tmpValue < 1.0:
			tmpValue = 1.0
		colorR = (tmpValue/100 * maxValue) + biasValue
		#blue
		tmpValue = 100.0 + (((self.valueQuality-1.0)/(50.0-1.0)) * (1.0-100.0))
		if tmpValue < 1.0:
			tmpValue = 1.0
		colorB = (tmpValue/100 * maxValue) + biasValue
		#green
		if self.valueQuality > 50:
			tmpValue = 100.0 + (((self.valueQuality-50.0)/(75.0-50.0)) * (1.0-100.0))
			if tmpValue < 1.0:
				tmpValue = 1.0
			colorG = (tmpValue/100 * maxValue) + biasValue
		elif self.valueQuality == 50:
			colorG = maxValue + biasValue
		else:
			tmpValue = 1.0 + (((self.valueQuality-25.0)/(50.0-25.0)) * (100.0-1.0))
			if tmpValue < 1.0:
				tmpValue = 1.0
			colorG = (tmpValue/100 * maxValue) + biasValue
		
		if not self.bashMode:
			cmds.intSlider(self.UI.quality_SD, edit = True, backgroundColor = [colorR, colorG, colorB])
		#=====change slider color end
		
		enable = True
		if dicoOptimizationChooser:
			self.valueQuality += dicoOptimizationChooser['OptimizationChooserGlobalOptionInt'][1]
			enable = dicoOptimizationChooser['OptimizationChooserGlobalOptionInt'][0]
		if enable:
			#################################################Global option Start#####################################################
			#=====================================set Global option globopt_mtl_limitDepth
			# quality 0 = 2
			# quality 50 = 4
			# quality 100 = 12
			# for 1 quality, add 0,16
			multiplier = (float(self.vraySettings_globopt_mtl_maxDepthH) - float(self.vraySettings_globopt_mtl_maxDepthM))/50
			minValue = float(self.vraySettings_globopt_mtl_maxDepthM)-(multiplier*50)
			#check if attribute is not locked
			if cmds.attributeQuery( 'globopt_mtl_limitDepth', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.globopt_mtl_limitDepth', lock = True):
					cmds.setAttr("vraySettings.globopt_mtl_limitDepth", 1)
				value = minValue + self.valueQuality*multiplier
				if value <= 2.0:
					value = 2.0
				#check if attribute is not locked
				if not cmds.getAttr('vraySettings.globopt_mtl_maxDepth', lock = True):
					cmds.setAttr("vraySettings.globopt_mtl_maxDepth", value )
			
		#################################################Global option End#####################################################
		
		enable = True
		if dicoOptimizationChooser:
			self.valueQuality += dicoOptimizationChooser['OptimizationChooserImageSamplerInt'][1]
			enable = dicoOptimizationChooser['OptimizationChooserImageSamplerInt'][0]
		if enable:
			#################################################DMC AA Start#####################################################
			#=====================================set DMC AA
			# Algo to find nice resolution
			# import math
			# subdi = 4.0
			# n = math.log(4.0/subdi)/math.log(0.6)
			# resolution = 307200 * 4**n
			# print resolution
			#
			# Algo to find nice radius
			# resolution = 307200
			# n = (math.log(307200.0/resolution)/math.log(4.0)) * -1
			# subdi = 4.0/ (1.2**n)
			# print print
			# 4
			#
			#
			# quality 0 = 2
			# quality 50 = 4
			# quality 100 = 10
			# for 1 quality, add 0,12
			
			multiplier = (float(self.vraySettings_dmcMaxSubdivsH) - float(self.vraySettings_dmcMaxSubdivsM))/50
			minValue = float(self.vraySettings_dmcMaxSubdivsM)-(multiplier*50)
			value = minValue + self.valueQuality*multiplier
			if value <= 2:
				value = 2.0
			
			n = (math.log(307200.0/resolution)/math.log(4.0)) * -1
			subdi = (math.ceil(value/ (float(self.multiplicator_vraySettings_dmcMaxSubdivs)**n)))
			
			#check if attribute is not locked
			if cmds.attributeQuery( 'dmcMaxSubdivs', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.dmcMaxSubdivs', lock = True):
					cmds.setAttr ("vraySettings.dmcMaxSubdivs", subdi)
			
			#=====================================set DMC AA dmcMinSubdivs
			# quality 0 = 1
			# quality 50 = 1
			# quality 100 = 3
			# for 1 quality, add 0,04
			multiplier = (float(self.vraySettings_dmcMinSubdivsH) - float(self.vraySettings_dmcMinSubdivsM))/50
			minValue = float(self.vraySettings_dmcMinSubdivsM)-(multiplier*50)
			value = minValue + self.valueQuality*multiplier
			if value <= 1:
				value = 1
			#check if attribute is not locked
			if cmds.attributeQuery( 'dmcMinSubdivs', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.dmcMinSubdivs', lock = True):
					cmds.setAttr ("vraySettings.dmcMinSubdivs", value)
			
			
			#=====================================set DMC AA dmcThreshold
			# quality 0 = 0.023
			# quality 50 = 0.012
			# quality 100 = 0.001
			# for 1 quality, remove 0,00022
			multiplier = (float(self.vraySettings_dmcThresholdM) - float(self.vraySettings_dmcThresholdH))/50
			minValue = float(self.vraySettings_dmcThresholdM)+(multiplier*50)
			value = minValue - self.valueQuality*multiplier
			if value <= 0.001:
				value = 0.001
			#check if attribute is not locked
			if cmds.attributeQuery( 'dmcThreshold', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.dmcThreshold', lock = True):
					cmds.setAttr("vraySettings.dmcThreshold", value)
			
			'''
			#=====================================set DMC AA aaFilterOn
			#check if attribute is not locked
			if cmds.attributeQuery( 'aaFilterOn', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.aaFilterOn', lock = True):
					cmds.setAttr("vraySettings.aaFilterOn", 0)
			'''
			
			#################################################DMC AA End#####################################################
		
		enable = True
		if dicoOptimizationChooser:
			self.valueQuality += dicoOptimizationChooser['OptimizationChooserIrradianceMapInt'][1]
			enable = dicoOptimizationChooser['OptimizationChooserIrradianceMapInt'][0]
		if enable:
			#################################################Irradiance MAP Start#####################################################
			#=====================================set irradiance map min
			# Algo to find nice resolution. -4 is the initial value for 640 * 480
			# ir = -5.0 <---- value i want to set
			# n = ((4+ir)*-1)/0.6
			# res = 307200.0* 4**n
			# print res
			#
			# For a value of -3.5, i set a value of -4
			# For a value of -4.5, i set a value of -5
			#
			# resolution = 307200
			# n = (math.log(307200.0/resolution)/math.log(4.0)) * -1
			# subdi = round((1.0 + (0.6*n))) * -1
			# print subdi
			# -4.0
			#
			# quality 0 = -5
			# quality 50 = -4
			# quality 100 = -3
			# for 1 quality, add 0,02
			
			"""
			if resolution >= 94.4940787421:
				cmds.setAttr ("vraySettings.imap_minRate", -1)
			if resolution >= 952.440631181:
				cmds.setAttr ("vraySettings.imap_minRate", -2)
			if resolution >= 9600.0:
				cmds.setAttr ("vraySettings.imap_minRate", -3)
			if resolution >= 96761.9366319:
				cmds.setAttr ("vraySettings.imap_minRate", -4)
			if resolution >= 975299.206329:
				cmds.setAttr ("vraySettings.imap_minRate", -5)
			if resolution >= 9830400.0:
				cmds.setAttr ("vraySettings.imap_minRate", -6)
			if resolution >= 99084223.1111:
				cmds.setAttr ("vraySettings.imap_minRate", -7)
			if resolution < 94.4940787421:
				cmds.setAttr ("vraySettings.imap_minRate", 0)
			"""
			multiplier = (float(self.vraySettings_imap_minRateH) - float(self.vraySettings_imap_minRateM))/50
			minValue = float(self.vraySettings_imap_minRateM)-(multiplier*50)
			value = minValue + self.valueQuality*multiplier
			
			n = (math.log(307200.0/resolution)/math.log(4.0)) * -1
			subdi = round((value + (float(self.multiplicator_vraySettings_imap_minRate)*n)))
			
			#check if attribute is not locked
			if cmds.attributeQuery( 'imap_minRate', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.imap_minRate', lock = True):
					cmds.setAttr ("vraySettings.imap_minRate", subdi)
				
			#=====================================set irradiance map max
			# Algo to find nice resolution. -1 is the initial value for 640 * 480
			# ir = -2 <---- value i want to set
			# n = ((1+ir)*-1)/0.6
			# res = 307200.0* 4**n
			# print res
			#
			# quality 0 = -2
			# quality 50 = -1
			# quality 100 = 0
			# for 1 quality, add 0,02
			"""
			if resolution >= 300.0:
				cmds.setAttr ("vraySettings.imap_maxRate", 2)
			if resolution >= 3023.81051975:
				cmds.setAttr ("vraySettings.imap_maxRate", 1)
			if resolution >= 30478.1001978:
				cmds.setAttr ("vraySettings.imap_maxRate", 0)
			if resolution >= 307200.0:
				cmds.setAttr ("vraySettings.imap_maxRate", -1)
			if resolution >= 3096381.97222:
				cmds.setAttr ("vraySettings.imap_maxRate", -2)
			if resolution >= 31209574.6025:
				cmds.setAttr ("vraySettings.imap_maxRate", -3)
			if resolution >= 314572800.0:
				cmds.setAttr ("vraySettings.imap_maxRate", -4)
			if resolution < 300.0:
				cmds.setAttr ("vraySettings.imap_maxRate", 3)
			"""
			multiplier = (float(self.vraySettings_imap_maxRateH) - float(self.vraySettings_imap_maxRateM))/50
			minValue = float(self.vraySettings_imap_maxRateM)-(multiplier*50)
			value = minValue + self.valueQuality*multiplier
			if value >= -1.0:
				value = -1.0
			n = (math.log(307200.0/resolution)/math.log(4.0)) * -1
			subdi = round((value + (float(self.multiplicator_vraySettings_imap_maxRate)*n)))
			#check if attribute is not locked
			if cmds.attributeQuery( 'imap_maxRate', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.imap_maxRate', lock = True):
					cmds.setAttr ("vraySettings.imap_maxRate", subdi)
			
			#=====================================set irradiance map colorThreshold
			# quality 0 = 0.717
			# quality 50 = 0.45
			# quality 100 = 0.183
			# for 1 quality, remove 0,00534
			multiplier = (float(self.vraySettings_imap_colorThresholdM) - float(self.vraySettings_imap_colorThresholdH))/50
			minValue = float(self.vraySettings_imap_colorThresholdM)+(multiplier*50)
			value = minValue - self.valueQuality*multiplier
			if value <= 0.001:
				value = 0.001
			#check if attribute is not locked
			if cmds.attributeQuery( 'imap_colorThreshold', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.imap_colorThreshold', lock = True):
					cmds.setAttr("vraySettings.imap_colorThreshold", value)
			
			#=====================================set irradiance map normalThreshold
			# quality 0 = 0.3
			# quality 50 = 0.2
			# quality 100 = 0.1
			# for 1 quality, remove 0,002
			multiplier = (float(self.vraySettings_imap_normalThresholdM) - float(self.vraySettings_imap_normalThresholdH))/50
			minValue = float(self.vraySettings_imap_normalThresholdM)+(multiplier*50)
			value = minValue - self.valueQuality*multiplier
			if value <= 0.001:
				value = 0.001
			#check if attribute is not locked
			if cmds.attributeQuery( 'imap_normalThreshold', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.imap_normalThreshold', lock = True):
					cmds.setAttr("vraySettings.imap_normalThreshold", value)
			
			#=====================================set irradiance map distanceThreshold
			# quality 0 = 0.0
			# quality 50 = 0.05
			# quality 100 = 0.383
			# for 1 quality, add 0,00666
			multiplier = (float(self.vraySettings_imap_distanceThresholdH) - float(self.vraySettings_imap_distanceThresholdM))/50
			minValue = float(self.vraySettings_imap_distanceThresholdM)-(multiplier*50)
			value = minValue + (multiplier * self.valueQuality)
			if value <= 0:
				value = 0
			#check if attribute is not locked
			if cmds.attributeQuery( 'imap_distanceThreshold', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.imap_distanceThreshold', lock = True):
					cmds.setAttr("vraySettings.imap_distanceThreshold", value )
			
			#=====================================set irradiance map subdivs
			# quality 0 = 24
			# quality 50 = 18
			# quality 100 = 12
			# for 1 quality, remove 0,12
			multiplier = (float(self.vraySettings_imap_subdivsM) - float(self.vraySettings_imap_subdivsH))/50
			minValue = float(self.vraySettings_imap_subdivsM)+(multiplier*50)
			value = minValue - self.valueQuality*multiplier
			if value <= 1:
				value = 1
			#check if attribute is not locked
			if cmds.attributeQuery( 'imap_subdivs', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.imap_subdivs', lock = True):
					cmds.setAttr("vraySettings.imap_subdivs", value)
			
			#=====================================set irradiance map interpSamples
			# quality 0 = 36
			# quality 50 = 28
			# quality 100 = 20
			# for 1 quality, remove 0,16
			multiplier = (float(self.vraySettings_imap_interpSamplesM) - float(self.vraySettings_imap_interpSamplesH))/50
			minValue = float(self.vraySettings_imap_interpSamplesM)+(multiplier*50)
			value = minValue - self.valueQuality*multiplier
			if value <= 1:
				value = 1
			#check if attribute is not locked
			if cmds.attributeQuery( 'imap_interpSamples', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.imap_interpSamples', lock = True):
					cmds.setAttr("vraySettings.imap_interpSamples", value )
			
			#=====================================set irradiance map detail radius
			# Algo to find nice detail radius depend of the resolution
			# resolution = 307200
			# n = (math.log(307200.0/resolution)/math.log(4.0)) * -1
			# radius = 12* (1.75**n)
			# print radius
			# 12
			#
			#
			# quality 0 = 1
			# quality 50 = 12
			# quality 100 = 116/3 = 38,66666666666667
			# for 1 quality, add ((116/3.0) - 12.0)/50.0 = 0.533333333333
			
			
			multiplier = (float(eval(str(self.vraySettings_imap_detailRadiusH))) - float(self.vraySettings_imap_detailRadiusM))/50
			minValue = float(self.vraySettings_imap_detailRadiusM)-(multiplier*50)
			value = minValue + self.valueQuality*multiplier
			if value <= 1:
				value = 1
	
			n = (math.log(307200.0/resolution)/math.log(4.0)) * -1
			radius = value* (float(self.multiplicator_vraySettings_imap_detailRadius)**n)
			
			#check if attribute is not locked
			if cmds.attributeQuery( 'imap_detailRadius', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.imap_detailRadius', lock = True):
					cmds.setAttr("vraySettings.imap_detailRadius", radius)
						
			#=====================================set irradiance map detailSubdivsMult
			# quality 0 = 0.184
			# quality 50 = 0.278
			# quality 100 = 0.372
			# for 1 quality, add 0,00188
			multiplier = (float(self.vraySettings_imap_detailSubdivsMultH) - float(self.vraySettings_imap_detailSubdivsMultM))/50
			minValue = float(self.vraySettings_imap_detailSubdivsMultM)-(multiplier*50)
			value =  minValue + self.valueQuality *multiplier
			if value <= 0.001:
				value = 0.001
			#check if attribute is not locked
			if cmds.attributeQuery( 'imap_detailSubdivsMult', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.imap_detailSubdivsMult', lock = True):
					cmds.setAttr("vraySettings.imap_detailSubdivsMult", value )
			
			#################################################Irradiance MAP End######################################################
		
		enable = True
		if dicoOptimizationChooser:
			self.valueQuality += dicoOptimizationChooser['OptimizationChooserLightCacheInt'][1]
			enable = dicoOptimizationChooser['OptimizationChooserLightCacheInt'][0]
		if enable:
			#################################################Light cache Start#####################################################
			#=====================================set Light cache subdivs
			# quality 0 = 388
			# quality 50 = 700
			# quality 100 = 1633
			# for 1 quality, add 18,66
			multiplier = (float(self.vraySettings_subdivsH) - float(self.vraySettings_subdivsM))/50
			minValue = float(self.vraySettings_subdivsM)-(multiplier*50)
			value = minValue + self.valueQuality*multiplier
			if value <= 388:
				value = 388
			#check if attribute is not locked
			if cmds.attributeQuery( 'subdivs', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.subdivs', lock = True):
					cmds.setAttr("vraySettings.subdivs", value )
			
			#=====================================set Light cache sampleSize
			# quality 0 = 0.02
			# quality 50 = 0.015
			# quality 100 = 0.008
			# for 1 quality, remove 0,00014
			multiplier = (float(self.vraySettings_sampleSizeM) - float(self.vraySettings_sampleSizeH))/50
			minValue = float(self.vraySettings_sampleSizeM)+(multiplier*50)
			value = minValue - self.valueQuality*multiplier
			if value >= 0.02:
				value = 0.02
			if value <= 0.001:
				value = 0.001
			#check if attribute is not locked
			if cmds.attributeQuery( 'sampleSize', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.sampleSize', lock = True):
					cmds.setAttr("vraySettings.sampleSize", value )
			
			#=====================================set Light cache prefilterSamples
			# quality 0 = 11
			# quality 50 = 32
			# quality 100 = 117
			# for 1 quality, remove 0,00014
			multiplier = (float(self.vraySettings_prefilterSamplesH) - float(self.vraySettings_prefilterSamplesM))/50
			minValue = float(self.vraySettings_prefilterSamplesM)-(multiplier*50)
			value = minValue + self.valueQuality*multiplier
			if value <= 11:
				value = 11
			#check if attribute is not locked
			if cmds.attributeQuery( 'prefilter', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.prefilter', lock = True):
					cmds.setAttr("vraySettings.prefilter", 1 )
			#check if attribute is not locked
			if cmds.attributeQuery( 'prefilterSamples', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.prefilterSamples', lock = True):
					cmds.setAttr("vraySettings.prefilterSamples", value )
			#check if attribute is not locked
			if cmds.attributeQuery( 'useForGlossy', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.useForGlossy', lock = True):
					cmds.setAttr("vraySettings.useForGlossy", 1)
			#check if attribute is not locked
			if cmds.attributeQuery( 'useRetraceThreshold', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.useRetraceThreshold', lock = True):
					cmds.setAttr("vraySettings.useRetraceThreshold", 1)
			
			#=====================================set Light cache filterSamples
			# quality 0 = 3
			# quality 50 = 5
			# quality 100 = 12
			# for 1 quality, remove 0,14
			multiplier = (float(self.vraySettings_filterSamplesH) - float(self.vraySettings_filterSamplesM))/50
			minValue = float(self.vraySettings_filterSamplesM)-(multiplier*50)
			value = minValue + self.valueQuality*multiplier
			if value <= 3:
				value = 3
			#check if attribute is not locked
			if cmds.attributeQuery( 'filterSamples', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.filterSamples', lock = True):
					cmds.setAttr("vraySettings.filterSamples", value )
			
			#=====================================Expression start
			line = 'string $core[] = `hardware -npr`;\nvraySettings.numPasses = $core[0];'
			if not cmds.objExists('deeXVrayFastExpression'):
				cmds.expression( n='deeXVrayFastExpression', s=line )
			else:
				actualExpression = cmds.expression( 'deeXVrayFastExpression', s=True, query=True)
				if line not in actualExpression:
					cmds.expression( 'deeXVrayFastExpression', edit = True, s = actualExpression + '\n' + line)
			#=====================================Expression end
		else:
			#delete expression system
			line = 'string $core[] = `hardware -npr`;\nvraySettings.numPasses = $core[0];'
			if cmds.objExists('deeXVrayFastExpression'):
				actualExpression = cmds.expression( 'deeXVrayFastExpression', s=True, query=True)
				if line in actualExpression:
					cmds.expression( 'deeXVrayFastExpression', edit = True, s = actualExpression.replace(line, ""))
			#################################################Light cache End#####################################################
		
		enable = True
		if dicoOptimizationChooser:
			self.valueQuality += dicoOptimizationChooser['OptimizationChooserDMCSamplerInt'][1]
			enable = dicoOptimizationChooser['OptimizationChooserDMCSamplerInt'][0]
		if enable:
			#################################################DMC Sampler start######################################################
			#=====================================set DMC Sampler adaptiveAmount
			# quality 0 = 1.0
			# quality 50 = 0.8
			# quality 100 = 0.533
			# for 1 quality, remove 0,00534
			multiplier = (float(self.vraySettings_dmcs_adaptiveAmountM) - float(self.vraySettings_dmcs_adaptiveAmountH))/50
			minValue = float(self.vraySettings_dmcs_adaptiveAmountM)+(multiplier*50)
			value = minValue - self.valueQuality*multiplier
			if value >= 1.0:
				value = 1.0
			if value <= 0.001:
				value = 0.001
			#check if attribute is not locked
			if cmds.attributeQuery( 'dmcs_adaptiveAmount', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.dmcs_adaptiveAmount', lock = True):
					cmds.setAttr("vraySettings.dmcs_adaptiveAmount", value )
			
			#=====================================set DMC Sampler adaptiveThreshold
			# quality 0 = 0.008
			# quality 50 = 0.005
			# quality 100 = 0.002
			# for 1 quality, remove 0,00006
			multiplier = (float(self.vraySettings_dmcs_adaptiveThresholdM) - float(self.vraySettings_dmcs_adaptiveThresholdH))/50
			minValue = float(self.vraySettings_dmcs_adaptiveThresholdM)+(multiplier*50)
			value = minValue - self.valueQuality *multiplier
			if value <= 0.001:
				value = 0.001
			#check if attribute is not locked
			if cmds.attributeQuery( 'dmcs_adaptiveThreshold', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.dmcs_adaptiveThreshold', lock = True):
					cmds.setAttr("vraySettings.dmcs_adaptiveThreshold", value)
			
			#=====================================set DMC Sampler adaptiveMinSamples
			# quality 0 = 8
			# quality 50 = 128
			# quality 100 = 299
			# for 1 quality, add 3,42
			multiplier = (float(self.vraySettings_dmcs_adaptiveMinSamplesH) - float(self.vraySettings_dmcs_adaptiveMinSamplesM))/50
			minValue = float(self.vraySettings_dmcs_adaptiveMinSamplesM)-(multiplier*50)
			value = minValue + self.valueQuality*multiplier
			if value <= 8.0:
				value = 8.0
			#check if attribute is not locked
			if cmds.attributeQuery( 'dmcs_adaptiveMinSamples', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.dmcs_adaptiveMinSamples', lock = True):
					cmds.setAttr("vraySettings.dmcs_adaptiveMinSamples", value )
			
			#=====================================set DMC Sampler subdivsMult
			# quality 0 = 1
			# quality 50 = 2
			# quality 100 = 10
			# for 1 quality, add 0,16
			multiplier = (float(self.vraySettings_dmcs_subdivsMultH) - float(self.vraySettings_dmcs_subdivsMultM))/50
			minValue = float(self.vraySettings_dmcs_subdivsMultM)-(multiplier*50)
			value = minValue + self.valueQuality*multiplier
			if value <= 1.0:
				value = 1.0
			#check if attribute is not locked
			if cmds.attributeQuery( 'dmcs_subdivsMult', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.dmcs_subdivsMult', lock = True):
					cmds.setAttr("vraySettings.dmcs_subdivsMult", value )
			#################################################DMC Sampler end######################################################
		
		enable = True
		if dicoOptimizationChooser:
			self.valueQuality += dicoOptimizationChooser['OptimizationChooserSystemInt'][1]
			enable = dicoOptimizationChooser['OptimizationChooserSystemInt'][0]
		if enable:
			#######################################Default subdi and displacement start###########################################
			#check if attribute is not locked
			if cmds.attributeQuery( 'ddisplac_maxSubdivs', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.ddisplac_maxSubdivs', lock = True):
					cmds.setAttr("vraySettings.ddisplac_maxSubdivs", 23 )
			#######################################Default subdi and displacement end#############################################
			
			#######################################System start###########################################
			#check if attribute is not locked
			if cmds.attributeQuery( 'sys_regsgen_xylocked', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.sys_regsgen_xylocked', lock = True):
					cmds.setAttr("vraySettings.sys_regsgen_xylocked", 0)
			core  = int(cmds.hardware(npr = True)[0])
			count = 0
			value = 60
			for bucketSize in [actualWidth, actualHeight]:
				finalValue = 0
				lastValue = 80
				for i in range(40,80):
					if bucketSize%i <= lastValue:
						lastValue = bucketSize%i
						if lastValue == 0:
							finalValue = i
						else:
							finalValue = i + 1
				if count == 0:#it is x
					if actualWidth <= 40*core:
						value = math.ceil(actualWidth/int(core))
						if value <= 1:
							value = 1
						#check if attribute is not locked
						if cmds.attributeQuery( 'sys_regsgen_xc', n='vraySettings', ex=True ):
							if not cmds.getAttr('vraySettings.sys_regsgen_xc', lock = True):
								cmds.setAttr("vraySettings.sys_regsgen_xc", value)
					else:
						value = finalValue
						if value <= 1:
							value = 1
						#check if attribute is not locked
						if cmds.attributeQuery( 'sys_regsgen_xc', n='vraySettings', ex=True ):
							if not cmds.getAttr('vraySettings.sys_regsgen_xc', lock = True):
								cmds.setAttr("vraySettings.sys_regsgen_xc", value)
				else:#it is y
					if actualHeight <= 40*core:
						value = math.ceil(actualHeight/int(core))
						if value <= 1:
							value = 1
						#check if attribute is not locked
						if cmds.attributeQuery( 'sys_regsgen_yc', n='vraySettings', ex=True ):
							if not cmds.getAttr('vraySettings.sys_regsgen_yc', lock = True):
								cmds.setAttr("vraySettings.sys_regsgen_yc", value)
					else:
						value = finalValue
						if value <= 1:
							value = 1
						#check if attribute is not locked
						if cmds.attributeQuery( 'sys_regsgen_yc', n='vraySettings', ex=True ):
							if not cmds.getAttr('vraySettings.sys_regsgen_yc', lock = True):
								cmds.setAttr("vraySettings.sys_regsgen_yc", value)
				count += 1
			
			#check if attribute is not locked
			if cmds.attributeQuery( 'sys_regsgen_seqtype', n='vraySettings', ex=True ):
				if not cmds.getAttr('vraySettings.sys_regsgen_seqtype', lock = True):
					cmds.setAttr('vraySettings.sys_regsgen_seqtype', 3)
			#######################################System end#############################################
		
			#=====================================Expression start
			line = 'python(\"import maya.cmds as cmds\\nvalue = cmds.memory(phy=True, megaByte=True)\\nif isinstance( value, int ):\\n\\tmemory = float(value)\\nelse:\\n\\tmemory = float(value[0])\");\nfloat $memory = `python "memory"`;\nvraySettings.sys_rayc_dynMemLimit = $memory - 1500;'
			if not cmds.objExists('deeXVrayFastExpression'):
				cmds.expression( n='deeXVrayFastExpression', s=line )
			else:
				actualExpression = cmds.expression( 'deeXVrayFastExpression', s=True, query=True)
				if line not in actualExpression:
					cmds.expression( 'deeXVrayFastExpression', edit = True, s = actualExpression + '\n' +line)
			#=====================================Expression end
		else:
			#delete expression system
			line = 'python(\"import maya.cmds as cmds\\nvalue = cmds.memory(phy=True, megaByte=True)\\nif isinstance( value, int ):\\n\\tmemory = float(value)\\nelse:\\n\\tmemory = float(value[0])\");\nfloat $memory = `python "memory"`;\nvraySettings.sys_rayc_dynMemLimit = $memory - 1500;'
			if cmds.objExists('deeXVrayFastExpression'):
				actualExpression = cmds.expression( 'deeXVrayFastExpression', s=True, query=True)
				if line in actualExpression:
					cmds.expression( 'deeXVrayFastExpression', edit = True, s = actualExpression.replace(line, ""))
		
		#=====================================PreComp
		####comment
		if not self.bashMode:
			if self.preCompComment is not None or self.preCompComment != "":
				cmds.scrollField(self.UI.preCompComment_LB, edit = True, text = self.preCompComment)
			else:
				cmds.scrollField(self.UI.preCompComment_LB, edit = True, text = "No comment")
	
	#============================================
	#
	# Change windows size
	#
	#============================================
	def sizeWindowsResolution(self, *args):
		if not cmds.checkBox( self.UI.resolutionVisible_CB, query = True, value=True ):
			#self.UI.height -= cmds.control( 'resolution_GB', query=True, height=True)
			self.UI.height -= 260
		else:
			#self.UI.height += cmds.control( 'resolution_GB', query=True, height=True)
			self.UI.height += 260
		
		if cmds.window (self.UI.ui, query = True, ex = True):
			cmds.window (self.UI.ui, edit = True, height = self.UI.height)
			
	def sizeWindowsFastControl(self, *args):
		if not cmds.checkBox( self.UI.fastControlVisible_CB, query = True, value=True ):
			#self.UI.height -= cmds.control( self.UI.fastControl_GB, query=True, height=True)
			self.UI.height -= 250
		else:
			#self.UI.height += cmds.control( self.UI.fastControl_GB, query=True, height=True)
			self.UI.height += 250
		if cmds.window (self.UI.ui, query = True, ex = True):
			cmds.window (self.UI.ui, edit = True, height = self.UI.height)
			
	def sizeWindowsQuality(self, *args):
		if not cmds.checkBox( self.UI.qualityVisible_CB, query = True, value=True ):
			#self.UI.height -= cmds.control( 'quality_GB', query=True, height=True)
			self.UI.height -= 224
		else:
			#self.UI.height += cmds.control( 'quality_GB', query=True, height=True)
			self.UI.height += 224
		if cmds.window (self.UI.ui, query = True, ex = True):
			cmds.window (self.UI.ui, edit = True, height = self.UI.height)
			
	def sizeWindowsPreComp(self, *args):
		if not cmds.checkBox( self.UI.preCompVisible_CB, query = True, value=True ):
			#self.UI.height -= cmds.control( 'quality_GB', query=True, height=True)
			self.UI.height -= 100
		else:
			#self.UI.height += cmds.control( 'quality_GB', query=True, height=True)
			self.UI.height += 100
		if cmds.window (self.UI.ui, query = True, ex = True):
			cmds.window (self.UI.ui, edit = True, height = self.UI.height)

	#============================================
	#
	# Preset Resolution button
	#
	#============================================
	"""
	def changeResolutionwidth_SD(self, *args):
		cmds.setAttr("vraySettings.width", cmds.intSlider('width_SD', query = True, value = True))
		self.refresh()
	
	def changeResolutionheight_SD(self, *args):
		cmds.setAttr("vraySettings.height", cmds.intSlider('height_SD', query = True, value = True))
		self.refresh()
	"""
	
	def changeResolutionpixelW_SB(self, *args):
		cmds.setAttr("vraySettings.width", cmds.intField(self.UI.pixelW_SB, q = True, value = True))
		self.refresh()
	
	def changeResolutionpixelH_SB(self, *args):
		cmds.setAttr("vraySettings.height", cmds.intField(self.UI.pixelH_SB, q = True, value = True))
		self.refresh()		
	
	def changeResolutionPreset01(self, *args):
		cmds.setAttr("vraySettings.width", 320)
		cmds.setAttr("vraySettings.height", 240)
		self.refresh()
	
	def changeResolutionPreset02(self, *args):
		cmds.setAttr("vraySettings.width", 640)
		cmds.setAttr("vraySettings.height", 480)
		self.refresh()
	
	def changeResolutionPreset03(self, *args):
		cmds.setAttr("vraySettings.width", 1024)
		cmds.setAttr("vraySettings.height", 1024)
		self.refresh()
		
	def changeResolutionPreset04(self, *args):
		cmds.setAttr("vraySettings.width", 2048)
		cmds.setAttr("vraySettings.height", 2048)
		self.refresh()
	
	def changeResolutionPreset05(self, *args):
		cmds.setAttr("vraySettings.width", 2048)
		cmds.setAttr("vraySettings.height", 1152)
		self.refresh()
	
	def changeResolutionPreset06(self, *args):
		cmds.setAttr("vraySettings.width", 1024)
		cmds.setAttr("vraySettings.height", 768)
		self.refresh()
	
	def changeResolutionPreset07(self, *args):
		cmds.setAttr("vraySettings.width", 1280)
		cmds.setAttr("vraySettings.height", 1024)
		self.refresh()
	
	def changeResolutionPreset08(self, *args):
		cmds.setAttr("vraySettings.width", 1280)
		cmds.setAttr("vraySettings.height", 720)
		self.refresh()
	
	def changeResolutionPreset09(self, *args):
		cmds.setAttr("vraySettings.width", 1920)
		cmds.setAttr("vraySettings.height", 1080)
		self.refresh()
		
	def changeResolutionPreset10(self, *args):
		cmds.setAttr("vraySettings.width", 4096)
		cmds.setAttr("vraySettings.height", 4096)
		self.refresh()
	
	def changeResolutionC1(self, *args):
		w = cmds.getAttr("vraySettings.width")/2
		h = cmds.getAttr("vraySettings.height")/2
		if w <= 2:
			w = 2
		if h <= 2:
			h = 2
		cmds.setAttr("vraySettings.width", w)
		cmds.setAttr("vraySettings.height", h)
		self.refresh()
	
	def changeResolutionC2(self, *args):
		w = cmds.getAttr("vraySettings.width")/4
		h = cmds.getAttr("vraySettings.height")/4
		if w <= 2:
			w = 2
		if h <= 2:
			h = 2
		cmds.setAttr("vraySettings.width", w)
		cmds.setAttr("vraySettings.height", h)
		self.refresh()
	
	def changeResolutionC3(self, *args):
		cmds.setAttr("vraySettings.width", cmds.getAttr("vraySettings.width")*2)
		cmds.setAttr("vraySettings.height", cmds.getAttr("vraySettings.height")*2)
		self.refresh()
		
	def changeResolutionC4(self, *args):
		cmds.setAttr("vraySettings.width", cmds.getAttr("vraySettings.width")*4)
		cmds.setAttr("vraySettings.height", cmds.getAttr("vraySettings.height")*4)
		self.refresh()
	
	def fastControlGIType(self, *args):
		actualValue = cmds.optionMenu(self.UI.GIType_CB, query = True, select = True)
		if actualValue == 1:
			cmds.setAttr ('vraySettings.primaryEngine', 3)
			cmds.setAttr ('vraySettings.secondaryEngine', 3)
			cmds.setAttr ('vraySettings.imap_detailEnhancement', False)
		elif actualValue == 2:
			cmds.setAttr ('vraySettings.primaryEngine', 0)
			cmds.setAttr ('vraySettings.secondaryEngine', 3)
			cmds.setAttr ('vraySettings.imap_detailEnhancement', False)
		elif actualValue == 3:
			cmds.setAttr ('vraySettings.primaryEngine', 0)
			cmds.setAttr ('vraySettings.secondaryEngine', 3)
			cmds.setAttr ('vraySettings.imap_detailEnhancement', True)
		elif actualValue == 4:
			cmds.setAttr ('vraySettings.primaryEngine', 0)
			cmds.setAttr ('vraySettings.secondaryEngine', 2)
			cmds.setAttr ('vraySettings.imap_detailEnhancement', False)
		elif actualValue == 5:
			cmds.setAttr ('vraySettings.primaryEngine', 0)
			cmds.setAttr ('vraySettings.secondaryEngine', 2)
			cmds.setAttr ('vraySettings.imap_detailEnhancement', True)
		elif actualValue == 6:
			cmds.setAttr ('vraySettings.primaryEngine', 2)
			cmds.setAttr ('vraySettings.secondaryEngine', 2)
			cmds.setAttr ('vraySettings.imap_detailEnhancement', False)
		
		self.refresh()
		'''
		Light Cache + Light Cache (preview render)
		Irradiance Map + Light Cache (best ratio between quality/speed)
		Irradiance Map + Detail enhancement + Light Cache (more precise)
		Irradiance Map + Brute Force
		Irradiance Map + Detail enhancement + Brute Force
		Brute Force + Brute Force (best quality but very slow)
		'''
	
	def fastControlGI_optionMenu(self, *args):
		if cmds.optionMenu(self.UI.GIType_CB, query = True, ex = 1):
			giPrimary = cmds.getAttr('vraySettings.primaryEngine')
			giSecondary = cmds.getAttr('vraySettings.secondaryEngine')
			giDE = cmds.getAttr('vraySettings.imap_detailEnhancement')
			if giPrimary == 3 and giSecondary == 3:
				cmds.optionMenu(self.UI.GIType_CB, edit = True, select = 1)
			elif giPrimary == 0 and giSecondary == 3 and giDE == False:
				cmds.optionMenu(self.UI.GIType_CB, edit = True, select = 2)
			elif giPrimary == 0 and giSecondary == 3 and giDE == True:
				cmds.optionMenu(self.UI.GIType_CB, edit = True, select = 3)
			elif giPrimary == 0 and giSecondary == 2 and giDE == False:
				cmds.optionMenu(self.UI.GIType_CB, edit = True, select = 4)
			elif giPrimary == 0 and giSecondary == 2 and giDE == True:
				cmds.optionMenu(self.UI.GIType_CB, edit = True, select = 5)
			elif giPrimary == 2 and giSecondary == 2:
				cmds.optionMenu(self.UI.GIType_CB, edit = True, select = 6)
			else:
				cmds.optionMenu(self.UI.GIType_CB, edit = True, select = 7)
				
	def fastControlGI(self, *args):
		#GI
		if cmds.getAttr( 'vraySettings.giOn' ):
			cmds.optionMenu( self.UI.GIType_CB, edit = True, enable= True )
			cmds.attrControlGrp(self.fastControlAOCheckBox, edit = True, enable= True )
			self.fastControlGI_optionMenu()
		else:
			cmds.optionMenu( self.UI.GIType_CB, edit = True, enable= False )
			cmds.attrControlGrp(self.fastControlAOCheckBox, edit = True, enable= False )
		#self.fastControlInit()
		#self.refresh()
	
	'''
	def fastControlAO(self, *args):
		#Ambient occlusion
		if cmds.checkBox( 'AO_CB', query = True, value= True ):
			cmds.setAttr('vraySettings.aoOn', True)
		else:
			cmds.setAttr('vraySettings.aoOn', False)
		self.refresh()
			
	def fastControldisplacement(self, *args):
		#Displacement
		if cmds.checkBox( 'displacement_CB', query = True, value= True ):
			cmds.setAttr('vraySettings.globopt_geom_displacement', True)
		else:
			cmds.setAttr('vraySettings.globopt_geom_displacement', False)
		self.refresh()
	
	def fastControlreflectionrefraction(self, *args):
		#Reflection Refraction
		if cmds.checkBox( 'reflectionrefraction_CB', query = True, value= True ):
			cmds.setAttr('vraySettings.globopt_mtl_reflectionRefraction', True)
		else:
			cmds.setAttr('vraySettings.globopt_mtl_reflectionRefraction', False)
		self.refresh()
			
	def fastControlmaps(self, *args):
		#Maps
		if cmds.checkBox( 'maps_CB', query = True, value= True ):
			cmds.setAttr('vraySettings.globopt_mtl_doMaps', True)
		else:
			cmds.setAttr('vraySettings.globopt_mtl_doMaps', False)
		self.refresh()
	
	def fastControlglossyEffects(self, *args):
		#Glossy Maps
		if cmds.checkBox( 'glossyEffects_CB', query = True, value= True ):
			cmds.setAttr('vraySettings.globopt_mtl_glossy', True)
		else:
			cmds.setAttr('vraySettings.globopt_mtl_glossy', False)
		self.refresh()
			
	def fastControlshadows(self, *args):
		#Shadows
		if cmds.checkBox( 'shadows_CB', query = True, value= True ):
			cmds.setAttr('vraySettings.globopt_light_doShadows', True)
		else:
			cmds.setAttr('vraySettings.globopt_light_doShadows', False)
		self.refresh()
			
	def fastControlantialiasingFilter(self, *args):
		#Antialiasing filter
		if cmds.checkBox( 'antialiasingFilter_CB', query = True, value= True ):
			cmds.setAttr('vraySettings.aaFilterOn', True)
		else:
			cmds.setAttr('vraySettings.aaFilterOn', False)
		self.refresh()
			
	def fastControloverrideEnvironment(self, *args):
		#Override environment
		if cmds.checkBox( 'overrideEnvironment_CB', query = True, value= True ):
			cmds.setAttr('vraySettings.cam_overrideEnvtex', True)
		else:
			cmds.setAttr('vraySettings.cam_overrideEnvtex', False)
		self.refresh()
			
	def fastControldof(self, *args):
		#DOF
		if cmds.checkBox( 'dof_CB', query = True, value= True ):
			cmds.setAttr('vraySettings.cam_dofOn', True)
		else:
			cmds.setAttr('vraySettings.cam_dofOn', False)
		self.refresh()
			
	def fastControlmotionBlur(self, *args):
		#Motion blur
		if cmds.checkBox( 'motionBlur_CB', query = True, value= True ):
			cmds.setAttr('vraySettings.cam_mbOn', True)
		else:
			cmds.setAttr('vraySettings.cam_mbOn', False)
		self.refresh()
			
	def fastControldistributedRendering(self, *args):
		#Distributed rendering
		if cmds.checkBox( 'distributedRendering_CB', query = True, value= True ):
			cmds.setAttr('vraySettings.sys_distributed_rendering_on', True)
		else:
			cmds.setAttr('vraySettings.sys_distributed_rendering_on', False)
		self.refresh()
	'''
		
	def fastControlColorMapping(self, *args):
		actualValue = cmds.intSlider(self.UI.colorMapping_SD, query = True, value = True)
		#set to reinhard
		if not cmds.getAttr('vraySettings.cmap_type', lock = True):
			cmds.setAttr("vraySettings.cmap_type", 6)
		cmds.setAttr('vraySettings.cmap_brightMult', actualValue/100.0)
		cmds.text('exponential_LB', edit = True, label = 'Exponential : ' + str(100 - actualValue) + '%')
		cmds.text('linear_LB', edit = True, label = 'Linear : ' + str(actualValue) + '%')
		self.refresh()	
		
			
	def changePresetType(self, *args):
		if not self.bashMode:
			value = cmds.optionMenu(self.UI.presetType_CB, query = True, value = True)
			cmds.setAttr('vraySettings.deeXVrayFastLastTypePreset', value, type = 'string')
			self.actualPresetType = value
		else:
			cmds.setAttr('vraySettings.deeXVrayFastLastTypePreset', self.actualPresetType, type = 'string')

		self.presetTypeInit()
		self.refresh()
	
	def changePresetPreComp(self, *args):
		if not self.bashMode:
			value = cmds.optionMenu(self.UI.preCompNuke_CB, query = True, value = True)
			cmds.setAttr('vraySettings.deeXVrayFastLastPresetPreComp', value, type = 'string')
			self.actualPresetPrecomp = value
		else:
			cmds.setAttr('vraySettings.deeXVrayFastLastPresetPreComp', self.actualPresetPrecomp, type = 'string')

		self.preCompInit()
		self.refresh()
	
	#============================================
	#
	# Get image file
	#
	#============================================
	def getImageFiles(self, *args):
		workspaceRoot= cmds.workspace(q = True, rootDirectory = True)
		workspacePaths = cmds.workspace(q = True, rt = True)
		imgPath = ""
		
		for i in range(0, len(workspacePaths)):
			if workspacePaths[i]=="images":
				imgPath=workspacePaths[i+1]
				break

		lastChar= workspaceRoot[-1]
		if lastChar !="/" and lastChar !="\\":
			workspaceRoot= workspaceRoot+"/"
		imagePath = workspaceRoot + imgPath + "/"
		
		imgExt = cmds.getAttr("vraySettings.imageFormatStr")
		if imgExt == "" or imgExt is None:
			imgExt = "png"
			
		imgExt = imgExt.split(" ")[0]
		
		prefix = cmds.getAttr("vraySettings.fileNamePrefix")
		if prefix == "(not set; using filename)" or prefix == "" or prefix is None:
			prefix = mel.eval('getSceneName')
		
		prefix = mel.eval('vrayTransformFilename("'+prefix+'", "persp", "", 0);')
		#imageName = prefix + "." + imgExt;
		#listImages = {}
		separate = True
		if cmds.getAttr("vraySettings.relements_separateFolders" ) == 0:
			separate = False
		finalImageName = [imagePath, prefix, imgExt, separate]
		framePadding = cmds.getAttr("vraySettings.fileNamePadding" )
		if cmds.getAttr("defaultRenderGlobals.animation") == 1:
			finalImageName = [imagePath, prefix, "#"*framePadding + "." + imgExt, separate]
		
		"""
		listImages["master"] = finalImageName
		
		#renderElement
		if cmds.getAttr("vraySettings.relements_enableall") == 1:
			for element in cmds.ls(type = "VRayRenderElement"):
				if cmds.getAttr(element + ".enabled") == 1:
					for myAttr in cmds.listAttr( element, r=True ):
						if "vray_name" in myAttr:
							suffix = cmds.getAttr(element + "." + myAttr)
							if cmds.getAttr("vraySettings.relements_separateFolders" ) == 0:
								finalImageName = imagePath + prefix + "." + suffix + "." + imgExt
								if cmds.getAttr("defaultRenderGlobals.animation") == 1:
									finalImageName = imagePath + prefix + "." + suffix + "." + "#"*framePadding + "." + imgExt
							else:
								finalImageName = imagePath + suffix + "/" + prefix + "." + suffix + "." + imgExt
								if cmds.getAttr("defaultRenderGlobals.animation") == 1:
									finalImageName = imagePath + suffix + "/" + prefix + "." + suffix + "." + "#"*framePadding + "." + imgExt
							listImages[suffix] = finalImageName
		"""
		
		return finalImageName
	
	#============================================
	#
	# Generate renderElements in Maya
	#
	#============================================
	def generateRenderElementsInMaya(self, *args):
		renderElements = self.preCompRenderElements
		renderElementsList = renderElements.split(",")
		channelList = ["lightingChannel", "giChannel", "specularChannel", "reflectChannel", "refractChannel", "backgroundChannel", "selfIllumChannel", "rawLightChannel", "rawGiChannel", "diffuseChannel", "rawReflectionChannel", "reflectionFilterChannel", "rawRefractionChannel", "refractionFilterChannel"]
		for myRenderElement in renderElementsList:
			if renderElementsList.index(myRenderElement) <= len(channelList):
				mel.eval("vrayAddRenderElement "+ channelList[renderElementsList.index(myRenderElement)] +";")
				OpenMaya.MGlobal.displayInfo("[deeXVrayFast] Create " + myRenderElement + " render element.")
	
	#============================================
	#
	# Generate nuke File
	#
	#============================================
	def generateNuke(self, file = None):
		renderElements = self.preCompRenderElements
		renderElementsList = renderElements.split(",")
		finalComp = self.preCompString
		if "deeX_preComp_startFrame" in finalComp:
			finalComp = finalComp.replace("deeX_preComp_startFrame", str(cmds.getAttr("defaultRenderGlobals.startFrame")))
		if "deeX_preComp_endFrame" in finalComp:
			finalComp = finalComp.replace("deeX_preComp_endFrame", str(cmds.getAttr("defaultRenderGlobals.endFrame")))
		if "deeX_preComp_width" in finalComp:
			finalComp = finalComp.replace("deeX_preComp_width", str(cmds.getAttr("vraySettings.width")))
		if "deeX_preComp_height" in finalComp:
			finalComp= finalComp.replace("deeX_preComp_height", str(cmds.getAttr("vraySettings.height")))
		
		imageNames = self.getImageFiles()
		typeElementsList = ["refract", "specular", "reflect", "GI", "lighting", "background", "selfIllum", "diffuse", "rawLight", "rawGI", "rawReflection", "reflectionFilter", "rawRefraction", "refractionFilter"]

		OpenMaya.MGlobal.displayInfo("[deeXVrayFast] Generate Nuke file for render elements :")
		for myRenderElement in renderElementsList:
			masterImage = imageNames[0] + imageNames[1] + "." + imageNames[2]
			if imageNames[3]:
				renderElementImage = imageNames[0] + myRenderElement + "/" + imageNames[1] + "." + myRenderElement + "." + imageNames[2]
			else:	
				renderElementImage = imageNames[0] + imageNames[1] + "." + myRenderElement + "." + imageNames[2]
			
			if "deeX_preComp_imageMaster" in finalComp:
					finalComp = finalComp.replace("deeX_preComp_imageMaster", masterImage)
			if myRenderElement in typeElementsList:
				OpenMaya.MGlobal.displayInfo("        - " + myRenderElement)
				if "deeX_preComp_image" + myRenderElement[:1].capitalize() + myRenderElement[1:] in finalComp:
					finalComp = finalComp.replace("deeX_preComp_image" + myRenderElement[:1].capitalize() + myRenderElement[1:], renderElementImage)
		
		if not file:
			nukeFilter = "*.nk"
			selectedFile = cmds.fileDialog2(fileFilter=nukeFilter, dialogStyle=2, okCaption = "Save" ,fileMode=0, returnFilter= True, caption = "Save nuke file")
		else:
			selectedFile = file
		if selectedFile is None:
			return
		
		if "deeX_preComp_nukeFilePath" in finalComp:
			finalComp = finalComp.replace("deeX_preComp_nukeFilePath", selectedFile[0])

		if selectedFile is not None:
			file = open(selectedFile[0], "w")
			file.write(finalComp)
			file.close()
	
	#============================================
	#
	# Tool : Proxy Multi Importer
	#
	#============================================
	def deexVrayFastProxyMultiImporter(self, files = list()):
		if not files:
			vrmeshFilter = "*.vrmesh"
			selectedFile = cmds.fileDialog2(fileFilter=vrmeshFilter, dialogStyle=2, okCaption = "Load" ,fileMode=4, returnFilter= True, caption = "Vray proxy multi importer")
		else:
			selectedFile = files
		if selectedFile is not None:
			for myFile in selectedFile:
				if myFile != "*.vrmesh":
					fileName = os.path.basename(myFile)
					mel.eval('vrayCreateProxyExisting("'+ fileName +'", "'+ myFile +'")')
	
	#============================================
	#
	# Tool : Proxy Shader auto connect
	#
	#============================================				
	def deexVrayFastProxyShaderAutoConnect(self, *args):
		#select all vray mesh proxy material
		proxyMaterialNodes = cmds.ls(type = "VRayMeshMaterial")
		#select all material
		allMaterials = cmds.ls(materials = True)
		materialClean = list(set(allMaterials) - set(proxyMaterialNodes))
		if len(proxyMaterialNodes) == 0:
			OpenMaya.MGlobal.displayWarning("No VRayMeshMaterial in the scene !")
		#list all connection name on all vray mesh proxy material
		for proxyMaterialNode in proxyMaterialNodes:
			numberOfSlot = cmds.getAttr(proxyMaterialNode + ".shaderNames", size = True)
			for i in range(numberOfSlot):
				nameSlot = cmds.getAttr(proxyMaterialNode + ".shaderNames[" + str(i) + "]")
				#conected or not ?
				if cmds.connectionInfo( proxyMaterialNode + ".shaders[" + str(i) + "]", isDestination=True):
					connected = cmds.connectionInfo( proxyMaterialNode + ".shaders[" + str(i) + "]", sourceFromDestination=True)
					cmds.disconnectAttr(connected, proxyMaterialNode + ".shaders[" + str(i) + "]")
					print "[deeXVrayFast] Disconnect " + proxyMaterialNode + ".shaders[" + str(i) + "]"
				for myMat in materialClean:
					if myMat.split(":")[-1] == nameSlot.split(":")[-1]:
						#try:
						cmds.connectAttr(myMat + ".outColor", proxyMaterialNode + ".shaders[" + str(i) + "]", f = True)
						print "[deeXVrayFast] " + proxyMaterialNode + ".shaders[" + str(i) + "] connected."
						
	#============================================
	#
	# Tool : Textures to Tiled Exr
	#
	#============================================
	def deexVrayFastTextureToTiledExrSelection(self, *args):
		textureFiles1 = cmds.ls(type = "file", sl = True)
		self.deexVrayFastTextureToTiledExr(textureFiles = textureFiles1)
		
	def deexVrayFastTextureToTiledExrAll(self, *args):
		textureFiles1 = cmds.ls(type = "file")
		self.deexVrayFastTextureToTiledExr(textureFiles = textureFiles1)
	
	def deexVrayFastTextureToTiledExr(self, textureFiles = None):
		if self.environVRAY_TOOLS is None:
			OpenMaya.MGlobal.displayError("Variable environment VRAY_TOOLS_MAYA"+ self.mayaVersion +" not found. Check your installation")
			return
			
		if len(textureFiles) == 0 or textureFiles is None:
			OpenMaya.MGlobal.displayError("No file(s) node(s) selected or found.")
			return

		for textureFile in textureFiles:
			fileName = cmds.getAttr(textureFile + ".fileTextureName")
			fileNameExr1 = fileName.split(".")
			fileNameExr1.pop(-1)
			fileNameExr = ".".join(fileNameExr1) + "_tiled.exr"
			doLinear = False
			#get extension
			if fileName.split(".")[-1] != "exr":
				#add attributes to back
				dicoOriginal = {}
				cmds.addAttr(textureFile, ln="deexVrayFastOriginalFileTextureName" , dt = "string")
				originalTextureGammaEnable = None
				originalColorSpace = None
				originalVrayFileGammaValue = None
				textureGammaEnable = None
				textureGammaMode = None
				#remove linear correction because texture are also linear in exr
				if cmds.attributeQuery( 'vrayFileGammaEnable', node=textureFile, ex=True ):
					originalVrayFileGammaValue = cmds.getAttr(textureFile + ".vrayFileGammaValue")
					if cmds.getAttr(textureFile + ".vrayFileGammaEnable") == 1:#have corrected texture
						originalTextureGammaEnable = 1
						if cmds.getAttr(textureFile + ".vrayFileColorSpace") == 2:#was in srgb, so desactivate
							textureGammaEnable = 0
							originalColorSpace = 2
						elif cmds.getAttr(textureFile + ".vrayFileColorSpace") == 0:#was in linear, so color to srgb
							doLinear = True
							textureGammaEnable = 0
							originalColorSpace = 0
						else:#? disable correction
							textureGammaEnable = 0
							originalColorSpace = 1
						print "[deeXVrayFast] Color space disabled."
					else:#have no correction but attribut, so texture to no linear
						originalTextureGammaEnable = 0
						doLinear = True
						textureGammaEnable = 0
				else:#have not correction and no attribut, so correct it to linear
					#mel.eval('evalDeferred "vray addAttributesFromGroup '+ textureFile +' vray_file_gamma 1;"')
					doLinear = True
					
				if textureGammaEnable is not None:
					mel.eval('evalDeferred "setAttr '+textureFile  + '.vrayFileGammaEnable ' + str(textureGammaEnable) + ';"')
					
					if textureGammaMode is not None:
						mel.eval('evalDeferred "setAttr '+textureFile  + '.vrayFileColorSpace ' + str(textureGammaMode) + ';"')
				if not os.path.isfile(fileNameExr):
					print "[deeXVrayFast] Start to convert : " + fileName + " to exr linear."
					#builds command line
					if self.osSystemType == "nt" or self.osSystemType == "win64" or self.osSystemType == "mac":#this is windows
						command = self.environVRAY_TOOLS + "/img2tiledexr.exe "
					elif self.osSystemType == "linux" or self.osSystemType == "linux64":#this is linux
						command = self.environVRAY_TOOLS + "/./img2tiledexr.exe "
					else:#??? ?
						OpenMaya.MGlobal.displayError("What is your system ?")
						return
					#os.system(command)
					if doLinear:
						subprocess.call ([command, fileName, "-linear", "off"])
						print "[deeXVrayFast] Executed command : " + command + fileName + " -linear off"
					else:
						subprocess.call ([command, fileName])
						print "[deeXVrayFast] Executed command : " + command + fileName
					print "[deeXVrayFast] Conversion finished."
				else:
					print '[deeXVrayFast] ' + fileNameExr + " exist. No convertion."
				#set attr
				cmds.setAttr(textureFile + ".fileTextureName", fileNameExr, type = "string")
				#set original attr
				if textureGammaEnable is None:#not correction
					dicoOriginal[fileName] = None
				else:
					dicoOriginal[fileName] = [originalTextureGammaEnable, originalColorSpace, originalVrayFileGammaValue]
				cmds.setAttr(textureFile + ".deexVrayFastOriginalFileTextureName", dicoOriginal, type="string")
				cmds.setAttr( textureFile + ".deexVrayFastOriginalFileTextureName", lock=True )
				print '[deeXVrayFast] ' + textureFile + " switched to : " + fileNameExr
				print "==================================="
	
	#============================================
	#
	# Tool : Textures to Tiled Exr back
	#
	#============================================
	def deexVrayFastTextureToTiledExrBackSelection(self, *args):
		textureFiles1 = cmds.ls(type = "file", sl = True)
		self.deexVrayFastTextureToTiledExrBack(textureFiles = textureFiles1)
		
	def deexVrayFastTextureToTiledExrBackAll(self, *args):
		textureFiles1 = cmds.ls(type = "file")
		self.deexVrayFastTextureToTiledExrBack(textureFiles = textureFiles1)
	
	def deexVrayFastTextureToTiledExrBack(self, textureFiles = None):
		if len(textureFiles) == 0 or textureFiles is None:
			OpenMaya.MGlobal.displayError("No file(s) node(s) selected or found.")
			return
		for textureFile in textureFiles:
			if cmds.attributeQuery( 'deexVrayFastOriginalFileTextureName', n= textureFile, ex=True ):
				#get original value
				originalValue = cmds.getAttr(textureFile + ".deexVrayFastOriginalFileTextureName")
				dico = eval(originalValue)
				for myFileName in dico:
					#set attr
					cmds.setAttr(textureFile + ".fileTextureName", myFileName, type = "string")
					if dico[myFileName] is not None:
						if dico[myFileName][0] is not None:
							cmds.setAttr(textureFile + ".vrayFileGammaEnable", dico[myFileName][0])
						if dico[myFileName][1] is not None:
							cmds.setAttr(textureFile + ".vrayFileColorSpace", dico[myFileName][1])
						if dico[myFileName][2] is not None:
							cmds.setAttr(textureFile + ".vrayFileGammaValue", dico[myFileName][2])
					#delete attributed
					cmds.setAttr( textureFile + ".deexVrayFastOriginalFileTextureName", lock=False )
					cmds.deleteAttr( textureFile + '.deexVrayFastOriginalFileTextureName' )
	
	#============================================
	#
	# Tool : Material ID add
	#
	#============================================
	def deexVrayFastMaterialIDaddSelection(self, *args):
		selections = cmds.ls(materials = True, type = "shadingEngine", sl = True)
		self.deexVrayFastMaterialIDadd(selection = selections)
		
	def deexVrayFastMaterialIDaddAllMat(self, *args):
		selections = cmds.ls(materials = True)
		self.deexVrayFastMaterialIDadd(selection = selections)
	
	def deexVrayFastMaterialIDaddAllSG(self, *args):
		selections = cmds.ls(type = "shadingEngine")
		self.deexVrayFastMaterialIDadd(selection = selections)
	
	def deexVrayFastMaterialIDadd(self, selection = None):
		if len(selection) == 0 or selection is None:
			OpenMaya.MGlobal.displayError("No material(s) node(s) or shading(s) engine node(s) selected or found.")
			return
		for mySelect in selection:
			#exclude custom material
			if cmds.objectType( mySelect ) in self.materialIDexcludeType:
				print "[deeXVrayFast] " + mySelect + " must not have materialID."
				continue
			
			mel.eval('vray addAttributesFromGroup '+ mySelect +' vray_material_id 1;')
			print "[deeXVrayFast] Add material ID attributes to " + mySelect
		
	#============================================
	#
	# Tool : Material ID set
	#
	#============================================
	def deexVrayFastMaterialIDsetSelection(self, *args):
		selections = cmds.ls(materials = True, type = "shadingEngine", sl = True)
		self.deexVrayFastMaterialIDset(selection = selections)
		
	def deexVrayFastMaterialIDsetAllMat(self, *args):
		selections = cmds.ls(materials = True)
		self.deexVrayFastMaterialIDset(selection = selections)
	
	def deexVrayFastMaterialIDsetAllSG(self, *args):
		selections = cmds.ls(type = "shadingEngine")
		self.deexVrayFastMaterialIDset(selection = selections)
	
	def deexVrayFastMaterialIDset(self, selection = None):
		if len(selection) == 0 or selection is None:
			OpenMaya.MGlobal.displayError("No material(s) node(s) or shading(s) engine node(s) selected or found.")
			return
		for mySelect in selection:
			#exclude custom material
			if cmds.objectType( mySelect ) in self.materialIDexcludeType:
				print "[deeXVrayFast] " + mySelect + " must not have materialID."
				continue
			
			#check if the attribute exist
			if not cmds.attributeQuery( 'vrayColorId', n= mySelect, ex=True ):
				print "[deeXVrayFast] Material ID attributes of " + mySelect + " doen't exist."
				continue
			
			#check if we have a name space
			if ":" in selection:
				striped = mySelect.split(":")[-1]
			else:
				striped = mySelect

			#generate a unique color based of a md5 of the selection
			strToMd5 = hashlib.md5(striped).hexdigest()
			finalNum = 0
			for letter in strToMd5:
				if letter.isdigit():
					finalNum += int(letter)
				else:
					finalNum += ord(letter)

			multimatteID = mel.eval('seed(' + str(finalNum) + ');')
			
			myVector = mel.eval('sphrand(1);')
			
			rCol = float(abs(myVector[0]))
			gCol = float(abs(myVector[1]))
			bCol = float(abs(myVector[2]))
			
			#set attributes
			cmds.setAttr (mySelect + ".vrayColorId", rCol, gCol, bCol, type = "double3")
			cmds.setAttr (mySelect + ".vrayMaterialId", multimatteID)
			
			print "[deeXVrayFast] Material ID attributes of " + mySelect + " setted."
	
	#============================================
	#
	# Tool : Material ID delete
	#
	#============================================
	def deexVrayFastMaterialIDdeleteSelection(self, *args):
		selections = cmds.ls(materials = True, type = "shadingEngine", sl = True)
		self.deexVrayFastMaterialIDdelete(selection = selections)
		
	def deexVrayFastMaterialIDdeleteAllMat(self, *args):
		selections = cmds.ls(materials = True)
		self.deexVrayFastMaterialIDdelete(selection = selections)
	
	def deexVrayFastMaterialIDdeleteAllSG(self, *args):
		selections = cmds.ls(type = "shadingEngine")
		self.deexVrayFastMaterialIDdelete(selection = selections)
	
	def deexVrayFastMaterialIDdelete(self, selection = None):
		if len(selection) == 0 or selection is None:
			OpenMaya.MGlobal.displayError("No material(s) node(s) or shading(s) engine node(s) selected or found.")
			return
		for mySelect in selection:
			#exclude custom material
			if cmds.objectType( mySelect ) in self.materialIDexcludeType:
				print "[deeXVrayFast] " + mySelect + " must not have materialID."
				continue
			
			#check if the attribute exist
			if not cmds.attributeQuery( 'vrayColorId', n= mySelect, ex=True ):
				print "[deeXVrayFast] Material ID attributes of " + mySelect + " doen't exist."
				continue
			
			mel.eval('vray addAttributesFromGroup '+ mySelect +' vray_material_id 0;')
			print "[deeXVrayFast] Remove material ID attributes to " + mySelect

	#============================================
	#
	# Tool : Object ID add
	#
	#============================================
	def deexVrayFastObjectIDaddSelection(self, *args):
		selections = cmds.ls(type = "mesh", sl = True)
		self.deexVrayFastObjectIDaddAll(selection = selections)
		
	def deexVrayFastObjectIDaddAllMeshs(self, *args):
		selections = cmds.ls(type = "mesh")
		self.deexVrayFastObjectIDaddAll(selection = selections)
	
	def deexVrayFastObjectIDaddAll(self, selection = None):
		if len(selection) == 0 or selection is None:
			OpenMaya.MGlobal.displayError("No mesh(s) selected or found.")
			return
		for mySelect in selection:
			mel.eval('vray addAttributesFromGroup '+ mySelect +' vray_objectID 1;')
			print "[deeXVrayFast] Add object ID attributes to " + mySelect
	
	#============================================
	#
	# Tool : Object ID set
	#
	#============================================
	def deexVrayFastObjectIDsetSelection(self, *args):
		selections = cmds.ls(type = "mesh", sl = True)
		self.deexVrayFastObjectIDset(selection = selections)
		
	def deexVrayFastObjectIDsetAllMeshs(self, *args):
		selections = cmds.ls(type = "mesh")
		self.deexVrayFastObjectIDset(selection = selections)
	
	def deexVrayFastObjectIDset(self, selection = None):
		if len(selection) == 0 or selection is None:
			OpenMaya.MGlobal.displayError("No mesh(s) selected or found.")
			return
		for mySelect in selection:
			#check if the attribute exist
			if not cmds.attributeQuery( 'vrayObjectID', n= mySelect, ex=True ):
				print "[deeXVrayFast] Object ID attributes of " + mySelect + " doen't exist."
				continue
			
			#check if we have a name space
			if ":" in selection:
				striped = mySelect.split(":")[-1]
			else:
				striped = mySelect

			#generate a unique color based of a md5 of the selection
			strToMd5 = hashlib.md5(striped).hexdigest()
			finalNum = 0
			for letter in strToMd5:
				if letter.isdigit():
					finalNum += int(letter)
				else:
					finalNum += ord(letter)

			objectID = mel.eval('seed(' + str(finalNum) + ');')
			
			cmds.setAttr (mySelect + ".vrayObjectID", objectID)
			
			print "[deeXVrayFast] Object ID attributes of " + mySelect + " setted."

	#============================================
	#
	# Tool : Object ID delete
	#
	#============================================
	def deexVrayFastObjectIDremoveSelection(self, *args):
		selections = cmds.ls(type = "mesh", sl = True)
		self.deexVrayFastObjectIDremove(selection = selections)
		
	def deexVrayFastObjectIDremoveAllMeshs(self, *args):
		selections = cmds.ls(type = "mesh")
		self.deexVrayFastObjectIDremove(selection = selections)
	
	def deexVrayFastObjectIDremove(self, selection = None):
		if len(selection) == 0 or selection is None:
			OpenMaya.MGlobal.displayError("No mesh(s) selected or found.")
			return
		for mySelect in selection:
			#check if the attribute exist
			if not cmds.attributeQuery( 'vrayObjectID', n= mySelect, ex=True ):
				print "[deeXVrayFast] Object ID attributes of " + mySelect + " doen't exist."
				continue
			
			mel.eval('vray addAttributesFromGroup '+ mySelect +' vray_objectID 0;')
			print "[deeXVrayFast] Remove object ID attributes to " + mySelect

	#============================================
	#
	# Automatic update
	#
	#============================================
	def deexVrayFastAutoUpdate(self, *args):
		now = datetime.date.today()
		now2 = datetime.datetime.now()
		nowString = str(now.year) + "," + str(now.month) + "," +  str(now.day)
		doUpdate = False
		#look for the environement variable
		if "DEEX_VRAY_FAST_LASTUPDATE_DATE" in os.environ:
			lastUpdate = os.environ["DEEX_VRAY_FAST_LASTUPDATE_DATE"]
			lastDatetime = datetime.datetime( int(lastUpdate.split(",")[0]), int(lastUpdate.split(",")[1]), int(lastUpdate.split(",")[2]) )
			diff = now2 - lastDatetime
			#get thedifference
			OpenMaya.MGlobal.displayInfo("[deeXVrayFast] Your last update was at "+ lastUpdate +".")
			if diff.days >= 15:
				OpenMaya.MGlobal.displayInfo("[deeXVrayFast] You doesn't update since "+ str(diff.days) +" days.")
				doUpdate = True		
		else:
			#force to check update
			doUpdate = True
		
		if doUpdate:
			if self.deexVrayFastUpdate():
				os.environ["DEEX_VRAY_FAST_LASTUPDATE_DATE"] = nowString

	#============================================
	#
	# Update the script
	#
	#============================================
	def deexVrayFastUpdate(self, *args):
		startUpdate = deexVrayFastUpdater(self)
		if startUpdate.update():
			return True
		else:
			return False
		
	#============================================
	#
	# Calcule age
	#
	#============================================
	def calculateAge(self, born):
		"""Calculate the age of a user."""
		j = int(born.split(",")[0])
		m = int(born.split(",")[1])
		a = int(born.split(",")[2])
		today = datetime.date.today()
		birthday = datetime.date(a, m, j)

		if today.month < birthday.month:
			return str(today.year - a - 1) + " years old"
		elif today.month == birthday.month:
			if today.day > birthday.day:
				return str(today.year - a - 1) + " years old"
			elif today.day == birthday.day:
				return str(today.year - a - 1) + " years old.\nIt is my birthday today !\nSay happy birthday Damien"
			else:
				return str(today.year - a) + " years old"
		else:
			return str(today.year - a) + " years old"
	
	#============================================
	#
	# About
	#
	#============================================
	def deexVrayFastAbout(self, *args):
		myAge = self.calculateAge("26,9,1986")
		aboutMessage = "Deex Vray Fast was created by Damien Bataille, alias DeeX.\n"
		aboutMessage += "This tool is Free and can be found on www.deex.info\n"
		aboutMessage += "If you like this tool, don't hesitate to say thank and encourage me by email.\n"
		aboutMessage += "I am a french lighting TD and lookDev TD, " + myAge + ".\n"
		aboutMessage += "I will look for a job in VFX in Canada or USA in 2012.\n"
		aboutMessage += "If you are interested to work with me, contact me.\n"
		aboutMessage += "Deex"
		cmds.confirmDialog( title='About', message=aboutMessage, button=['Close'], defaultButton='Close', cancelButton='Close', dismissString='Close' )

	
	#============================================
	#
	# Load Vray Plugin
	#
	#============================================
	def loadVray(self, *args):
		cmds.loadPlugin( 'vrayformaya.mll', quiet = True )
		cmds.setAttr ('defaultRenderGlobals.currentRenderer', "vray", type = "string" )
		mel.eval('vrayCreateVRaySettingsNode();')
	
	#============================================
	#
	# Create windows
	#
	#============================================
	def deexVrayFastCreateUI(self, *args):
		if cmds.dockControl('deeXVrayFastDock', q = True, ex = True):
			cmds.deleteUI ("deeXVrayFastDock", control=True)
		if cmds.window ("deexVrayFast", exists = True):
			cmds.deleteUI ("deexVrayFast", window=True)
		if self.UI is None:
			self.UI = deeXVrayFastUi(self)
		return self.UI

class deeXVrayFastUtils(object):
	"""Documentation for a class.

    More details.
    """
	def __init__(self):
		"""The constructor."""
		self.tool = deeXVrayFastTool(bashMode = True)
		if self.tool.initialize() is True:
			print "[deeXVrayFast] deeXVrayFast initialized."
		else:
			OpenMaya.MGlobal.displayError("[deeXVrayFast] vraySettings not found!")
			del self.__class__.__name__
		
	def __del__(self):
		class_name = self.__class__.__name__
		print class_name, "destroyed"
	
	def setQuality(self, quality = None, preset = None):
		"""Set the quality of your scene.
		
		quality is the quality number between 1 and 99.
		
		preset is the preset that you want to use, like 'deeX_interior'.
		
		If you do not set a preset, 'deeX_interior' prest will be used.
		
		Example code :
		
		\code
		import deeXVrayFast
		myTool = deeXVrayFast.deeXVrayFastUtils()
		myTool.setQuality(quality = 10, preset = 'deeX_exterior')
		\endcode
		"""
		if quality is not None:
			if preset is None:
				self.tool.actualPresetType = 'deeX_interior'
			else:
				self.tool.actualPresetType = preset
			self.tool.changePresetType()
			self.tool.optimize(valueQuality = quality)
		else:
			OpenMaya.MGlobal.displayError("[deeXVrayFast] Please set a quality")
			
	def saveSettings(self):
		"""Save current settings of your scene.
		
		Example code :
		
		\code
		import deeXVrayFast
		myTool = deeXVrayFast.deeXVrayFastUtils()
		myTool.saveSettings()
		\endcode
		"""
		self.tool.saveSetting()
		
	def backSettings(self):
		"""Reverse settings of your scene.
		
		Example code :
		
		\code
		import deeXVrayFast
		myTool = deeXVrayFast.deeXVrayFastUtils()
		myTool.backSettings()
		\endcode
		"""
		self.tool.backSetting()
		
	def proxyMultiImporter(self, files = list()):
		"""Proxy multi-importer.
		
		Import multiple proxy in GUI mode or batch mode.
		
		For batch mode, you must add a list of files.
		
		Example code :
		
		\code
		import deeXVrayFast
		myTool = deeXVrayFast.deeXVrayFastUtils()
		myTool.proxyMultiImporter(["C:/path/my.vrmesh"])
		\endcode
		"""
		self.tool.deexVrayFastProxyMultiImporter(files = files)
		
	def proxyShaderAutoConnect(self):
		"""Proxy shaderAutoConnect.
		
		Connect all shaders on all proxis materials.
		
		Example code :
		
		\code
		import deeXVrayFast
		myTool = deeXVrayFast.deeXVrayFastUtils()
		myTool.proxyShaderAutoConnect()
		\endcode
		"""
		self.tool.deexVrayFastProxyShaderAutoConnect()
	
	def textureToTiledExr(self, files = list()):
		"""Convert list textures into tiled exr.

		Example code :
		
		\code
		import deeXVrayFast
		myTool = deeXVrayFast.deeXVrayFastUtils()
		myTool.deexVrayFastTextureToTiledExr(textureFiles = ["file1", "file2"])
		\endcode
		"""
		if files:
			self.tool.deexVrayFastTextureToTiledExr(textureFiles = files)
		else:
			OpenMaya.MGlobal.displayError("[deeXVrayFast] You must to add a list files")
		
	def textureToTiledExrBack(self, files = list()):
		"""Resert list files texture node.

		Example code :
		
		\code
		import deeXVrayFast
		myTool = deeXVrayFast.deeXVrayFastUtils()
		myTool.deexVrayFastTextureToTiledExrBack(textureFiles = ["file1", "file2"])
		\endcode
		"""
		self.tool.deexVrayFastTextureToTiledExrBack(textureFiles = files)
	
	def materialIDadd(self, files = list()):
		"""Add material ID to materials or SG.

		Example code :
		
		\code
		import deeXVrayFast
		myTool = deeXVrayFast.deeXVrayFastUtils()
		myTool.deexVrayFastMaterialIDadd(selection = ["material1", "sg1"])
		\endcode
		"""
		self.tool.deexVrayFastMaterialIDadd(selection = files)
		
	def materialIDset(self, files = list()):
		"""Set material ID of materials or SG based of the name.

		Example code :
		
		\code
		import deeXVrayFast
		myTool = deeXVrayFast.deeXVrayFastUtils()
		myTool.deexVrayFastMaterialIDset(selection = ["material1", "sg1"])
		\endcode
		"""
		self.tool.deexVrayFastMaterialIDset(selection = files)
		
	def materialIDdelete(self, files = list()):
		"""Remove material ID of materials or SG based of the name.

		Example code :
		
		\code
		import deeXVrayFast
		myTool = deeXVrayFast.deeXVrayFastUtils()
		myTool.deexVrayFastMaterialIDdelete(selection = ["material1", "sg1"])
		\endcode
		"""
		self.tool.deexVrayFastMaterialIDdelete(selection = files)

	def objectIDadd(self, files = list()):
		"""Add object ID to mesh or transform.

		Example code :
		
		\code
		import deeXVrayFast
		myTool = deeXVrayFast.deeXVrayFastUtils()
		myTool.deexVrayFastObjectIDadd(selection = ["pSphere1_vrmesh", "pSphere1_vrmeshShape"])
		\endcode
		"""
		self.tool.deexVrayFastObjectIDaddAll(selection = files)
		
	def objectIDset(self, files = list()):
		"""Set object ID to mesh or transform.

		Example code :
		
		\code
		import deeXVrayFast
		myTool = deeXVrayFast.deeXVrayFastUtils()
		myTool.deexVrayFastObjectIDset(selection = ["pSphere1_vrmesh", "pSphere1_vrmeshShape"])
		\endcode
		"""
		self.tool.deexVrayFastObjectIDset(selection = files)
		
	def objectIDremove(self, files = list()):
		"""Remove object ID to mesh or transform.

		Example code :
		
		\code
		import deeXVrayFast
		myTool = deeXVrayFast.deeXVrayFastUtils()
		myTool.deexVrayFastObjectIDremove(selection = ["pSphere1_vrmesh", "pSphere1_vrmeshShape"])
		\endcode
		"""
		self.tool.deexVrayFastObjectIDremove(selection = files)

"""
def deeXVrayFastUtils(quality = None, preset = None, saveSettings = False, backSettings = False):
	#if cmds.dockControl('deeXVrayFastDock', q = True, ex = True):
	#	cmds.deleteUI ("deeXVrayFastDock", control=True)
	#if cmds.window ("deexVrayFast", exists = True):
	#	cmds.deleteUI ("deexVrayFast", window=True)
	object = deeXVrayFast(bashMode = True)
	if object.initialize() is True:
		if saveSettings:
			object.saveSetting()
		if quality is not None:
			if preset is None:
				object.actualPresetType = 'deeX_interior'
			else:
				object.actualPresetType = preset
			object.changePresetType()
			object.optimize(valueQuality = quality)
		if backSettings:
			object.backSetting()
	else:
		OpenMaya.MGlobal.displayError("[deeXVrayFast] vraySettings not found!")
"""
		
def deeXVrayFastUI():
	tool = deeXVrayFastTool()
	tool.deexVrayFastAutoUpdate()
	windows = tool.deexVrayFastCreateUI()
	if tool.initialize() is True:
		cmds.showWindow(windows.ui)
		#position
		mayaWindSize = cmds.window('MayaWindow', query = True, widthHeight = True )
		mayaWindPos = cmds.window('MayaWindow', query = True, topLeftCorner = True )
		w = mayaWindSize[1]/2 + mayaWindPos[0] - (cmds.window(windows.ui, query = True, width = True )/2)
		h = mayaWindSize[0]/2 + mayaWindPos[1] - (cmds.window(windows.ui, query = True, height = True )/2)
		cmds.window (windows.ui, edit = True, topLeftCorner = [w, h],width = windows.width, height = windows.height, title = 'Deex Vray Fast v' + str(tool.version))
		#print cmds.window ("deexVrayFast", query = True, height = True)
		
		#cmds.dockControl( windows.ui, area='left', content=windows.ui, allowedArea=['right', 'left'])
		
	else:
		OpenMaya.MGlobal.displayError("[deeXVrayFast] vraySettings not found!")