from PySide.QtCore import *
from PySide.QtGui import *
from shiboken import wrapInstance
from ui.arsenal_ui import Ui_arsenal_main
from ui.arsenal_multimatteMask_ui import Ui_arsenal_multimatteMask
from arsenal import Arsenal
from arsenalQuality import ArsenalQualityTool
import arsenalToolBox
import os
import functools
import imp
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as mui
import pymel.all as pm
pm.optionVar['arsenal_UI'] = False

class OverrideCustomMenu(QMenu):

    def __init__(self, parent = None, widget = None, pos = None, always = None, menuType = None):
        super(OverrideCustomMenu, self).__init__(parent)
        self.parent = parent
        self.widget = widget
        self.pos = pos
        self.always = always
        if menuType == 'fastOverride':
            if self.always:
                self.addAction(QIcon(self.parent.dir + 'ui/images/buttonIconRed.png'), 'Remove override for this pass', self.goMenuOverrideAttribute)
            else:
                self.addAction(QIcon(self.parent.dir + 'ui/images/buttonIconGreen.png'), 'Add override for this pass', self.goMenuOverrideAttribute)
        elif menuType == 'pass':
            if self.always:
                self.addAction(QIcon(self.parent.dir + 'ui/images/buttonIconRed.png'), 'Set global to off', self.goMenuOverridePass)
            else:
                self.addAction(QIcon(self.parent.dir + 'ui/images/buttonIconGreen.png'), 'Set global to on', self.goMenuOverridePass)
        global_pos = self.widget.mapToGlobal(self.pos)
        self.exec_(global_pos)



    def goMenuOverrideAttribute(self):
        self.parent.goOverrideAttribute(widget=self.widget, always=self.always)



    def goMenuOverridePass(self):
        self.parent.goOverridePass(widget=self.widget, always=self.always)




class Communicate(QObject):
    updateBW = Signal(int)


