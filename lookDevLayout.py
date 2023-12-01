import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class LookDevelopmentEnvironment(QWidget):
    def __init__(self):
        super().__init__()
        self.root = NodegraphAPI.GetRootNode()
        self.createUI()

    def createWindow(self):

        self.setGeometry(150, 150, 200, 250)
        self.setWindowTitle('Look development Window')

        self.createUI()
        self.show()
    
    def createUI(self):

        layout = QGridLayout()

        lookdevHeading = QLabel("Look Development Assets")

        backgrounds = QLabel("Backgrounds")

        self.enablePlatform = QCheckBox("Enable Platform")
        self.enableFlatBG = QCheckBox("Enable Flat Background")
        self.enableDomeBG = QCheckBox("Enable Round Background")

        lookdevTools = QLabel("LookDev Tools")

        self.enableGrey = QCheckBox("Enable Grey Ball")
        self.enableChrome = QCheckBox("Enable Chrome Ball")
        self.enableChart = QCheckBox("Enable Macbeth Chart")
        self.enableAll = QCheckBox("Enable All")

        self.createLookdev = QPushButton("Create")
        self.createLookdev.clicked.connect(self.generateScene)

        layout.addWidget(lookdevHeading, 0, 0)
        layout.addWidget(backgrounds, 1, 0)
        layout.addWidget(self.enablePlatform, 2, 0)
        layout.addWidget(self.enableFlatBG, 2, 1)
        layout.addWidget(self.enableDomeBG, 2, 3)
        layout.addWidget(lookdevTools, 3, 0)
        layout.addWidget(self.enableGrey, 4, 0)
        layout.addWidget(self.enableChrome, 4, 1)
        layout.addWidget(self.enableChart, 4, 2)
        layout.addWidget(self.enableAll, 4, 3)
        layout.addWidget(self.createLookdev, 5, 0, 1, 4)

        self.show()
        self.setLayout(layout)

    def geoCreate(self, primitiveType, parent):
        primitiveCreate = NodegraphAPI.CreateNode('PrimitiveCreate', parent)
        changePrimType = UI4.FormMaster.CreateParameterPolicy(None, primitiveCreate.getParameter('type'))
        changePrimType.setValue(primitiveType, 0)

        return primitiveCreate

    def shadingNodeCreate(self, nodeType, parent, dlShadingNodeType = 'DlShadingNode'):
        dlPrincipled = NodegraphAPI.CreateNode(dlShadingNodeType, parent)
        dlPrincipled.getParameter('nodeType').setValue(nodeType, 0)
        dlPrincipled.getParameter('name').setValue(nodeType, 0)
        dlPrincipled.checkDynamicParameters()
        return dlPrincipled


    def materialAssignSetup(self, assetLocation, material, parent):
        
        materialAssign = NodegraphAPI.CreateNode('MaterialAssign', parent)
        materialAssign.getParameter('CEL').setValue(assetLocation, 0)
        materialAssign.getParameter('args.materialAssign.enable').setValue(1, 0)
        materialAssign.getParameter('args.materialAssign.value').setValue(material, 0)

        return materialAssign


    def groupNodeSetup(self, parent):
        group = NodegraphAPI.CreateNode('Group', parent)
        group.addOutputPort('groupOut')
        groupReturn = group.getReturnPort('out')

        return group


    # ---------------------------------------------------------------------------------------------------
    # ------------------------------ Functions for connecting nodes together ----------------------------
    # ---------------------------------------------------------------------------------------------------

    def nmcConnect(self, networkMaterial, shadingNode, terminalInput):
        terminal = networkMaterial.getNetworkMaterials()[0]

        terminalOut = terminal.getInputPort(terminalInput)
        shadingNodeOut = shadingNode.getOutputPort('outColor')

        terminalOut.connect(shadingNodeOut)


    def connectTwoNodes(self, nodeOutput, nodeInput, outValue, inValue):

        nodeOutPort = nodeOutput.getOutputPort(outValue)
        nodeInPort = nodeInput.getInputPort(inValue)

        nodeOutPort.connect(nodeInPort)

    def multiMerge (self, nodesToMerge, parent):
        mergeNode = NodegraphAPI.CreateNode('Merge', parent)

        for node in nodesToMerge:
            outputPort = node.getOutputPort('out')
            mergeInput = mergeNode.addInputPort('i')
            outputPort.connect(mergeInput)
        return mergeNode

    # ---------------------------------------------------------------------------------------------------
    # --------------------------------- Additional helpful functions ------------------------------------
    # ---------------------------------------------------------------------------------------------------

    def getMaterialPath(self, nmc):

        nmcRootLocation = nmc.getParameterValue('rootLocation', NodegraphAPI.GetCurrentTime())
        
        material = nmc.getNetworkMaterials()[-1]
        materialName = material.getParameterValue('name', NodegraphAPI.GetCurrentTime())

        materialPath = nmcRootLocation + "/" + materialName

        return materialPath
    
    def subDivideMesh(self, meshToSubdivide):
        
    

    def generateScene(self):

        nmc = NodegraphAPI.CreateNode('NetworkMaterialCreate', self.root)
        nmcTerminal = self.getMaterialPath(nmc)
        

        if self.enableGrey.isChecked() == True:
            greySphere = self.geoCreate('poly sphere', self.root)
            greyRename = greySphere.getParameter('name').setValue('/root/world/geo/greySphere', 0)
            greySphereLocation = greySphere.getParameterValue('name', NodegraphAPI.GetCurrentTime())

            greyMat = self.shadingNodeCreate('dlPrincipled', nmc)
            greyMatBase = UI4.FormMaster.CreateParameterPolicy(None, greyMat.getParameter('parameters.color'))
            greyMatBase.setValue([0.18,
                                  0.18,
                                  0.18])
            
            greyRoughness = UI4.FormMaster.CreateParameterPolicy(None, greyMat.getParameter('parameters.roughness')).setValue(0)

            greyNmcConnect = self.nmcConnect(nmc, greyMat, 'dlSurface')

            greyMerge = self.multiMerge([greySphere, nmc], self.root)

            greyMatAssign = self.materialAssignSetup(greySphereLocation, nmcTerminal, self.root)

            greyMergeToAssign = self.connectTwoNodes(greyMerge, greyMatAssign, 'out', 'input')
            






lookDevWindow = LookDevelopmentEnvironment()