import pymel.core as pm
import json

data = {}
with open('C:/copyKey.txt') as outfile:
    data = json.load(outfile)
outfile.close()

for infoGrp in data.values():
    for info in infoGrp:
        target = info[0].replace(':assassin_', ':')
        animCv = info[1]
        try:
            conn = pm.listConnections(target, c= 1, p= 1, t= 'animCurve')
            if conn:
                for c in conn:
                    try:
                        cmds.disconnectAttr(str(c[1]), str(c[0]))
                    except:
                        pass
            cmds.connectAttr(animCv, target)
            #print 'yeah'
        except:
            #print 'error'
            pass