import os
import maya.cmds as cmds
import maya.mel as mel
import xgenm as xg
import xgenm.xgGlobal as xgg

import sys
sys.path.append('//storage-server/LaiTaWei/script/MS_MayaOil')
import moCache.moGeoCache as moGeoCache
reload(moGeoCache)

import logging
logger = logging.getLogger('MayaOil')
logger.setLevel(logging.DEBUG)
logger.info('start')

# vars
geoCollection = {	'hair_geo':'O:/201603_SongOfKnights/Maya/assets/char/assassin_xGen_master__hairCollection.xgen',
					'brow_geo':'O:/201603_SongOfKnights/Maya/assets/char/assassin_xGen_master__brow.xgen',
					 'lid_geo':'O:/201603_SongOfKnights/Maya/assets/char/assassin_xGen_master__lashCollection.xgen'
				}

hairColl = 'hairCollection'

hairCacheDisc = ['hairA3', 'hairA4', 'hairA5']

hairSimRoot = 'O:/201603_SongOfKnights/Maya/scenes/nHairSim/'

cutId = 'c' + os.path.basename(cmds.file(q= 1, exn= 1)).split('_')[1][-2:]



if not cmds.objExists('hair_grp'):
	# reference geo
	cmds.file('O:/201603_SongOfKnights/Maya/assets/char/assassin_xGen_geoHolder_master.ma', r= 1, typ= 'mayaAscii',  iv= 1, mnc= 1, ns= ':')


	# import geoCache
	cmds.select(cl= 1)
	for geo in geoCollection.keys():
		cmds.select(cmds.ls('*' + geo, r= 1)[0], add= 1)
	moGeoCache.importGeoCache('assassin_' + cutId + '_geoCache_v01', 1, 'assassin')


# import collections
for geo in geoCollection.keys():
	cmds.select(cmds.ls('*' + geo, r= 1)[0], r= 1)
	cmds.setAttr(cmds.ls(sl= 1)[0] + '.v', 0)
	xg.importPalette( geoCollection[geo], [], '' )


# get abc
for disc in hairCacheDisc:
	xg.setAttr( 'cacheFileName', str(hairSimRoot + cutId + '/' + disc + '.abc'), hairColl, disc, 'SplinePrimitive')
	xg.setAttr( 'useCache', 'true', hairColl, disc, 'SplinePrimitive')
	xg.setAttr( 'liveMode', 'false', hairColl, disc, 'SplinePrimitive')

# set renderer
for collection in xg.palettes():
	for disc in xg.descriptions(collection):
		xg.setAttr( 'renderer', 'VRay', collection, disc, 'RendermanRenderer')

# update ui
de = xgg.DescriptionEditor 
de.refresh('Full')

# assign shader
hairGrp = ['hairA3', 'hairA4', 'hairA5', 'hairA6', 'hairA14']
browlashGrp = ['assassin1', 'assassin2', 'lash1', 'lash2', 'lash3', 'lashBottom1']

cmds.select(hairGrp, r= 1)
cmds.hyperShade(a= 'VRayHair_HairRed')

cmds.select(browlashGrp, r= 1)
cmds.hyperShade(a= 'VRayHair_browLid')

'''
note
'''
#xg.getAttr( 'useCache','hairCollection', 'hairA3', 'SplinePrimitive' )
#xg.attrs( 'hairCollection', 'hairA3', 'SplinePrimitive' )
#xg.objects( 'hairCollection', 'hairA3', True )