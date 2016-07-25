import sys
import os

tSrc = 'devPath'

toolPaths = {
	'pubPath' : 'T:/Script/Maya/tools/Hub',
	'devPath' : 'C:/Users/David/Documents/GitHub/MS_MayaHub'	
	}

sysPath = sys.path
for i, sp in enumerate(sysPath):
	sysPath[i] = str(os.path.abspath(sp))
sysPath = list(set(sysPath))
for tpv in toolPaths.values():
	tpv = os.path.abspath(tpv)
	if tpv in sysPath:
		sysPath.remove(tpv)

sysPath.insert(0, os.path.abspath(toolPaths[tSrc]))
sys.path = sysPath

import moCache; reload(moCache)
import moCache.moGeoCacheUI as moGeoCacheUI; reload(moGeoCacheUI)
moGeoCacheUI.ui_main()
