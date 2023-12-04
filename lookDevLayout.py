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

        if networkMaterial.getType() == 'NetworkMaterialCreate':
            terminal = networkMaterial.getNetworkMaterials()[0]
            terminalIn = terminal.getInputPort(terminalInput)
        elif networkMaterial.getType() == 'NetworkMaterial':
            terminalIn = networkMaterial.addInputPort(terminalInput)
        
        shadingNodeOut = shadingNode.getOutputPort('outColor')
        terminalIn.connect(shadingNodeOut)

        print(networkMaterial.getParameter('NodeType') == 'NetworkMaterialCreate')


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
    
    def subDivideMesh(self, meshToSubdivide, parent):
        attributeSet = NodegraphAPI.CreateNode('AttributeSet', parent)
        meshLocation = meshToSubdivide.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        path = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('paths.i0'))
        path.setValue(meshLocation)

        attributeName = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('attributeName'))
        attributeName.setValue('Type')

        attributeType = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('attributeType'))
        attributeType.setValue('string')

        subdivideMesh = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('stringValue.i0'))
        subdivideMesh.setValue('subdmesh')

        return attributeSet


    

    def generateScene(self):

        if self.enableGrey.isChecked() or self.enableChrome.isChecked() or self.enableChart.isChecked() or self.enableAll.isChecked() == True:
            nmc = NodegraphAPI.CreateNode('NetworkMaterialCreate', self.root)
            nmcTerminal = self.getMaterialPath(nmc)
        
        # creating the setup for the grey shaderball
        if self.enableGrey.isChecked() == True:
            greySphere = self.geoCreate('poly sphere', self.root)
            greyRename = greySphere.getParameter('name').setValue('/root/world/geo/greySphere', 0)
            greySphereLocation = greySphere.getParameterValue('name', NodegraphAPI.GetCurrentTime())

            subDMesh = self.subDivideMesh(greySphere, self.root)

            sphereIntoAttributes = self.connectTwoNodes(greySphere, subDMesh, 'out', 'A')

            greyMat = self.shadingNodeCreate('dlPrincipled', nmc)
            greyMatBase = UI4.FormMaster.CreateParameterPolicy(None, greyMat.getParameter('parameters.color'))
            greyMatBase.setValue([0.18,
                                  0.18,
                                  0.18])
            
            greyRoughness = UI4.FormMaster.CreateParameterPolicy(None, greyMat.getParameter('parameters.roughness')).setValue(0)

            greyNmcConnect = self.nmcConnect(nmc, greyMat, 'dlSurface')
        
            greyMerge = self.multiMerge([subDMesh, nmc], self.root)
            greyMatAssign = self.materialAssignSetup(greySphereLocation, nmcTerminal, self.root)
            greyMergeToAssign = self.connectTwoNodes(greyMerge, greyMatAssign, 'out', 'input')

        # creating the setup for the chrome shaderball
        if self.enableChrome.isChecked() == True:
            
            chromeSphere = self.geoCreate('poly sphere', self.root)
            chromeRename = chromeSphere.getParameter('name').setValue('/root/world/geo/chromeSphere', 0)
            chromeLocation = chromeSphere.getParameterValue('name', NodegraphAPI.GetCurrentTime())

            chromeSubD = self.subDivideMesh(chromeSphere, self.root)

            setChromeAttributes = self.connectTwoNodes(chromeSphere, chromeSubD, 'out', 'A')

            if self.enableGrey.isChecked() == True:
                chromeNM = NodegraphAPI.CreateNode('NetworkMaterial', nmc)
                chromeLocation = '/root/materials/NetworkMaterial1'
            
            chromeMat = self.shadingNodeCreate('dlPrincipled', nmc)

            chromeMatBase = UI4.FormMaster.CreateParameterPolicy(None, chromeMat.getParameter('parameters.color'))
            chromeMatBase.setValue([1,
                                    1,
                                    1])
            chromeRoughness = UI4.FormMaster.CreateParameterPolicy(None, chromeMat.getParameter('parameters.roughness')).setValue(0)
            chromeMetallic = UI4.FormMaster.CreateParameterPolicy(None, chromeMat.getParameter('parameters.metallic')).setValue(1)


            if self.enableGrey.isChecked() == True:
                # if there's more than one material in the NMC
                chromeConnect = self.nmcConnect(chromeNM, chromeMat, 'dlSurface')
            else:
                # if the chrome ball is the only material in the NMC
                chromeConnect = self.nmcConnect(nmc, chromeMat, 'dlSurface')

            if self.enableGrey.isChecked() != True:
                chromeMerge = self.multiMerge([chromeSubD, nmc], self.root)
                chromeMatAssign = self.materialAssignSetup(chromeLocation, '/root/materials/NetworkMaterial1', self.root)
                chromMatConnect = self.connectTwoNodes(chromeMerge, chromeMatAssign, 'out', 'input')
            elif self.enableGrey.isChecked() and self.enableChrome.isChecked():
                primGroup = self.groupNodeSetup(self.root)

                greySphere.setParent(primGroup)
                subDMesh.setParent(primGroup)

                chromeSphere.setParent(primGroup)
                chromeSubD.setParent(primGroup)
                
                nmc.setParent(primGroup)

                greyMerge.setParent(primGroup)
                chromeMerge = greyMerge.addInputPort('i2')
                chromeOut = chromeSubD.getOutputPort('out')

                chromeOut.connect(chromeMerge)

                nmcOut = greyMerge.getOutputPort('out')
                groupReturn = primGroup.getReturnPort('groupOut')

                nmcOut.connect(groupReturn)

                groupOut = self.connectTwoNodes(primGroup, greyMatAssign, 'groupOut', 'input')


'''
        elif self.enableGrey.isChecked() and self.enableChrome.isChecked():
            primGroup = self.groupNodeSetup(self.root)
            matStackCreate = NodegraphAPI.CreateNode('GroupStack', root).setName('MaterialAssign Stack')
            '''


lookDevWindow = LookDevelopmentEnvironment()