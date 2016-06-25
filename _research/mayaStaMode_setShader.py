# set shader in standalone mode
# In Maya Standalone, you can't use "hyperShade" cmd

cmds.shadingNode('VRayMtl', asShader= 1)
cmds.sets(renderable=True, noSurfaceShader= True, empty= 1, name= 'VRayMtl1SG')
cmds.connectAttr('VRayMtl1.outColor' ,'VRayMtl1SG.surfaceShader')
cmds.select('pCube1', r= 1)
cmds.sets(e= 1,fe= 'VRayMtl1SG')

