import pymel.core as pm
[nuc.enable.set(0) for nuc in pm.ls(typ= 'nucleus')]
[ncl.isDynamic.set(0) for ncl in pm.ls(typ= 'nCloth')]
[nrg.isDynamic.set(0) for nrg in pm.ls(typ= 'nRigid')]
[ndc.enable.set(0) for ndc in pm.ls(typ= 'dynamicConstraint')]
[nhr.simulationMethod.set(0) for nhr in pm.ls(typ= 'hairSystem')]
[nhr.active.set(0) for nhr in pm.ls(typ= 'hairSystem')]