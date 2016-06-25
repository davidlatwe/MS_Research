import pymel.core as pm
import json

data = {}
dagList = pm.ls(sl= 1)
for dag in dagList:
    connectInfo = pm.listConnections(dag, c= 1, p= 1, t= 'animCurve')
    if connectInfo:
        infoConvertGrp = []
        for info in connectInfo:
            infoConvert = []
            for i in info:
                infoConvert.append(str(i))
            infoConvertGrp.append(infoConvert)
        data[len(data)] = infoConvertGrp


with open('C:/copyKey.txt', 'w') as outfile:
    json.dump(data, outfile)

outfile.close()