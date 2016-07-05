n = nuke.thisNode()
k = nuke.thisKnob()


if 'position' in k.name():

    posX = n['position'].value(0)
    posY = n['position'].value(1)
    n.begin()
    idShuffle = nuke.toNode('idShuffle')
    sample = nuke.sample(idShuffle,'g', posX, posY)
    n.end()
   
    n['colorID'].setValue(int(sample))
    n['colIDexp'].setValue(int(sample))
    
    if n['reset_on_move'].value()==True:
        n['rangemin'].setValue(0)
        n['rangemax'].setValue(0)
        
if 'colorID' in k.name():
    n['colIDexp'].setValue(n['colorID'].value())
    if n['reset_on_move'].value()==True:
        n['rangemin'].setValue(0)
        n['rangemax'].setValue(0)




