import time
start = time.time()


pos = nuke.toNode('Position1')
cordX = pos.knob('translate').x()
cordY = pos.knob('translate').y()

bd = nuke.toNode('BackdropNode1')
bdChilds = bd.getNodes()


for read in bdChilds:
    red = round(nuke.sample(read, 'red', cordX, cordY))
    if red:
        read.setSelected(True)
    else:
        read.setSelected(False)


end = time.time()
print(end - start)