class BurningWidget(QWidget):

    def __init__(self, parent = None):
        super(BurningWidget, self).__init__()
        self.parent = parent
        self.initUI()



    def initUI(self):
        self.setMinimumSize(1, 30)
        self.value = self.parent.ui.arsenal_qualitySlider.value()
        self.num = [10,
         20,
         30,
         40,
         50,
         60,
         70,
         80,
         90,
         100]



    def setValue(self, value):
        self.value = value



    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()



    def drawWidget(self, qp):
        font = QFont('Serif', 7, QFont.Light)
        qp.setFont(font)
        size = self.size()
        w = size.width()
        h = size.height()
        step = int(round(w / 10.0))
        till = int(w / 100.0 * self.value)
        biasValue = 0.3
        maxValue = 0.3
        tmpValue = 1.0 + (self.value - 50.0) / 50.0 * 99.0
        if tmpValue < 1.0:
            tmpValue = 1.0
        colorR = tmpValue / 100 * maxValue + biasValue
        tmpValue = 100.0 + (self.value - 1.0) / 49.0 * -99.0
        if tmpValue < 1.0:
            tmpValue = 1.0
        colorB = tmpValue / 100 * maxValue + biasValue
        if self.value > 50:
            tmpValue = 100.0 + (self.value - 50.0) / 25.0 * -99.0
            if tmpValue < 1.0:
                tmpValue = 1.0
            colorG = tmpValue / 100 * maxValue + biasValue
        elif self.value == 50:
            colorG = maxValue + biasValue
        else:
            tmpValue = 1.0 + (self.value - 25.0) / 25.0 * 99.0
            if tmpValue < 1.0:
                tmpValue = 1.0
            colorG = tmpValue / 100 * maxValue + biasValue
        qp.setPen(QColor(255, 255, 255))
        qp.setBrush(QColor(colorR * 255, colorG * 255, colorB * 255))
        qp.drawRect(0, 0, till, h)
        qp.setPen(QColor(255, 175, 175))
        qp.setBrush(QColor(colorR * 255, colorG * 255, colorB * 255))
        pen = QPen(QColor(20, 20, 20), 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.setBrush(Qt.NoBrush)
        qp.drawRect(0, 0, w - 1, h - 1)
        j = 0
        for i in range(step, 10 * step, step):
            qp.drawLine(i, 0, i, 5)
            metrics = qp.fontMetrics()
            fw = metrics.width(str(self.num[j]))
            qp.drawText(i - fw / 2, h / 2, str(self.num[j]))
            j = j + 1





class MultimatteMaskUI(QWidget):

    def __init__(self, parent = None, name = None, number = None, passName = None, valide = None):
        self.parent = parent
        self.ui = Ui_arsenal_multimatteMask()
        self.ui.setupUi(self.parent)
        self.name = name
        self.passName = passName
        if valide is None:
            self.valide = False
        else:
            self.valide = valide
        if number is None:
            if self.parent.arsenal.passName[self.passName].multimatteMaskName:
                self.number = self.foundLastMaskNumber() + 1
            else:
                self.number = 1
        else:
            self.number = number
        self.ui.arsenal_multimatteMaskGroupBox.setTitle('Layer : ' + self.passName.name() + ' | Number : ' + str(self.number))
        self.parent.ui.arsenal_createNewMultiMatteMask_layout.insertWidget(1, self.ui.arsenal_multimatteMaskWidget)
        if name is not None:
            self.ui.arsenal_multimatteMaskName.setText(name)
            self.ui.arsenal_multimatteMaskName.setStyleSheet('background-color: rgb(0, 125, 0);\n')
            self.ui.arsenal_multimatteMaskButtonsGroup.setEnabled(True)
        else:
            self.ui.arsenal_multimatteMaskName.setStyleSheet('background-color: rgb(125, 0, 0);\n')
            self.ui.arsenal_multimatteMaskButtonsGroup.setEnabled(False)
        self.ui.arsenal_multimatteMaskRemoveGroupe.clicked.connect(functools.partial(self.goRemoveMultimatteMask))
        self.ui.arsenal_multimatteMaskName.editingFinished.connect(functools.partial(self.goWriteMultimatteMask))
        self.ui.arsenal_multimatteMaskaddInRed.clicked.connect(functools.partial(self.goAddRedChannel))
        self.ui.arsenal_multimatteMaskaddInGreen.clicked.connect(functools.partial(self.goAddGreenChannel))
        self.ui.arsenal_multimatteMaskaddInBlue.clicked.connect(functools.partial(self.goAddBlueChannel))
        self.ui.arsenal_multimatteMaskselectInRed.clicked.connect(functools.partial(self.goSelectRedChannel))
        self.ui.arsenal_multimatteMaskselectInGreen.clicked.connect(functools.partial(self.goSelectGreenChannel))
        self.ui.arsenal_multimatteMaskselectInBlue.clicked.connect(functools.partial(self.goSelectBlueChannel))
        self.ui.arsenal_multimatteMaskremoveInRed.clicked.connect(functools.partial(self.goRemoveRedChannel))
        self.ui.arsenal_multimatteMaskremoveInGreen.clicked.connect(functools.partial(self.goRemoveGreenChannel))
        self.ui.arsenal_multimatteMaskremoveInBlue.clicked.connect(functools.partial(self.goRemoveBlueChannel))



    def foundLastMaskNumber(self):
        hightNum = 1
        for i in self.parent.arsenal.passName[self.passName].multimatteMaskName:
            if i >= hightNum:
                hightNum = i

        return hightNum



    def goRemoveMultimatteMask(self):
        currentPass = self.parent.ui.arsenal_listPass.selectedItems()
        currentPassString = str(currentPass[0].text())
        self.parent.ui.arsenal_createNewMultiMatteMask_layout.removeWidget(self.ui.arsenal_multimatteMaskWidget)
        self.parent.multiMatteMaskListUI.remove(self)
        if self.number in self.parent.arsenal.passName[self.passName].multimatteMaskName:
            self.parent.arsenal.passName[self.passName].multimatteMaskName.pop(self.number)
        self.ui.arsenal_multimatteMaskWidget.destroy()
        self.ui.arsenal_multimatteMaskWidget.close()
        self.parent.arsenal.removeMultimatteMask(layer=currentPassString, number=self.number)



    def goWriteMultimatteMask(self):
        currentPassString = self.passName.name()
        text = str(self.ui.arsenal_multimatteMaskName.text())
        if not self.parent.arsenal.writeMultimatteMask(name=text, layer=currentPassString, number=self.number):
            self.ui.arsenal_multimatteMaskName.setStyleSheet('background-color: rgb(125, 0, 0);\n')
            self.ui.arsenal_multimatteMaskButtonsGroup.setEnabled(False)
            self.valide = False
        else:
            self.ui.arsenal_multimatteMaskName.setStyleSheet('background-color: rgb(0, 125, 0);\n')
            self.ui.arsenal_multimatteMaskButtonsGroup.setEnabled(True)
            self.valide = True
            self.name = text



    def goAddRedChannel(self):
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        self.parent.arsenal.addObjects(selection=currentSelection, renderPass=self.passName, attribute='multimatteMaskMembers[' + str(self.number) + '].multimatteMaskMembersRed')



    def goAddGreenChannel(self):
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        self.parent.arsenal.addObjects(selection=currentSelection, renderPass=self.passName, attribute='multimatteMaskMembers[' + str(self.number) + '].multimatteMaskMembersGreen')



    def goAddBlueChannel(self):
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        self.parent.arsenal.addObjects(selection=currentSelection, renderPass=self.passName, attribute='multimatteMaskMembers[' + str(self.number) + '].multimatteMaskMembersBlue')



    def goSelectRedChannel(self):
        self.parent.arsenal.selectObjects(node=self.passName + '_arsenalPass', attribute='multimatteMaskMembers[' + str(self.number) + '].multimatteMaskMembersRed')



    def goSelectGreenChannel(self):
        self.parent.arsenal.selectObjects(node=self.passName + '_arsenalPass', attribute='multimatteMaskMembers[' + str(self.number) + '].multimatteMaskMembersGreen')



    def goSelectBlueChannel(self):
        self.parent.arsenal.selectObjects(node=self.passName + '_arsenalPass', attribute='multimatteMaskMembers[' + str(self.number) + '].multimatteMaskMembersBlue')



    def goRemoveRedChannel(self):
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        self.parent.arsenal.deleteObjects(selection=currentSelection, node=self.passName + '_arsenalPass', attribute='multimatteMaskMembers[' + str(self.number) + '].multimatteMaskMembersRed')



    def goRemoveGreenChannel(self):
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        self.parent.arsenal.deleteObjects(selection=currentSelection, node=self.passName + '_arsenalPass', attribute='multimatteMaskMembers[' + str(self.number) + '].multimatteMaskMembersGreen')



    def goRemoveBlueChannel(self):
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        self.parent.arsenal.deleteObjects(selection=currentSelection, node=self.passName + '_arsenalPass', attribute='multimatteMaskMembers[' + str(self.number) + '].multimatteMaskMembersBlue')




class ArsenalUI(QDialog):

    def __init__(self, parent = None):
        super(ArsenalUI, self).__init__(parent)
        self.ui = Ui_arsenal_main()
        self.ui.setupUi(self)
        self.version = 1.21
        self.setWindowFlags(Qt.Dialog)
        self.pinWindowStatue = False
        self.thread = None
        self.multiMatteMaskListUI = []
        self.dir = str(os.path.abspath(os.path.dirname(__file__))).replace('\\', '/') + '/'
        self.arsenal = Arsenal(self)
        self.arsenalQualityUi = ArsenalQualityUi(parent=self)
        self.arsenal.arsenalQuality = self.arsenalQualityUi.arsenalQualityTool
        self.passList = []
        self.ui.arsenal_import.clicked.connect(self.goImport)
        self.ui.arsenal_export.clicked.connect(self.goExport)
        self.ui.arsenal_pinWindow.clicked.connect(self.pinWindow)
        self.ui.arsenal_createPass.clicked.connect(self.goNewPasse)
        self.ui.arsenal_deletePass.clicked.connect(self.goDeletePasse)
        self.ui.arsenal_duplicatePass.clicked.connect(self.goDuplicatePasse)
        self.ui.arsenal_listPass.itemClicked.connect(self.goSelectPass)
        self.ui.arsenal_listPass.itemChanged.connect(self.goChangePassProperty)
        self.ui.arsenal_listPass.itemSelectionChanged.connect(self.goChekSelectedPass)
        self.ui.arsenal_addBlackHole.clicked.connect(self.goAddBlackHole)
        self.ui.arsenal_removeBlackHole.clicked.connect(self.godeleteBlackHole)
        self.ui.arsenal_selectBlackHole.clicked.connect(self.goselectBlackHole)
        self.ui.arsenal_addBlackHoleReceiveShd.clicked.connect(self.goAddBlackHoleReceiveShd)
        self.ui.arsenal_removeBlackHoleReceiveShd.clicked.connect(self.goRemoveBlackHoleReceiveShd)
        self.ui.arsenal_selectBlackHoleReceiveShd.clicked.connect(self.goSelectBlackHoleReceiveShd)
        self.ui.arsenal_addGIGenerateOff.clicked.connect(self.goAddGIGenerateOff)
        self.ui.arsenal_removeGIGenerateOff.clicked.connect(self.goRemoveGIGenerateOff)
        self.ui.arsenal_selectGIGenerateOff.clicked.connect(self.goSelectGIGenerateOff)
        self.ui.arsenal_addGIReceiveOff.clicked.connect(self.goAddGIReceiveOff)
        self.ui.arsenal_removeGIReceiveOff.clicked.connect(self.goRemoveGIReceiveOff)
        self.ui.arsenal_selectGIReceiveOff.clicked.connect(self.goSelectGIReceiveOff)
        self.ui.arsenal_addPrimaryOff.clicked.connect(self.goAddPrimaryOff)
        self.ui.arsenal_removePrimaryOff.clicked.connect(self.goRemovePrimaryOff)
        self.ui.arsenal_selectPrimaryOff.clicked.connect(self.goSelectPrimaryOff)
        self.ui.arsenal_addReflectionOff.clicked.connect(self.goAddReflectionOff)
        self.ui.arsenal_removeReflectionOff.clicked.connect(self.goRemoveReflectionOff)
        self.ui.arsenal_selectReflectionOff.clicked.connect(self.goSelectReflectionOff)
        self.ui.arsenal_addRefractionOff.clicked.connect(self.goAddRefractionOff)
        self.ui.arsenal_removeRefractionOff.clicked.connect(self.goRemoveRefractionOff)
        self.ui.arsenal_selectRefractionOff.clicked.connect(self.goSelectRefractionOff)
        self.ui.arsenal_addShdCastOff.clicked.connect(self.goAddShdCastOff)
        self.ui.arsenal_removeShdCastOff.clicked.connect(self.goRemoveShdCastOff)
        self.ui.arsenal_selectShdCastOff.clicked.connect(self.goSelectShdCastOff)
        self.ui.arsenal_addLightSelectNormal.clicked.connect(self.goAddLightSelectNormal)
        self.ui.arsenal_removeLightSelectNormal.clicked.connect(self.godeleteLightSelectNormal)
        self.ui.arsenal_selectLightSelectNormal.clicked.connect(self.goselectLightSelectNormal)
        self.ui.arsenal_addLightSelectDiffuse.clicked.connect(self.goAddLightSelectDiffuse)
        self.ui.arsenal_removeLightSelectDiffuse.clicked.connect(self.godeleteLightSelectDiffuse)
        self.ui.arsenal_selectLightSelectDiffuse.clicked.connect(self.goselectLightSelectDiffuse)
        self.ui.arsenal_addLightSelectRaw.clicked.connect(self.goAddLightSelectRaw)
        self.ui.arsenal_removeLightSelectRaw.clicked.connect(self.godeleteLightSelectRaw)
        self.ui.arsenal_selectLightSelectRaw.clicked.connect(self.goselectLightSelectRaw)
        self.ui.arsenal_addLightSelectSpecular.clicked.connect(self.goAddLightSelectSpecular)
        self.ui.arsenal_removeLightSelectSpecular.clicked.connect(self.godeleteLightSelectSpecular)
        self.ui.arsenal_selectLightSelectSpecular.clicked.connect(self.goselectLightSelectSpecular)
        for myButton in [self.ui.arsenal_addBlackHole,
         self.ui.arsenal_removeBlackHole,
         self.ui.arsenal_selectBlackHole,
         self.ui.arsenal_addBlackHoleReceiveShd,
         self.ui.arsenal_removeBlackHoleReceiveShd,
         self.ui.arsenal_selectBlackHoleReceiveShd,
         self.ui.arsenal_addGIGenerateOff,
         self.ui.arsenal_removeGIGenerateOff,
         self.ui.arsenal_selectGIGenerateOff,
         self.ui.arsenal_addGIReceiveOff,
         self.ui.arsenal_removeGIReceiveOff,
         self.ui.arsenal_selectGIReceiveOff,
         self.ui.arsenal_addPrimaryOff,
         self.ui.arsenal_removePrimaryOff,
         self.ui.arsenal_selectPrimaryOff,
         self.ui.arsenal_addReflectionOff,
         self.ui.arsenal_removeReflectionOff,
         self.ui.arsenal_selectReflectionOff,
         self.ui.arsenal_addRefractionOff,
         self.ui.arsenal_removeRefractionOff,
         self.ui.arsenal_selectRefractionOff,
         self.ui.arsenal_addShdCastOff,
         self.ui.arsenal_removeShdCastOff,
         self.ui.arsenal_selectShdCastOff,
         self.ui.arsenal_addLightSelectNormal,
         self.ui.arsenal_removeLightSelectNormal,
         self.ui.arsenal_selectLightSelectNormal,
         self.ui.arsenal_addLightSelectDiffuse,
         self.ui.arsenal_removeLightSelectDiffuse,
         self.ui.arsenal_selectLightSelectDiffuse,
         self.ui.arsenal_addLightSelectRaw,
         self.ui.arsenal_removeLightSelectRaw,
         self.ui.arsenal_selectLightSelectRaw,
         self.ui.arsenal_addLightSelectSpecular,
         self.ui.arsenal_removeLightSelectSpecular,
         self.ui.arsenal_selectLightSelectSpecular]:
            myButton.setStyleSheet('background-image: url(' + self.dir + '/ui/images/generalButton.png); background-repeat: no-repeat; background-position: center;')

        self.ui.arsenal_import.setStyleSheet('background-image: url(' + self.dir + '/ui/images/import.png); background-repeat: no-repeat; background-position: center; Text-align:left; padding: 10px;')
        self.ui.arsenal_export.setStyleSheet('background-image: url(' + self.dir + '/ui/images/export.png); background-repeat: no-repeat; background-position: center; Text-align:left; padding: 10px;')
        self.ui.arsenal_pinWindow.setStyleSheet('background-image: url(' + self.dir + '/ui/images/pin.png); background-repeat: no-repeat;')
        self.ui.arsenal_createNewMultiMatteMask.clicked.connect(self.goCreateNewMultimatteMask)
        self.GITypeListView = self.ui.arsenal_FastGIType.view()
        self.GITypeListView.setMinimumSize(330, 100)
        self.ui.arsenal_lightSelectAutoNormal.stateChanged[int].connect(self.goLightSelect)
        self.ui.arsenal_lightSelectAutoDiffuse.stateChanged[int].connect(self.goLightSelect)
        self.ui.arsenal_lightSelectAutoRaw.stateChanged[int].connect(self.goLightSelect)
        self.ui.arsenal_lightSelectAutoSpecular.stateChanged[int].connect(self.goLightSelect)
        self.ui.arsenal_FastGI.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastGIType.activated.connect(self.goFastControl)
        self.ui.arsenal_FastAO.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastGE.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastRR.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastM.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastSHD.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastAA.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastDSP.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastMB.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastDOF.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastOVENV.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastVLambert.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastDR.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastMaterialID.stateChanged[int].connect(self.goFastControl)
        self.ui.arsenal_FastProxyObjectID.stateChanged[int].connect(self.goFastControl)
        self.c = Communicate()
        self.wid = BurningWidget(self)
        self.c.updateBW[int].connect(self.wid.setValue)
        self.ui.arsenal_qualitySlider.valueChanged[int].connect(self.changeValue)
        self.ui.verticalLayout_10.addWidget(self.wid)
        self.ui.arsenal_qualityLCDFrame.setStyleSheet('background-image: url(' + self.dir + '/ui/images/qualityButtonRound.png); background-repeat: no-repeat; background-position: right; background-clip: padding; padding-right: 16px;')
        self.ui.arsenal_qualityLCDGlobal_optionLCDFrame.setStyleSheet('background-image: url(' + self.dir + '/ui/images/qualityButtonRoundMini.png); background-repeat: no-repeat; background-position: right; background-clip: padding; padding-right: 8px; max-width: 16px;')
        self.ui.arsenal_qualityLCDImageSamplerLCDFrame.setStyleSheet('background-image: url(' + self.dir + '/ui/images/qualityButtonRoundMini.png); background-repeat: no-repeat; background-position: right; background-clip: padding; padding-right: 8px; max-width: 16px;')
        self.ui.arsenal_qualityLCDDMCSamplerLCDFrame.setStyleSheet('background-image: url(' + self.dir + '/ui/images/qualityButtonRoundMini.png); background-repeat: no-repeat; background-position: right; background-clip: padding; padding-right: 8px; max-width: 16px;')
        self.ui.arsenal_qualityLCDIrradianceMapLCDFrame.setStyleSheet('background-image: url(' + self.dir + '/ui/images/qualityButtonRoundMini.png); background-repeat: no-repeat; background-position: right; background-clip: padding; padding-left: 3px; max-width: 16px;')
        self.ui.arsenal_qualityLCDLightCacheLCDFrame.setStyleSheet('background-image: url(' + self.dir + '/ui/images/qualityButtonRoundMini.png); background-repeat: no-repeat; background-position: right; background-clip: padding; padding-left: 3px; max-width: 16px;')
        self.ui.arsenal_qualityLCDSystemLCDFrame.setStyleSheet('background-image: url(' + self.dir + '/ui/images/qualityButtonRoundMini.png); background-repeat: no-repeat; background-position: right; background-clip: padding; padding-left: 3px; max-width: 16px;')
        self.ui.arsenal_qualityLCD.setStyleSheet('background: none; color: rgb(255, 255, 255);')
        self.ui.arsenal_qualityLCDGlobal_option.setStyleSheet('background: none; color: rgb(255, 255, 255);')
        self.ui.arsenal_qualityLCDImageSampler.setStyleSheet('background: none; color: rgb(255, 255, 255);')
        self.ui.arsenal_qualityLCDDMCSampler.setStyleSheet('background: none; color: rgb(255, 255, 255);')
        self.ui.arsenal_qualityLCDIrradianceMap.setStyleSheet('background: none; color: rgb(255, 255, 255);')
        self.ui.arsenal_qualityLCDLightCache.setStyleSheet('background: none; color: rgb(255, 255, 255);')
        self.ui.arsenal_qualityLCDSystem.setStyleSheet('background: none; color: rgb(255, 255, 255);')
        self.ui.arsenal_listPass.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_listPass.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_listPass))
        self.ui.arsenal_FastGI.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_FastGI.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_FastGI))
        self.ui.arsenal_FastGIType.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_FastGIType.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_FastGIType))
        self.ui.arsenal_FastAO.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_FastAO.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_FastAO))
        self.ui.arsenal_FastGE.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_FastGE.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_FastGE))
        self.ui.arsenal_FastRR.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_FastRR.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_FastRR))
        self.ui.arsenal_FastM.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_FastM.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_FastM))
        self.ui.arsenal_FastSHD.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_FastSHD.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_FastSHD))
        self.ui.arsenal_FastAA.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_FastAA.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_FastAA))
        self.ui.arsenal_FastDSP.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_FastDSP.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_FastDSP))
        self.ui.arsenal_FastMB.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_FastMB.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_FastMB))
        self.ui.arsenal_FastDOF.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_FastDOF.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_FastDOF))
        self.ui.arsenal_FastOVENV.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_FastOVENV.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_FastOVENV))
        self.ui.arsenal_FastDR.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.arsenal_FastDR.customContextMenuRequested[QPoint].connect(functools.partial(self.menuRightClick, self.ui.arsenal_FastDR))
        self.ui.arsenal_multiProxyImporter.clicked.connect(functools.partial(self.goToolBoxProxyMultiImporter))
        self.ui.arsenal_shaderAutoConnectProxy.clicked.connect(functools.partial(self.goToolBoxProxyShaderAutoConnect))
        self.ui.arsenal_addMaterialIDSelection.clicked.connect(functools.partial(self.goAddMaterialIDSelection))
        self.ui.arsenal_addMaterialIDMaterials.clicked.connect(functools.partial(self.goAddMaterialIDMaterials))
        self.ui.arsenal_addMaterialIDSG.clicked.connect(functools.partial(self.goAddMaterialIDSG))
        self.ui.arsenal_setMaterialIDSelection.clicked.connect(functools.partial(self.goSetMaterialIDSelection))
        self.ui.arsenal_setMaterialIDMaterials.clicked.connect(functools.partial(self.goSetMaterialIDMaterials))
        self.ui.arsenal_setMaterialIDSG.clicked.connect(functools.partial(self.goSetMaterialIDSG))
        self.ui.arsenal_removeMaterialIDSelection.clicked.connect(functools.partial(self.goRemoveMaterialIDSelection))
        self.ui.arsenal_removeMaterialIDMaterials.clicked.connect(functools.partial(self.goRemoveMaterialIDMaterials))
        self.ui.arsenal_removeMaterialIDSG.clicked.connect(functools.partial(self.goRemoveMaterialIDSG))
        self.ui.arsenal_addObjectIDSelection.clicked.connect(functools.partial(self.goAddObjectIDSelection))
        self.ui.arsenal_addObjectIDAll.clicked.connect(functools.partial(self.goAddObjectIDAll))
        self.ui.arsenal_setObjectIDSelection.clicked.connect(functools.partial(self.goSetObjectIDSelection))
        self.ui.arsenal_setObjectIDAll.clicked.connect(functools.partial(self.goSetObjectIDAll))
        self.ui.arsenal_removeObjectIDSelection.clicked.connect(functools.partial(self.goRemoveObjectIDSelection))
        self.ui.arsenal_removeObjectIDAll.clicked.connect(functools.partial(self.goRemoveObjectIDAll))
        self.ui.arsenal_FastMaterial_reflecGo.clicked.connect(functools.partial(self.goControlMaterialReflection))
        self.ui.arsenal_FastMaterial_refracGo.clicked.connect(functools.partial(self.goControlMaterialRefraction))
        self.ui.arsenal_FastLight_Go.clicked.connect(functools.partial(self.goFastControlLight))
        self.threadPool = []



    def __del__(self):
        del self.wid
        print 'Goodbye'



    def pinWindow(self):
        if not self.pinWindowStatue:
            self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
            self.ui.arsenal_pinWindow.setStyleSheet('background-image: url(' + self.dir + '/ui/images/pin.png); background-repeat: no-repeat;background-color: rgb(0, 150, 0);')
            self.pinWindowStatue = True
        else:
            self.setWindowFlags(Qt.Dialog)
            self.ui.arsenal_pinWindow.setStyleSheet('background-image: url(' + self.dir + '/ui/images/pin.png); background-repeat: no-repeat;')
            self.pinWindowStatue = False
        self.close()
        self.show()



    def changeValue(self):
        self.ui.arsenal_qualityLCD.display(self.ui.arsenal_qualitySlider.value())
        value = self.ui.arsenal_qualitySlider.value() + self.ui.arsenal_qualityOptimizationChooserGlobalOptionValue.value()
        if value > 99:
            value = 99
        elif value < 1:
            value = 1
        self.ui.arsenal_qualityLCDGlobal_option.display(value)
        value = self.ui.arsenal_qualitySlider.value() + self.ui.arsenal_qualityOptimizationChooserIrradianceMapValue.value()
        if value > 99:
            value = 99
        elif value < 1:
            value = 1
        self.ui.arsenal_qualityLCDIrradianceMap.display(value)
        value = self.ui.arsenal_qualitySlider.value() + self.ui.arsenal_qualityOptimizationChooserImageSamplerValue.value()
        if value > 99:
            value = 99
        elif value < 1:
            value = 1
        self.ui.arsenal_qualityLCDImageSampler.display(value)
        value = self.ui.arsenal_qualitySlider.value() + self.ui.arsenal_qualityOptimizationChooserLightCacheValue.value()
        if value > 99:
            value = 99
        elif value < 1:
            value = 1
        self.ui.arsenal_qualityLCDLightCache.display(value)
        value = self.ui.arsenal_qualitySlider.value() + self.ui.arsenal_qualityOptimizationChooserDMCSamplerValue.value()
        if value > 99:
            value = 99
        elif value < 1:
            value = 1
        self.ui.arsenal_qualityLCDDMCSampler.display(value)
        value = self.ui.arsenal_qualitySlider.value() + self.ui.arsenal_qualityOptimizationChooserSystemValue.value()
        if value > 99:
            value = 99
        elif value < 1:
            value = 1
        self.ui.arsenal_qualityLCDSystem.display(value)
        self.c.updateBW.emit(self.ui.arsenal_qualitySlider.value())
        self.wid.repaint()



    def goCreateNewMultimatteMask(self):
        for myMultimatte in self.multiMatteMaskListUI:
            if not myMultimatte.valide or myMultimatte.name == '':
                return 

        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            self.multiMatteMaskListUI.append(MultimatteMaskUI(parent=self, passName=passName))




    def menuRightClick(self, widget, pos):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        if not currentPass or str(currentPass[0].text()) == 'defaultRenderLayer':
            return 
        if widget == self.ui.arsenal_listPass:
            menuType = 'pass'
            if not pm.getAttr(str(currentPass[0].text()) + '.global'):
                always = False
            else:
                always = True
        elif widget == self.ui.arsenal_FastGI:
            menuType = 'fastOverride'
            if pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) is None or 'vraySettings.giOn' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True):
                always = False
            else:
                always = True
        elif widget == self.ui.arsenal_FastGIType:
            menuType = 'fastOverride'
            if pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) is None or 'vraySettings.primaryEngine' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) and 'vraySettings.secondaryEngine' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True):
                always = False
            else:
                always = True
        elif widget == self.ui.arsenal_FastAO:
            menuType = 'fastOverride'
            if pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) is None or 'vraySettings.aoOn' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True):
                always = False
            else:
                always = True
        elif widget == self.ui.arsenal_FastGE:
            menuType = 'fastOverride'
            if pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) is None or 'vraySettings.globopt_mtl_glossy' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True):
                always = False
            else:
                always = True
        elif widget == self.ui.arsenal_FastRR:
            menuType = 'fastOverride'
            if pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) is None or 'vraySettings.globopt_mtl_reflectionRefraction' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True):
                always = False
            else:
                always = True
        elif widget == self.ui.arsenal_FastM:
            menuType = 'fastOverride'
            if pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) is None or 'vraySettings.globopt_mtl_doMaps' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True):
                always = False
            else:
                always = True
        elif widget == self.ui.arsenal_FastSHD:
            menuType = 'fastOverride'
            if pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) is None or 'vraySettings.globopt_light_doShadows' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True):
                always = False
            else:
                always = True
        elif widget == self.ui.arsenal_FastAA:
            menuType = 'fastOverride'
            if pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) is None or 'vraySettings.aaFilterOn' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True):
                always = False
            else:
                always = True
        elif widget == self.ui.arsenal_FastDSP:
            menuType = 'fastOverride'
            if pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) is None or 'vraySettings.globopt_geom_displacement' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True):
                always = False
            else:
                always = True
        elif widget == self.ui.arsenal_FastMB:
            menuType = 'fastOverride'
            if pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) is None or 'vraySettings.cam_mbOn' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True):
                always = False
            else:
                always = True
        elif widget == self.ui.arsenal_FastDOF:
            menuType = 'fastOverride'
            if pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) is None or 'vraySettings.cam_dofOn' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True):
                always = False
            else:
                always = True
        elif widget == self.ui.arsenal_FastOVENV:
            menuType = 'fastOverride'
            if pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) is None or 'vraySettings.cam_overrideEnvtex' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True):
                always = False
            else:
                always = True
        elif widget == self.ui.arsenal_FastDR:
            menuType = 'fastOverride'
            if pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True) is None or 'vraySettings.sys_distributed_rendering_on' not in pm.editRenderLayerAdjustment(str(currentPass[0].text()), q=True, layer=True):
                always = False
            else:
                always = True
        self.overrideMenu = OverrideCustomMenu(parent=self, widget=widget, pos=pos, always=always, menuType=menuType)



    def goOverridePass(self, widget = None, always = None):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            if not always:
                pm.setAttr(passName.name() + '.global', True)
            else:
                pm.setAttr(passName.name() + '.global', False)




    def goOverrideAttribute(self, widget = None, always = None):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            arsenalPass = passName.name() + '_arsenalPass'
            if widget == self.ui.arsenal_lightSelectAutoNormal:
                attribute = ['lightSelectAllNormal']
                node = [arsenalPass]
            elif widget == self.ui.arsenal_lightSelectAutoDiffuse:
                attribute = ['lightSelectAllDiffuse']
                node = [arsenalPass]
            elif widget == self.ui.arsenal_lightSelectAutoRaw:
                attribute = ['lightSelectAllRaw']
                node = [arsenalPass]
            elif widget == self.ui.arsenal_lightSelectAutoSpecular:
                attribute = ['lightSelectAllSpecular']
                node = [arsenalPass]
            elif widget == self.ui.arsenal_FastGI:
                attribute = ['giOn']
                node = ['vraySettings', arsenalPass]
            elif widget == self.ui.arsenal_FastGIType:
                attribute = ['primaryEngine', 'secondaryEngine']
                node = ['vraySettings', arsenalPass]
            elif widget == self.ui.arsenal_FastAO:
                attribute = ['aoOn']
                node = ['vraySettings', arsenalPass]
            elif widget == self.ui.arsenal_FastGE:
                attribute = ['globopt_mtl_glossy']
                node = ['vraySettings', arsenalPass]
            elif widget == self.ui.arsenal_FastRR:
                attribute = ['globopt_mtl_reflectionRefraction']
                node = ['vraySettings', arsenalPass]
            elif widget == self.ui.arsenal_FastM:
                attribute = ['globopt_mtl_doMaps']
                node = ['vraySettings', arsenalPass]
            elif widget == self.ui.arsenal_FastSHD:
                attribute = ['globopt_light_doShadows']
                node = ['vraySettings', arsenalPass]
            elif widget == self.ui.arsenal_FastAA:
                attribute = ['aaFilterOn']
                node = ['vraySettings', arsenalPass]
            elif widget == self.ui.arsenal_FastDSP:
                attribute = ['globopt_geom_displacement']
                node = ['vraySettings', arsenalPass]
            elif widget == self.ui.arsenal_FastMB:
                attribute = ['cam_mbOn']
                node = ['vraySettings', arsenalPass]
            elif widget == self.ui.arsenal_FastDOF:
                attribute = ['cam_dofOn']
                node = ['vraySettings', arsenalPass]
            elif widget == self.ui.arsenal_FastOVENV:
                attribute = ['cam_overrideEnvtex']
                node = ['vraySettings', arsenalPass]
            elif widget == self.ui.arsenal_FastVLambert:
                attribute = ['vrayLambert']
                node = [arsenalPass]
            elif widget == self.ui.arsenal_FastMaterialID:
                attribute = ['vrayMaterialID']
                node = [arsenalPass]
            elif widget == self.ui.arsenal_FastProxyObjectID:
                attribute = ['vrayProxyObjectID']
                node = [arsenalPass]
            elif widget == self.ui.arsenal_FastDR:
                attribute = ['sys_distributed_rendering_on']
                node = ['vraySettings', arsenalPass]
            for myNode in node:
                for myAttr in attribute:
                    self.arsenal.overrideAttribute(renderPass=passName, node=myNode, attribute=myAttr, always=always)


            if always:
                widget.setStyleSheet('')
            else:
                widget.setStyleSheet('background-color: rgb(204, 102, 0);\nborder:1px solid rgb(255, 170, 255);\ncolor:rgb(0, 0, 0);')




    def goImport(self):
        basicFilter = '*.arpass'
        paths = pm.fileDialog2(fileFilter=basicFilter, dialogStyle=2, caption='Export ArsenalPass', fileMode=4, okCaption='Import')
        self.arsenal.importPass(paths=paths)
        self.refresh()



    def goExport(self):
        currentSelection = self.ui.arsenal_listPass.selectedItems()
        selectedPass = list()
        strList = ''
        for selec in currentSelection:
            selectedPass.append(str(selec.text()))
            strList += str(selec.text()) + '\n'

        icon = QMessageBox.Question
        msgBox = QMessageBox()
        msgBox.setText('Do you want to export selected pass ?')
        msgBox.setInformativeText('Click on "Show Details" to see selected pass...')
        msgBox.setDetailedText(strList)
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)
        msgBox.setIcon(icon)
        ret = msgBox.exec_()
        if ret == QMessageBox.Yes:
            if selectedPass:
                basicFilter = '*.arpass'
                path = pm.fileDialog2(fileFilter=basicFilter, dialogStyle=2, caption='Export ArsenalPass', fileMode=0)
                self.arsenal.exportPass(layers=selectedPass, path=path)
            else:
                OpenMaya.MGlobal.displayError('[Arsenal] Please select pass.')
                return 
        elif ret == QMessageBox.No:
            print 'Canceled'



    def goNewPasse(self):
        validation = True
        while validation:
            (val, ok,) = QInputDialog.getText(self, 'New passe name', 'New passe:')
            if ok:
                if self.arsenal.isNotEmpty(val) and not str(val).isdigit():
                    name = str(val)
                    if self.passeNameValid(name):
                        self.arsenal.createPass(name)
                        validation = False
                else:
                    pm.mel.warning('You must enter a name !')
                    validation = False
            else:
                validation = False

        self.refresh()



    def goDeletePasse(self):
        currentSelection = self.ui.arsenal_listPass.selectedItems()
        for selec in currentSelection:
            self.arsenal.deletePass(layer=str(selec.text()))

        self.refresh()



    def goDuplicatePasse(self):
        currentSelection = self.ui.arsenal_listPass.selectedItems()
        for selec in currentSelection:
            renderPass = pm.PyNode(str(selec.text()))
            validation = True
            while validation:
                (val, ok,) = QInputDialog.getText(self, 'New passe name', 'New passe:')
                if ok:
                    if self.arsenal.isNotEmpty(val) and not str(val).isdigit():
                        name = str(val)
                        if self.passeNameValid(name):
                            self.arsenal.duplicatePass(layer=renderPass, name=name)
                            validation = False
                    else:
                        pm.mel.warning('You must enter a name !')
                        validation = False
                else:
                    validation = False


        self.refresh()



    def goSelectPass(self):
        currentSelection = self.ui.arsenal_listPass.selectedItems()
        for selec in currentSelection:
            renderPass = pm.PyNode(str(selec.text()))
            self.arsenal.selectPass(layer=renderPass)
            break

        self.refresh()



    def goChangePassProperty(self):
        currentSelection = self.ui.arsenal_listPass.selectedItems()
        for selec in currentSelection:
            renderPass = pm.PyNode(str(selec.text()))
            if selec.checkState():
                checkBoxValue = True
                selec.setBackground(QColor(0, 130, 0, 255))
            else:
                checkBoxValue = False
                selec.setBackground(QColor(50, 50, 50, 255))
            self.arsenal.changePropertyPass(layer=renderPass, renderable=checkBoxValue)




    def goChekSelectedPass(self):
        if not self.ui.arsenal_listPass.selectedItems():
            currentLayer = pm.PyNode(str(pm.editRenderLayerGlobals(query=True, currentRenderLayer=True)))
            self.ui.arsenal_listPass.clearSelection()
            items = self.ui.arsenal_listPass.findItems(currentLayer.name(), Qt.MatchExactly)
            if len(items):
                self.ui.arsenal_listPass.setCurrentItem(items[0])



    def goAddBlackHole(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            self.arsenal.addObjects(selection=currentSelection, renderPass=passName, attribute='blackHoleMembers')

        self.refreshObjectsUI()



    def godeleteBlackHole(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.deleteObjects(selection=currentSelection, node=passName, attribute='blackHoleMembers')

        self.refresh()



    def goselectBlackHole(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.selectObjects(node=passName, attribute='blackHoleMembers')

        self.refreshObjectsUI()



    def goAddBlackHoleReceiveShd(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            self.arsenal.addObjects(selection=currentSelection, renderPass=passName, attribute='blackHoleMembersReceiveShd')

        self.refreshObjectsUI()



    def goRemoveBlackHoleReceiveShd(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.deleteObjects(selection=currentSelection, node=passName, attribute='blackHoleMembersReceiveShd')

        self.refresh()



    def goSelectBlackHoleReceiveShd(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.selectObjects(node=passName, attribute='blackHoleMembersReceiveShd')

        self.refreshObjectsUI()



    def goAddGIGenerateOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            self.arsenal.addObjects(selection=currentSelection, renderPass=passName, attribute='giMembersGenerate')

        self.refreshObjectsUI()



    def goRemoveGIGenerateOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.deleteObjects(selection=currentSelection, node=passName, attribute='giMembersGenerate')

        self.refresh()



    def goSelectGIGenerateOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.selectObjects(node=passName, attribute='giMembersGenerate')

        self.refreshObjectsUI()



    def goAddGIReceiveOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            self.arsenal.addObjects(selection=currentSelection, renderPass=passName, attribute='giMembersReceive')

        self.refreshObjectsUI()



    def goRemoveGIReceiveOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.deleteObjects(selection=currentSelection, node=passName, attribute='giMembersReceive')

        self.refresh()



    def goSelectGIReceiveOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.selectObjects(node=passName, attribute='giMembersReceive')

        self.refreshObjectsUI()



    def goAddPrimaryOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            self.arsenal.addObjects(selection=currentSelection, renderPass=passName, attribute='primaryMembersOff')

        self.refreshObjectsUI()



    def goRemovePrimaryOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.deleteObjects(selection=currentSelection, node=passName, attribute='primaryMembersOff')

        self.refresh()



    def goSelectPrimaryOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.selectObjects(node=passName, attribute='primaryMembersOff')

        self.refreshObjectsUI()



    def goAddReflectionOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            self.arsenal.addObjects(selection=currentSelection, renderPass=passName, attribute='reflectionMembersOff')

        self.refreshObjectsUI()



    def goRemoveReflectionOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.deleteObjects(selection=currentSelection, node=passName, attribute='reflectionMembersOff')

        self.refresh()



    def goSelectReflectionOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.selectObjects(node=passName, attribute='reflectionMembersOff')

        self.refreshObjectsUI()



    def goAddRefractionOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            self.arsenal.addObjects(selection=currentSelection, renderPass=passName, attribute='refractionMembersOff')

        self.refreshObjectsUI()



    def goRemoveRefractionOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.deleteObjects(selection=currentSelection, node=passName, attribute='refractionMembersOff')

        self.refresh()



    def goSelectRefractionOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.selectObjects(node=passName, attribute='refractionMembersOff')

        self.refreshObjectsUI()



    def goAddShdCastOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            self.arsenal.addObjects(selection=currentSelection, renderPass=passName, attribute='shadowCastsMembersOff')

        self.refreshObjectsUI()



    def goRemoveShdCastOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, geometry=True, transforms=True)
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.deleteObjects(selection=currentSelection, node=passName, attribute='shadowCastsMembersOff')

        self.refresh()



    def goSelectShdCastOff(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.selectObjects(node=passName, attribute='shadowCastsMembersOff')

        self.refreshObjectsUI()



    def goAddLightSelectNormal(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, dag=True, fl=True, type=pm.listNodeTypes('light'))
        if not currentSelection:
            OpenMaya.MGlobal.displayError('[Arsenal] Please select light(s).')
            return 
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            self.arsenal.addObjects(selection=currentSelection, renderPass=passName, attribute='lightSelectNormalMembers')

        self.refreshObjectsUI()



    def godeleteLightSelectNormal(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, dag=True, fl=True, type=pm.listNodeTypes('light'))
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.deleteObjects(selection=currentSelection, node=passName, attribute='lightSelectNormalMembers')

        self.refresh()



    def goselectLightSelectNormal(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.selectObjects(node=passName, attribute='lightSelectNormalMembers')

        self.refreshObjectsUI()



    def goAddLightSelectDiffuse(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, dag=True, fl=True, type=pm.listNodeTypes('light'))
        if not currentSelection:
            OpenMaya.MGlobal.displayError('[Arsenal] Please select light(s).')
            return 
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            self.arsenal.addObjects(selection=currentSelection, renderPass=passName, attribute='lightSelectDiffuseMembers')

        self.refreshObjectsUI()



    def godeleteLightSelectDiffuse(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, dag=True, fl=True, type=pm.listNodeTypes('light'))
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.deleteObjects(selection=currentSelection, node=passName, attribute='lightSelectDiffuseMembers')

        self.refresh()



    def goselectLightSelectDiffuse(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.selectObjects(node=passName, attribute='lightSelectDiffuseMembers')

        self.refreshObjectsUI()



    def goAddLightSelectRaw(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, dag=True, fl=True, type=pm.listNodeTypes('light'))
        if not currentSelection:
            OpenMaya.MGlobal.displayError('[Arsenal] Please select light(s).')
            return 
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            self.arsenal.addObjects(selection=currentSelection, renderPass=passName, attribute='lightSelectRawMembers')

        self.refreshObjectsUI()



    def godeleteLightSelectRaw(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, dag=True, fl=True, type=pm.listNodeTypes('light'))
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.deleteObjects(selection=currentSelection, node=passName, attribute='lightSelectRawMembers')

        self.refresh()



    def goselectLightSelectRaw(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.selectObjects(node=passName, attribute='lightSelectRawMembers')

        self.refreshObjectsUI()



    def goAddLightSelectSpecular(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, dag=True, fl=True, type=pm.listNodeTypes('light'))
        if not currentSelection:
            OpenMaya.MGlobal.displayError('[Arsenal] Please select light(s).')
            return 
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            self.arsenal.addObjects(selection=currentSelection, renderPass=passName, attribute='lightSelectSpecularMembers')

        self.refreshObjectsUI()



    def godeleteLightSelectSpecular(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        currentSelection = pm.ls(sl=True, l=True, dag=True, fl=True, type=pm.listNodeTypes('light'))
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.deleteObjects(selection=currentSelection, node=passName, attribute='lightSelectSpecularMembers')

        self.refresh()



    def goselectLightSelectSpecular(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = str(selec.text()) + '_arsenalPass'
            self.arsenal.selectObjects(node=passName, attribute='lightSelectSpecularMembers')

        self.refreshObjectsUI()



    def goFastControl(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            if self.ui.arsenal_FastGI.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='giOn', value=value)
            index = self.ui.arsenal_FastGIType.currentIndex()
            if index == 0:
                self.arsenal.setValue(renderPass=passName, attribute='primaryEngine', value=3)
                self.arsenal.setValue(renderPass=passName, attribute='secondaryEngine', value=3)
                self.arsenal.setValue(renderPass=passName, attribute='imap_detailEnhancement', value=False)
            elif index == 1:
                self.arsenal.setValue(renderPass=passName, attribute='primaryEngine', value=0)
                self.arsenal.setValue(renderPass=passName, attribute='secondaryEngine', value=3)
                self.arsenal.setValue(renderPass=passName, attribute='imap_detailEnhancement', value=False)
            elif index == 2:
                self.arsenal.setValue(renderPass=passName, attribute='primaryEngine', value=0)
                self.arsenal.setValue(renderPass=passName, attribute='secondaryEngine', value=3)
                self.arsenal.setValue(renderPass=passName, attribute='imap_detailEnhancement', value=True)
            elif index == 3:
                self.arsenal.setValue(renderPass=passName, attribute='primaryEngine', value=0)
                self.arsenal.setValue(renderPass=passName, attribute='secondaryEngine', value=2)
                self.arsenal.setValue(renderPass=passName, attribute='imap_detailEnhancement', value=False)
            elif index == 4:
                self.arsenal.setValue(renderPass=passName, attribute='primaryEngine', value=0)
                self.arsenal.setValue(renderPass=passName, attribute='secondaryEngine', value=2)
                self.arsenal.setValue(renderPass=passName, attribute='imap_detailEnhancement', value=True)
            elif index == 5:
                self.arsenal.setValue(renderPass=passName, attribute='primaryEngine', value=2)
                self.arsenal.setValue(renderPass=passName, attribute='secondaryEngine', value=3)
                self.arsenal.setValue(renderPass=passName, attribute='imap_detailEnhancement', value=False)
            elif index == 6:
                self.arsenal.setValue(renderPass=passName, attribute='primaryEngine', value=2)
                self.arsenal.setValue(renderPass=passName, attribute='secondaryEngine', value=2)
                self.arsenal.setValue(renderPass=passName, attribute='imap_detailEnhancement', value=False)
            if self.ui.arsenal_FastAO.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='aoOn', value=value)
            if self.ui.arsenal_FastGE.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='globopt_mtl_glossy', value=value)
            if self.ui.arsenal_FastRR.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='globopt_mtl_reflectionRefraction', value=value)
            if self.ui.arsenal_FastM.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='globopt_mtl_doMaps', value=value)
            if self.ui.arsenal_FastSHD.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='globopt_light_doShadows', value=value)
            if self.ui.arsenal_FastAA.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='aaFilterOn', value=value)
            if self.ui.arsenal_FastDSP.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='globopt_geom_displacement', value=value)
            if self.ui.arsenal_FastMB.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='cam_mbOn', value=value)
            if self.ui.arsenal_FastDOF.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='cam_dofOn', value=value)
            if self.ui.arsenal_FastOVENV.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='cam_overrideEnvtex', value=value)
            if self.ui.arsenal_FastVLambert.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='vrayLambert', value=value)
            if self.ui.arsenal_FastDR.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='sys_distributed_rendering_on', value=value)
            if self.ui.arsenal_FastMaterialID.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='vrayMaterialID', value=value)
            if self.ui.arsenal_FastProxyObjectID.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='vrayProxyObjectID', value=value)




    def goControlMaterialReflection(self):
        self.goFastControlMaterial(1)



    def goControlMaterialRefraction(self):
        self.goFastControlMaterial(2)



    def goFastControlMaterial(self, mode):
        """
        mode 1 : reflection
        mode 2 : refraction
        """
        if self.ui.arsenal_FastMaterial_allRB.isChecked():
            selectionAll = True
        else:
            selectionAll = False
        valueReflecSub = self.ui.arsenal_FastMaterial_reflecSub.value()
        valueRefracSub = self.ui.arsenal_FastMaterial_refracSub.value()
        valueReflecInt = self.ui.arsenal_FastMaterial_reflecInt.isChecked()
        valueRefracInt = self.ui.arsenal_FastMaterial_refracInt.isChecked()
        valueReflecDepth = self.ui.arsenal_FastMaterial_reflecDepth.value()
        valueRefracDepth = self.ui.arsenal_FastMaterial_refracDepth.value()
        arsenalToolBox.arsenal_materialControl(arsenal=self.arsenal, selectionAll=selectionAll, valueReflecSub=valueReflecSub, valueRefracSub=valueRefracSub, valueReflecInt=valueReflecInt, valueRefracInt=valueRefracInt, valueReflecDepth=valueReflecDepth, valueRefracDepth=valueRefracDepth, mode=mode)



    def goFastControlLight(self):
        if self.ui.arsenal_FastLight_allRB.isChecked():
            selectionAll = True
        else:
            selectionAll = False
        value = self.ui.arsenal_FastLight_shdSub.value()
        arsenalToolBox.arsenal_lightControl(arsenal=self.arsenal, selectionAll=selectionAll, value=value)



    def goLightSelect(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        for selec in currentPass:
            passName = pm.PyNode(str(selec.text()))
            if self.ui.arsenal_lightSelectAutoNormal.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='lightSelectAllNormal', value=value)
            if self.ui.arsenal_lightSelectAutoDiffuse.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='lightSelectAllDiffuse', value=value)
            if self.ui.arsenal_lightSelectAutoRaw.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='lightSelectAllRaw', value=value)
            if self.ui.arsenal_lightSelectAutoSpecular.isChecked():
                value = True
            else:
                value = False
            self.arsenal.setValue(renderPass=passName, attribute='lightSelectAllSpecular', value=value)




    def goToolBoxProxyMultiImporter(self):
        arsenalToolBox.arsenal_proxyMultiImporter()



    def goToolBoxProxyShaderAutoConnect(self):
        ignoreNamespace = self.ui.arsenal_shaderAutoConnectProxyIgnoreNameSpace.checkState()
        arsenalToolBox.arsenal_proxyShaderAutoConnect(ignoreNamespace=ignoreNamespace)



    def goAddMaterialIDSelection(self):
        arsenalToolBox.arsenal_materialIDaddSelection()



    def goAddMaterialIDMaterials(self):
        arsenalToolBox.arsenal_materialIDaddAllMat()



    def goAddMaterialIDSG(self):
        arsenalToolBox.arsenal_materialIDaddAllSG()



    def goSetMaterialIDSelection(self):
        arsenalToolBox.arsenal_materialIDsetSelection()



    def goSetMaterialIDMaterials(self):
        arsenalToolBox.arsenal_materialIDsetAllMat()



    def goSetMaterialIDSG(self):
        arsenalToolBox.arsenal_materialIDsetAllSG()



    def goRemoveMaterialIDSelection(self):
        arsenalToolBox.arsenal_materialIDdeleteSelection()



    def goRemoveMaterialIDMaterials(self):
        arsenalToolBox.arsenal_materialIDdeleteAllMat()



    def goRemoveMaterialIDSG(self):
        arsenalToolBox.arsenal_materialIDdeleteAllSG()



    def goAddObjectIDSelection(self):
        arsenalToolBox.arsenal_objectIDaddSelection()



    def goAddObjectIDAll(self):
        arsenalToolBox.arsenal_objectIDaddAllMeshs()



    def goSetObjectIDSelection(self):
        arsenalToolBox.arsenal_objectIDsetSelection()



    def goSetObjectIDAll(self):
        arsenalToolBox.arsenal_objectIDsetAllMeshs()



    def goRemoveObjectIDSelection(self):
        arsenalToolBox.arsenal_objectIDremoveSelection()



    def goRemoveObjectIDAll(self):
        arsenalToolBox.arsenal_objectIDremoveAllMeshs()



    def progressBarUpdate(self, numStep = None, value = None, text = None):
        if numStep is None:
            numStep = 100
        if value is None:
            value = 100
        if text is None:
            text = 'Done'
        self.ui.arsenal_progressBar.setRange(0, numStep)
        self.ui.arsenal_progressBar.setFormat(text)
        self.ui.arsenal_progressBar.setValue(int(value))



    def refresh(self, enterMode = False):
        self.refreshPassListUI()
        self.arsenal.refreshArsenalPass(progressBarUpdate=self.progressBarUpdate)
        self.refreshObjectsUI()
        self.refreshMultimatteMask()
        self.refreshControlUI()
        self.goFastControl()
        self.arsenalQualityUi.goRefresh(enterMode=enterMode)



    def refreshMultimatteMask(self):
        currentWidgetDict = {}
        for i in range(self.ui.arsenal_createNewMultiMatteMask_layout.count()):
            if i == 0:
                continue
            item = self.ui.arsenal_createNewMultiMatteMask_layout.itemAt(i)
            if item is None:
                continue
            widgetToRemove = item.widget()
            if widgetToRemove is None:
                continue
            titleList = widgetToRemove.findChildren(QGroupBox, 'arsenal_multimatteMaskGroupBox')[0].title().split(' | ')
            actualWidgetLayer = titleList[0].split(' : ')[-1]
            actualWidgetNumber = titleList[-1].split(' : ')[-1]
            if actualWidgetLayer in currentWidgetDict:
                tmpDict = currentWidgetDict[actualWidgetLayer]
                tmpDict[actualWidgetNumber] = widgetToRemove
                currentWidgetDict[actualWidgetLayer] = tmpDict
            else:
                currentWidgetDict[actualWidgetLayer] = {actualWidgetNumber: widgetToRemove}

        currentMultiMatte = {}
        for multiMatte in self.multiMatteMaskListUI:
            if multiMatte.passName in currentMultiMatte:
                tmpList = currentMultiMatte[multiMatte.passName]
                tmpList.append(multiMatte.number)
                currentMultiMatte[multiMatte.passName] = tmpList
            else:
                currentMultiMatte[multiMatte.passName] = [multiMatte.number]

        currentPass = self.ui.arsenal_listPass.selectedItems()
        passList = []
        for selec in currentPass:
            passName = str(selec.text())
            passList.append(passName)

        goNotRemoveList = []
        for passName in passList:
            if not pm.objExists(passName):
                continue
            passName = pm.PyNode(passName)
            actualDict = self.arsenal.passName[passName].multimatteMaskName
            if actualDict in ('default', '', ' '):
                actualDict = {}
            for currentWidgetLayer in currentWidgetDict:
                if str(currentWidgetLayer) in passList:
                    for number in currentWidgetDict[currentWidgetLayer]:
                        if int(number) in actualDict.keys():
                            goNotRemoveList.append(currentWidgetLayer)


            for currentWidgetLayer in currentWidgetDict:
                if currentWidgetLayer not in goNotRemoveList:
                    for number in currentWidgetDict[currentWidgetLayer].keys():
                        self.ui.arsenal_createNewMultiMatteMask_layout.removeWidget(currentWidgetDict[currentWidgetLayer][number])
                        currentWidgetDict[currentWidgetLayer][number].destroy()
                        currentWidgetDict[currentWidgetLayer][number].close()
                        for myPass in self.multiMatteMaskListUI:
                            if myPass.number == int(number):
                                self.multiMatteMaskListUI.remove(myPass)



            toNotAddList = []
            for myMask in actualDict:
                if actualDict[myMask] == '':
                    toNotAddList.append(myMask)
                if passName in currentMultiMatte:
                    if myMask in currentMultiMatte[passName]:
                        toNotAddList.append(myMask)
                if passName in currentWidgetDict.keys():
                    if str(myMask) in currentWidgetDict[passName.name()].keys():
                        toNotAddList.append(myMask)

            for myMask in actualDict:
                if myMask not in toNotAddList:
                    self.multiMatteMaskListUI.append(MultimatteMaskUI(parent=self, name=actualDict[myMask], number=myMask, passName=passName, valide=True))





    def refreshObjectsUI(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        passName = str(currentPass[0].text())
        if not pm.objExists(passName):
            return 
        passName = pm.PyNode(passName)
        if self.arsenal.passName[passName].blackHoleMembers:
            self.ui.arsenal_removeBlackHole.setEnabled(True)
            self.ui.arsenal_selectBlackHole.setEnabled(True)
        else:
            self.ui.arsenal_removeBlackHole.setEnabled(False)
            self.ui.arsenal_selectBlackHole.setEnabled(False)
        if self.arsenal.passName[passName].blackHoleMembersReceiveShd:
            self.ui.arsenal_removeBlackHoleReceiveShd.setEnabled(True)
            self.ui.arsenal_selectBlackHoleReceiveShd.setEnabled(True)
        else:
            self.ui.arsenal_removeBlackHoleReceiveShd.setEnabled(False)
            self.ui.arsenal_selectBlackHoleReceiveShd.setEnabled(False)
        if self.arsenal.passName[passName].giMembersGenerate:
            self.ui.arsenal_removeGIGenerateOff.setEnabled(True)
            self.ui.arsenal_selectGIGenerateOff.setEnabled(True)
        else:
            self.ui.arsenal_removeGIGenerateOff.setEnabled(False)
            self.ui.arsenal_selectGIGenerateOff.setEnabled(False)
        if self.arsenal.passName[passName].giMembersReceive:
            self.ui.arsenal_removeGIReceiveOff.setEnabled(True)
            self.ui.arsenal_selectGIReceiveOff.setEnabled(True)
        else:
            self.ui.arsenal_removeGIReceiveOff.setEnabled(False)
            self.ui.arsenal_selectGIReceiveOff.setEnabled(False)
        if self.arsenal.passName[passName].primaryMembersOff:
            self.ui.arsenal_removePrimaryOff.setEnabled(True)
            self.ui.arsenal_selectPrimaryOff.setEnabled(True)
        else:
            self.ui.arsenal_removePrimaryOff.setEnabled(False)
            self.ui.arsenal_selectPrimaryOff.setEnabled(False)
        if self.arsenal.passName[passName].reflectionMembersOff:
            self.ui.arsenal_removeReflectionOff.setEnabled(True)
            self.ui.arsenal_selectReflectionOff.setEnabled(True)
        else:
            self.ui.arsenal_removeReflectionOff.setEnabled(False)
            self.ui.arsenal_selectReflectionOff.setEnabled(False)
        if self.arsenal.passName[passName].refractionMembersOff:
            self.ui.arsenal_removeRefractionOff.setEnabled(True)
            self.ui.arsenal_selectRefractionOff.setEnabled(True)
        else:
            self.ui.arsenal_removeRefractionOff.setEnabled(False)
            self.ui.arsenal_selectRefractionOff.setEnabled(False)
        if self.arsenal.passName[passName].shadowCastsMembersOff:
            self.ui.arsenal_removeShdCastOff.setEnabled(True)
            self.ui.arsenal_selectShdCastOff.setEnabled(True)
        else:
            self.ui.arsenal_removeShdCastOff.setEnabled(False)
            self.ui.arsenal_selectShdCastOff.setEnabled(False)
        if self.arsenal.passName[passName].lightSelectNormalMembers:
            self.ui.arsenal_removeLightSelectNormal.setEnabled(True)
            self.ui.arsenal_selectLightSelectNormal.setEnabled(True)
        else:
            self.ui.arsenal_removeLightSelectNormal.setEnabled(False)
            self.ui.arsenal_selectLightSelectNormal.setEnabled(False)
        if self.arsenal.passName[passName].lightSelectDiffuseMembers:
            self.ui.arsenal_removeLightSelectDiffuse.setEnabled(True)
            self.ui.arsenal_selectLightSelectDiffuse.setEnabled(True)
        else:
            self.ui.arsenal_removeLightSelectDiffuse.setEnabled(False)
            self.ui.arsenal_selectLightSelectDiffuse.setEnabled(False)
        if self.arsenal.passName[passName].lightSelectRawMembers:
            self.ui.arsenal_removeLightSelectRaw.setEnabled(True)
            self.ui.arsenal_selectLightSelectRaw.setEnabled(True)
        else:
            self.ui.arsenal_removeLightSelectRaw.setEnabled(False)
            self.ui.arsenal_selectLightSelectRaw.setEnabled(False)
        if self.arsenal.passName[passName].lightSelectSpecularMembers:
            self.ui.arsenal_removeLightSelectSpecular.setEnabled(True)
            self.ui.arsenal_selectLightSelectSpecular.setEnabled(True)
        else:
            self.ui.arsenal_removeLightSelectSpecular.setEnabled(False)
            self.ui.arsenal_selectLightSelectSpecular.setEnabled(False)



    def refreshControlUI(self):
        currentPass = self.ui.arsenal_listPass.selectedItems()
        passName = str(currentPass[0].text())
        if not pm.objExists(passName):
            return 
        passName = pm.PyNode(passName)
        arsenalPass = passName.name() + '_arsenalPass'
        ajustements = pm.editRenderLayerAdjustment(passName, q=True, layer=True)
        listValue = {}
        if self.arsenal.passName[passName].lightSelectAllNormal:
            listValue[self.ui.arsenal_lightSelectAutoNormal] = ['setChecked(True)', arsenalPass + '.lightSelectAllNormal']
        else:
            listValue[self.ui.arsenal_lightSelectAutoNormal] = ['setChecked(False)', arsenalPass + '.lightSelectAllNormal']
        if self.arsenal.passName[passName].lightSelectAllDiffuse:
            listValue[self.ui.arsenal_lightSelectAutoDiffuse] = ['setChecked(True)', arsenalPass + '.lightSelectAllDiffuse']
        else:
            listValue[self.ui.arsenal_lightSelectAutoDiffuse] = ['setChecked(False)', arsenalPass + '.lightSelectAllDiffuse']
        if self.arsenal.passName[passName].lightSelectAllRaw:
            listValue[self.ui.arsenal_lightSelectAutoRaw] = ['setChecked(True)', arsenalPass + '.lightSelectAllRaw']
        else:
            listValue[self.ui.arsenal_lightSelectAutoRaw] = ['setChecked(False)', arsenalPass + '.lightSelectAllRaw']
        if self.arsenal.passName[passName].lightSelectAllSpecular:
            listValue[self.ui.arsenal_lightSelectAutoSpecular] = ['setChecked(True)', arsenalPass + '.lightSelectAllSpecular']
        else:
            listValue[self.ui.arsenal_lightSelectAutoSpecular] = ['setChecked(False)', arsenalPass + '.lightSelectAllSpecular']
        if self.arsenal.passName[passName].giOn:
            listValue[self.ui.arsenal_FastGI] = ['setChecked(True)', 'vraySettings.giOn']
        else:
            listValue[self.ui.arsenal_FastGI] = ['setChecked(False)', 'vraySettings.giOn']
        if self.arsenal.passName[passName].primaryEngine == 3 and self.arsenal.passName[passName].secondaryEngine == 3 and self.arsenal.passName[passName].imap_detailEnhancement is False:
            listValue[self.ui.arsenal_FastGIType] = ['setCurrentIndex(0)',
             'vraySettings.primaryEngine',
             'vraySettings.secondaryEngine',
             'vraySettings.imap_detailEnhancement']
        elif self.arsenal.passName[passName].primaryEngine == 0 and self.arsenal.passName[passName].secondaryEngine == 3 and self.arsenal.passName[passName].imap_detailEnhancement is False:
            listValue[self.ui.arsenal_FastGIType] = ['setCurrentIndex(1)',
             'vraySettings.primaryEngine',
             'vraySettings.secondaryEngine',
             'vraySettings.imap_detailEnhancement']
        elif self.arsenal.passName[passName].primaryEngine == 0 and self.arsenal.passName[passName].secondaryEngine == 3 and self.arsenal.passName[passName].imap_detailEnhancement is True:
            listValue[self.ui.arsenal_FastGIType] = ['setCurrentIndex(2)',
             'vraySettings.primaryEngine',
             'vraySettings.secondaryEngine',
             'vraySettings.imap_detailEnhancement']
        elif self.arsenal.passName[passName].primaryEngine == 0 and self.arsenal.passName[passName].secondaryEngine == 2 and self.arsenal.passName[passName].imap_detailEnhancement is False:
            listValue[self.ui.arsenal_FastGIType] = ['setCurrentIndex(3)',
             'vraySettings.primaryEngine',
             'vraySettings.secondaryEngine',
             'vraySettings.imap_detailEnhancement']
        elif self.arsenal.passName[passName].primaryEngine == 0 and self.arsenal.passName[passName].secondaryEngine == 2 and self.arsenal.passName[passName].imap_detailEnhancement is True:
            listValue[self.ui.arsenal_FastGIType] = ['setCurrentIndex(4)',
             'vraySettings.primaryEngine',
             'vraySettings.secondaryEngine',
             'vraySettings.imap_detailEnhancement']
        elif self.arsenal.passName[passName].primaryEngine == 2 and self.arsenal.passName[passName].secondaryEngine == 3 and self.arsenal.passName[passName].imap_detailEnhancement is False:
            listValue[self.ui.arsenal_FastGIType] = ['setCurrentIndex(5)',
             'vraySettings.primaryEngine',
             'vraySettings.secondaryEngine',
             'vraySettings.imap_detailEnhancement']
        elif self.arsenal.passName[passName].primaryEngine == 2 and self.arsenal.passName[passName].secondaryEngine == 2 and self.arsenal.passName[passName].imap_detailEnhancement is False:
            listValue[self.ui.arsenal_FastGIType] = ['setCurrentIndex(6)',
             'vraySettings.primaryEngine',
             'vraySettings.secondaryEngine',
             'vraySettings.imap_detailEnhancement']
        else:
            listValue[self.ui.arsenal_FastGIType] = ['setCurrentIndex(7)',
             'vraySettings.primaryEngine',
             'vraySettings.secondaryEngine',
             'vraySettings.imap_detailEnhancement']
        if self.arsenal.passName[passName].aoOn:
            listValue[self.ui.arsenal_FastAO] = ['setChecked(True)', 'vraySettings.aoOn']
        else:
            listValue[self.ui.arsenal_FastAO] = ['setChecked(False)', 'vraySettings.aoOn']
        if self.arsenal.passName[passName].globopt_mtl_glossy:
            listValue[self.ui.arsenal_FastGE] = ['setChecked(True)', 'vraySettings.globopt_mtl_glossy']
        else:
            listValue[self.ui.arsenal_FastGE] = ['setChecked(False)', 'vraySettings.globopt_mtl_glossy']
        if self.arsenal.passName[passName].globopt_mtl_reflectionRefraction:
            listValue[self.ui.arsenal_FastRR] = ['setChecked(True)', 'vraySettings.globopt_mtl_reflectionRefraction']
        else:
            listValue[self.ui.arsenal_FastRR] = ['setChecked(False)', 'vraySettings.globopt_mtl_reflectionRefraction']
        if self.arsenal.passName[passName].globopt_mtl_doMaps:
            listValue[self.ui.arsenal_FastM] = ['setChecked(True)', 'vraySettings.globopt_mtl_doMaps']
        else:
            listValue[self.ui.arsenal_FastM] = ['setChecked(False)', 'vraySettings.globopt_mtl_doMaps']
        if self.arsenal.passName[passName].globopt_light_doShadows:
            listValue[self.ui.arsenal_FastSHD] = ['setChecked(True)', 'vraySettings.globopt_light_doShadows']
        else:
            listValue[self.ui.arsenal_FastSHD] = ['setChecked(False)', 'vraySettings.globopt_light_doShadows']
        if self.arsenal.passName[passName].aaFilterOn:
            listValue[self.ui.arsenal_FastAA] = ['setChecked(True)', 'vraySettings.aaFilterOn']
        else:
            listValue[self.ui.arsenal_FastAA] = ['setChecked(False)', 'vraySettings.aaFilterOn']
        if self.arsenal.passName[passName].globopt_geom_displacement:
            listValue[self.ui.arsenal_FastDSP] = ['setChecked(True)', 'vraySettings.globopt_geom_displacement']
        else:
            listValue[self.ui.arsenal_FastDSP] = ['setChecked(False)', 'vraySettings.globopt_geom_displacement']
        if self.arsenal.passName[passName].cam_mbOn:
            listValue[self.ui.arsenal_FastMB] = ['setChecked(True)', 'vraySettings.cam_mbOn']
        else:
            listValue[self.ui.arsenal_FastMB] = ['setChecked(False)', 'vraySettings.cam_mbOn']
        if self.arsenal.passName[passName].cam_dofOn:
            listValue[self.ui.arsenal_FastDOF] = ['setChecked(True)', 'vraySettings.cam_dofOn']
        else:
            listValue[self.ui.arsenal_FastDOF] = ['setChecked(False)', 'vraySettings.cam_dofOn']
        if self.arsenal.passName[passName].cam_overrideEnvtex:
            listValue[self.ui.arsenal_FastOVENV] = ['setChecked(True)', 'vraySettings.cam_overrideEnvtex']
        else:
            listValue[self.ui.arsenal_FastOVENV] = ['setChecked(False)', 'vraySettings.cam_overrideEnvtex']
        if self.arsenal.passName[passName].vrayLambert:
            listValue[self.ui.arsenal_FastVLambert] = ['setChecked(True)', arsenalPass + '.vrayLambert']
        else:
            listValue[self.ui.arsenal_FastVLambert] = ['setChecked(False)', arsenalPass + '.vrayLambert']
        if self.arsenal.passName[passName].sys_distributed_rendering_on:
            listValue[self.ui.arsenal_FastDR] = ['setChecked(True)', 'vraySettings.sys_distributed_rendering_on']
        else:
            listValue[self.ui.arsenal_FastDR] = ['setChecked(False)', 'vraySettings.sys_distributed_rendering_on']
        if self.arsenal.passName[passName].vrayMaterialID:
            listValue[self.ui.arsenal_FastMaterialID] = ['setChecked(True)', arsenalPass + '.vrayMaterialID']
        else:
            listValue[self.ui.arsenal_FastMaterialID] = ['setChecked(False)', arsenalPass + '.vrayMaterialID']
        if self.arsenal.passName[passName].vrayProxyObjectID:
            listValue[self.ui.arsenal_FastProxyObjectID] = ['setChecked(True)', arsenalPass + '.vrayProxyObjectID']
        else:
            listValue[self.ui.arsenal_FastProxyObjectID] = ['setChecked(False)', arsenalPass + '.vrayProxyObjectID']
        for myUi in listValue:
            cmd = 'myUi.' + listValue[myUi][0]
            exec cmd
            if ajustements is None or listValue[myUi][1] not in ajustements or passName.name() == 'defaultRenderLayer':
                myUi.setStyleSheet('')
            else:
                myUi.setStyleSheet('background-color: rgb(204, 102, 0);\nborder:1px solid rgb(255, 170, 255);\ncolor:rgb(0, 0, 0);')




    def refreshPassListUI(self):
        currentLayer = pm.PyNode(str(pm.editRenderLayerGlobals(query=True, currentRenderLayer=True)))
        self.passList = []
        itemList = {}
        for i in range(self.ui.arsenal_listPass.count()):
            item = self.ui.arsenal_listPass.item(i)
            if not pm.objExists(str(item.text())):
                continue
            PyRenderLayer = pm.PyNode(str(item.text()))
            itemList[PyRenderLayer] = [item, PyRenderLayer.renderable.get()]
            self.passList.append(PyRenderLayer)

        toRemove = list()
        for i in range(self.ui.arsenal_listPass.count()):
            item = self.ui.arsenal_listPass.item(i)
            if not pm.objExists(str(item.text())):
                toRemove.append([item, i])

        for myItem in toRemove:
            items = self.ui.arsenal_listPass.findItems(str(myItem[0].text()), Qt.MatchExactly)
            if len(items):
                index = self.ui.arsenal_listPass.row(items[0])
                self.ui.arsenal_listPass.takeItem(index)

        allLayers = pm.RenderLayer.listAllRenderLayers()
        allIndex = list()
        for i in allLayers:
            allIndex.append(i.displayOrder.get())

        for item in allLayers:
            if item not in itemList:
                tmpWidget = QListWidgetItem(item.name())
                index = allIndex.index(item.displayOrder.get())
                self.ui.arsenal_listPass.insertItem(index, tmpWidget)
                itemList[item] = [tmpWidget, True]

        for item in itemList:
            if itemList[item][1]:
                itemList[item][0].setCheckState(Qt.Checked)
                itemList[item][0].setBackground(QColor(0, 130, 0, 255))
            else:
                itemList[item][0].setCheckState(Qt.Unchecked)
                itemList[item][0].setBackground(QColor(50, 50, 50, 255))

        if not self.ui.arsenal_listPass.selectedItems():
            self.ui.arsenal_listPass.setCurrentRow(0)
        elif str(self.ui.arsenal_listPass.selectedItems()[0].text()) != currentLayer.name():
            self.ui.arsenal_listPass.clearSelection()
            items = self.ui.arsenal_listPass.findItems(currentLayer.name(), Qt.MatchExactly)
            if len(items):
                self.ui.arsenal_listPass.setCurrentItem(items[0])
        if self.ui.arsenal_listPass.count() >= 2:
            self.ui.arsenal_deletePass.setEnabled(True)
        else:
            self.ui.arsenal_deletePass.setEnabled(False)



    def passeNameValid(self, name):
        name = str(name)
        if '.' in name:
            pm.mel.warning('You can not use dot !')
            return False
        else:
            if '-' in name:
                pm.mel.warning('You can not use dash !')
                return False
            if ' ' in name:
                pm.mel.warning('You can not use space !')
                return False
            return True



    def enterEvent(self, event):
        if self.arsenal.initialize():
            self.refresh(enterMode=True)



    def showEvent(self, event):
        try:
            conf = open(self.dir + 'arsenal.cfg', 'r')
            confContent = conf.readlines()
            conf.close()
            for var in confContent:
                exec var

            self.move(poz)
        except:
            pass
        if self.arsenal.initialize():
            self.refresh()



    def closeEvent(self, event):
        conf = open(self.dir + 'arsenal.cfg', 'w')
        conf.writelines(('poz = ' + str(self.pos())).replace('PyQt4.QtCore.', ''))
        conf.close()




class ArsenalQualityUi(object):

    def __init__(self, parent = None):
        self.parent = parent
        self.arsenalQualityTool = ArsenalQualityTool(self)
        self.parent.ui.arsenal_qualitySaveSetting.clicked.connect(self.goSaveSetting)
        self.parent.ui.arsenal_qualityOptimize.clicked.connect(self.goOptimize)
        self.parent.ui.arsenal_qualityBackSetting.clicked.connect(self.goBackSetting)
        self.parent.ui.arsenal_qualityPresets.activated.connect(self.goChangePresetType)
        self.parent.ui.arsenal_qualitySlider.valueChanged.connect(self.goChangeSlider)
        self.parent.ui.arsenal_qualityOptimizeMat.clicked.connect(self.goOptimizeMat)
        self.parent.ui.arsenal_qualityOptimizeLights.clicked.connect(self.goOptimizeLights)
        self.parent.ui.arsenal_qualityOptimizationChooserGlobalOption.toggled[bool].connect(self.goChangeOffsetGlobalOption)
        self.parent.ui.arsenal_qualityOptimizationChooserGlobalOptionValue.valueChanged[int].connect(self.goChangeOffsetGlobalOption)
        self.parent.ui.arsenal_qualityOptimizationChooserIrradianceMap.toggled[bool].connect(self.goChangeOffsetIrradianceMap)
        self.parent.ui.arsenal_qualityOptimizationChooserIrradianceMapValue.valueChanged[int].connect(self.goChangeOffsetIrradianceMap)
        self.parent.ui.arsenal_qualityOptimizationChooserImageSampler.toggled[bool].connect(self.goChangeOffsetImageSampler)
        self.parent.ui.arsenal_qualityOptimizationChooserImageSamplerValue.valueChanged[int].connect(self.goChangeOffsetImageSampler)
        self.parent.ui.arsenal_qualityOptimizationChooserLightCache.toggled[bool].connect(self.goChangeOffsetLightCache)
        self.parent.ui.arsenal_qualityOptimizationChooserLightCacheValue.valueChanged[int].connect(self.goChangeOffsetLightCache)
        self.parent.ui.arsenal_qualityOptimizationChooserDMCSampler.toggled[bool].connect(self.goChangeOffsetDMCSampler)
        self.parent.ui.arsenal_qualityOptimizationChooserDMCSamplerValue.valueChanged[int].connect(self.goChangeOffsetDMCSampler)
        self.parent.ui.arsenal_qualityOptimizationChooserSystem.toggled[bool].connect(self.goChangeOffsetSystem)
        self.parent.ui.arsenal_qualityOptimizationChooserSystemValue.valueChanged[int].connect(self.goChangeOffsetSystem)
        self.parent.ui.arsenal_qualityLCDGlobal_optionTxt.setVisible(False)
        self.parent.ui.arsenal_qualityLCDGlobal_optionLCDFrame.setVisible(False)
        self.parent.ui.arsenal_qualityLCDIrradianceMapTxt.setVisible(False)
        self.parent.ui.arsenal_qualityLCDIrradianceMapLCDFrame.setVisible(False)
        self.parent.ui.arsenal_qualityLCDImageSamplerTxt.setVisible(False)
        self.parent.ui.arsenal_qualityLCDImageSamplerLCDFrame.setVisible(False)
        self.parent.ui.arsenal_qualityLCDLightCacheTxt.setVisible(False)
        self.parent.ui.arsenal_qualityLCDLightCacheLCDFrame.setVisible(False)
        self.parent.ui.arsenal_qualityLCDDMCSamplerTxt.setVisible(False)
        self.parent.ui.arsenal_qualityLCDDMCSamplerLCDFrame.setVisible(False)
        self.parent.ui.arsenal_qualityLCDSystemTxt.setVisible(False)
        self.parent.ui.arsenal_qualityLCDSystemLCDFrame.setVisible(False)



    def goSaveSetting(self):
        self.arsenalQualityTool.saveSetting()
        self.refreshQualityUI()



    def goOptimize(self):
        self.arsenalQualityTool.optimize()
        self.goRefresh()



    def goBackSetting(self):
        self.arsenalQualityTool.backSetting()
        self.goRefresh()



    def goOptimizeMat(self):
        minValue = self.parent.ui.arsenal_qualityOptimizeMat_min.value()
        maxValue = self.parent.ui.arsenal_qualityOptimizeMat_max.value()
        layerMode = self.parent.ui.arsenal_qualityOptimizeMat_layer.checkState()
        self.arsenalQualityTool.optimizeMat(layerMode=layerMode, minSub=minValue, maxSubd=maxValue)



    def goOptimizeLights(self):
        self.arsenalQualityTool.optimizeLights()



    def goChangeSlider(self):
        value = self.parent.ui.arsenal_qualitySlider.value()
        self.arsenalQualityTool.setValue(attribute='deeXVrayFastLastQuality', value=value, node='vraySettings')
        self.goRefresh()



    def goChangePresetType(self):
        value = str(self.parent.ui.arsenal_qualityPresets.currentText())
        self.arsenalQualityTool.setValue(attribute='deeXVrayFastLastTypePreset', value=value, node='vraySettings')
        self.goRefresh()



    def goChangeOffsetGlobalOption(self):
        value = self.parent.ui.arsenal_qualityOptimizationChooserGlobalOptionValue.value()
        activated = self.parent.ui.arsenal_qualityOptimizationChooserGlobalOption.isChecked()
        self.arsenalQualityTool.optimizationChooserChange(value=value, attribute='OptimizationChooserGlobalOptionInt', enabled=activated)
        self.parent.changeValue()



    def goChangeOffsetIrradianceMap(self):
        value = self.parent.ui.arsenal_qualityOptimizationChooserIrradianceMapValue.value()
        activated = self.parent.ui.arsenal_qualityOptimizationChooserIrradianceMap.isChecked()
        self.arsenalQualityTool.optimizationChooserChange(value=value, attribute='OptimizationChooserIrradianceMapInt', enabled=activated)
        self.parent.changeValue()



    def goChangeOffsetImageSampler(self):
        value = self.parent.ui.arsenal_qualityOptimizationChooserImageSamplerValue.value()
        activated = self.parent.ui.arsenal_qualityOptimizationChooserImageSampler.isChecked()
        self.arsenalQualityTool.optimizationChooserChange(value=value, attribute='OptimizationChooserImageSamplerInt', enabled=activated)
        self.parent.changeValue()



    def goChangeOffsetLightCache(self):
        value = self.parent.ui.arsenal_qualityOptimizationChooserLightCacheValue.value()
        activated = self.parent.ui.arsenal_qualityOptimizationChooserLightCache.isChecked()
        self.arsenalQualityTool.optimizationChooserChange(value=value, attribute='OptimizationChooserLightCacheInt', enabled=activated)
        self.parent.changeValue()



    def goChangeOffsetDMCSampler(self):
        value = self.parent.ui.arsenal_qualityOptimizationChooserDMCSamplerValue.value()
        activated = self.parent.ui.arsenal_qualityOptimizationChooserDMCSampler.isChecked()
        self.arsenalQualityTool.optimizationChooserChange(value=value, attribute='OptimizationChooserDMCSamplerInt', enabled=activated)
        self.parent.changeValue()



    def goChangeOffsetSystem(self):
        value = self.parent.ui.arsenal_qualityOptimizationChooserSystemValue.value()
        activated = self.parent.ui.arsenal_qualityOptimizationChooserSystem.isChecked()
        self.arsenalQualityTool.optimizationChooserChange(value=value, attribute='OptimizationChooserSystemInt', enabled=activated)
        self.parent.changeValue()



    def goRefresh(self, enterMode = False):
        if not enterMode:
            self.arsenalQualityTool.initAttributes()
            self.arsenalQualityTool.refresh()
            self.refreshQualityUI()



    def refreshQualityUI(self):
        if not pm.attributeQuery('deeXVrayFastActualSettings', n='vraySettings', ex=True) and not pm.attributeQuery('deeXVrayFastOptimized', n='vraySettings', ex=True):
            self.parent.ui.arsenal_qualitySaveSetting.setEnabled(True)
            self.parent.ui.arsenal_qualityOptimize.setEnabled(False)
            self.parent.ui.arsenal_qualityBackSetting.setEnabled(False)
            self.parent.ui.arsenal_qualityFrame.setEnabled(False)
            self.parent.ui.arsenal_qualityOptimizeMat.setEnabled(False)
            self.parent.ui.arsenal_qualityOptimizeLights.setEnabled(False)
            return 
        if pm.attributeQuery('deeXVrayFastActualSettings', n='vraySettings', ex=True) and not pm.attributeQuery('deeXVrayFastOptimized', n='vraySettings', ex=True):
            self.parent.ui.arsenal_qualitySaveSetting.setEnabled(False)
            self.parent.ui.arsenal_qualityOptimize.setEnabled(True)
            self.parent.ui.arsenal_qualityBackSetting.setEnabled(False)
            self.parent.ui.arsenal_qualityFrame.setEnabled(False)
            self.parent.ui.arsenal_qualityOptimizeMat.setEnabled(False)
            self.parent.ui.arsenal_qualityOptimizeLights.setEnabled(False)
            return 
        if pm.attributeQuery('deeXVrayFastActualSettings', n='vraySettings', ex=True) and pm.attributeQuery('deeXVrayFastOptimized', n='vraySettings', ex=True):
            self.parent.ui.arsenal_qualitySaveSetting.setEnabled(False)
            self.parent.ui.arsenal_qualityOptimize.setEnabled(True)
            self.parent.ui.arsenal_qualityBackSetting.setEnabled(True)
            self.parent.ui.arsenal_qualityFrame.setEnabled(True)
            self.parent.ui.arsenal_qualityOptimizeMat.setEnabled(True)
            self.parent.ui.arsenal_qualityOptimizeLights.setEnabled(True)
        self.parent.ui.arsenal_qualitySlider.setValue(self.arsenalQualityTool.deeXVrayFastLastQuality)
        self.parent.ui.arsenal_qualityPresets.clear()
        listPreset = self.arsenalQualityTool.listFile(dir=self.parent.dir + 'presets/', start='deeXVrayFastPresetType_', end='.txt')
        for myPreset in listPreset:
            presetName = myPreset.split('deeXVrayFastPresetType_')[-1][:-4]
            self.parent.ui.arsenal_qualityPresets.addItem(presetName)

        self.parent.ui.arsenal_qualityPresets.setCurrentIndex(self.parent.ui.arsenal_qualityPresets.findText(self.arsenalQualityTool.deeXVrayFastLastTypePreset))
        if self.arsenalQualityTool.presetComment is not None or self.arsenalQualityTool.presetComment != '':
            self.parent.ui.arsenal_qualityPresetComment.setPlainText(self.arsenalQualityTool.presetComment)
        else:
            self.parent.ui.arsenal_qualityPresetComment.setPlainText('No comment')
        lines = pm.getAttr('vraySettings.deeXVrayFastoptimizationChooserSettings')
        dicoOptimizationChooser = eval(lines)
        self.parent.ui.arsenal_qualityOptimizationChooserGlobalOption.setChecked(dicoOptimizationChooser['OptimizationChooserGlobalOptionInt'][0])
        self.parent.ui.arsenal_qualityOptimizationChooserGlobalOptionValue.setValue(dicoOptimizationChooser['OptimizationChooserGlobalOptionInt'][1])
        self.parent.ui.arsenal_qualityOptimizationChooserIrradianceMap.setChecked(dicoOptimizationChooser['OptimizationChooserIrradianceMapInt'][0])
        self.parent.ui.arsenal_qualityOptimizationChooserIrradianceMapValue.setValue(dicoOptimizationChooser['OptimizationChooserIrradianceMapInt'][1])
        self.parent.ui.arsenal_qualityOptimizationChooserImageSampler.setChecked(dicoOptimizationChooser['OptimizationChooserImageSamplerInt'][0])
        self.parent.ui.arsenal_qualityOptimizationChooserImageSamplerValue.setValue(dicoOptimizationChooser['OptimizationChooserImageSamplerInt'][1])
        self.parent.ui.arsenal_qualityOptimizationChooserLightCache.setChecked(dicoOptimizationChooser['OptimizationChooserLightCacheInt'][0])
        self.parent.ui.arsenal_qualityOptimizationChooserLightCacheValue.setValue(dicoOptimizationChooser['OptimizationChooserLightCacheInt'][1])
        self.parent.ui.arsenal_qualityOptimizationChooserDMCSampler.setChecked(dicoOptimizationChooser['OptimizationChooserDMCSamplerInt'][0])
        self.parent.ui.arsenal_qualityOptimizationChooserDMCSamplerValue.setValue(dicoOptimizationChooser['OptimizationChooserDMCSamplerInt'][1])
        self.parent.ui.arsenal_qualityOptimizationChooserSystem.setChecked(dicoOptimizationChooser['OptimizationChooserSystemInt'][0])
        self.parent.ui.arsenal_qualityOptimizationChooserSystemValue.setValue(dicoOptimizationChooser['OptimizationChooserSystemInt'][1])




def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QWidget)



def show():
    global arsenalUI
    if pm.optionVar['arsenal_UI']:
        print 'Show arsenal UI'
        arsenalUI.show()
    elif int(pm.about(v=1).split(' ')[0]) < 2011:
        print 'Initialize pumpThread for mayaVersion < 2011'
        import pumpThread as pt
        pt.initializePumpThread()
    print 'Create arsenal UI'
    arsenalUI = ArsenalUI(getMayaWindow())
    if arsenalUI.arsenal.initialize():
        arsenalUI.show()
        pm.optionVar['arsenal_UI'] = True
    arsenalUI.setWindowTitle('DeeX VRay Arsenal v%s' % arsenalUI.version)



def devReload():
    import py_compile
    listFile = []
    for (path, subdirs, files,) in os.walk('C:\\Users\\BigbossFr\\workspace\\arsenal'):
        if 'plugin' not in path:
            for name in files:
                if name[-3:] == '.py':
                    listFile.append(os.path.join(path, name))


    for i in listFile:
        py_compile.compile(i)
        lastPath = i.split('\\arsenal\\')[-1]
        lastDirTmp = os.path.dirname(lastPath)
        if lastDirTmp:
            lastDir = '\\' + lastDirTmp
        else:
            lastDir = ''
        print i + 'c'




