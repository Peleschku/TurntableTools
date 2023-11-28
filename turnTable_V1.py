import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class TurntableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.root = NodegraphAPI.GetRootNode()
        self.createWindow()
    
    def createWindow(self):

        self.setGeometry(150, 150, 200, 250)
        self.setWindowTitle('Please work')

        self.populateUI()
        self.show()
    
    def populateUI(self):

        layout = QGridLayout()

        assetLabel = QLabel("Path to Asset")
        self.assetPath = QLineEdit()
        
        # button that opens the file browser. Once a .abc file is specificed
        # the file path is added to self.assetPath()

        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.assetBrowser)

        # create camera is checkbox is checked

        cameraHeader = QLabel("Camera Settings")
        self.createCamera = QCheckBox("Create Camera?")
        updateCamRes = QLabel("Resolution")
        self.cameraResSelect = UI4.Widgets.ResolutionComboBox(self)

        # HDRI setup

        self.skydomeSetup = SkydomeSetup()

        
        # button that assembles the turn table when clicked

        self.createTurnTable = QPushButton("Create Turn Table")
        self.createTurnTable.clicked.connect(self.generateTT)

        layout.addWidget(assetLabel, 0, 0)
        layout.addWidget(self.assetPath, 0, 1, 1, 4)
        layout.addWidget(self.searchButton, 0, 5)
        layout.addWidget(cameraHeader, 1, 0)
        layout.addWidget(self.createCamera, 2, 0)
        layout.addWidget(updateCamRes, 3, 0)
        layout.addWidget(self.cameraResSelect, 3, 1, 1, 4)
        layout.addWidget(self.skydomeSetup, 4, 0, 1, 5)       
        layout.addWidget(self.createTurnTable, 5, 0, 1, 5)

        self.show()
        self.setLayout(layout)

    def assetBrowser(self):
        
        # means the file browser only reads alembic files
        filter = "alembic (*.abc)"
        
        self.filePath = QFileDialog.getOpenFileName(self, "Select Asset", "", filter)

        if self.filePath:
            self.assetPath.insert(self.filePath[0])
    
    def multiMerge (self, nodesToMerge):
        mergeNode = NodegraphAPI.CreateNode('Merge', self.root)

        for node in nodesToMerge:

            # grabbing the output ports of the nodes made outside of the function
            outputPort = node.getOutputPort('out')

            #adding input ports to the merge node  based on how many nodes were created
            mergeInput = mergeNode.addInputPort('i')

            #connecting the nodes
            outputPort.connect(mergeInput)
        
        return mergeNode
    
    def generateTT(self):

        alembicCreate = NodegraphAPI.CreateNode('Alembic_In', self.root)
        assetSet = UI4.FormMaster.CreateParameterPolicy(None, alembicCreate.getParameter('abcAsset'))
        assetSet.setValue(str(self.assetPath.text()))

        if self.createCamera.isChecked():
            camera = NodegraphAPI.CreateNode('CameraCreate', self.root)
        
        camTranslate = UI4.FormMaster.CreateParameterPolicy(None, camera.getParameter('transform.translate'))
        camTranslate.setValue([0.0,
                               0.6,
                               1.6], 1)
        

        camAssetMerge = self.multiMerge([alembicCreate, camera])
        camMergeOut = camAssetMerge.getOutputPort('out')

        # if the 'use skydome' check box is checked, create a skydome
        # note to self: the line in the if statement is calling a function
        # from within the SkydomeSetup class
        
        if self.skydomeSetup.useSkydome.isChecked():
            skydome = SkydomeSetup.createSkydome(self)

        skydomeInput = skydome.getInputPort('in')
        skydomeOutput = skydome.getOutputPort('out')

        camMergeOut.connect(skydomeInput)

        # creates render settings node and assigns the camera resolution
        # based on the selection in the UI's dropdown

        renderSettings = NodegraphAPI.CreateNode('RenderSettings', self.root)
        resolution = UI4.FormMaster.CreateParameterPolicy(None, renderSettings.getParameter('args.renderSettings.resolution'))
        resolution.setValue(str(self.cameraResSelect.currentText()))

        renderInput = renderSettings.getInputPort('input')
        skydomeOutput.connect(renderInput)

class SkydomeSetup(QWidget):
    def __init__(self):
        super().__init__()
        self.parentLayout = QGridLayout()
        self.root = NodegraphAPI.GetRootNode()
        self.createModule()
    
    def createModule(self):
        skydomeHeader = QLabel("Skydome Setup")
        useTexture = QCheckBox("Use HDRI Texture?")

        texturePathLabel = QLabel("Path to Texture")
        self.texturePath = QLineEdit()
        self.searchTexture = QPushButton("Search")
        self.searchTexture.clicked.connect(self.textureBrowser)


       
        self.useSkydome = QCheckBox("Use Skydome Setup")

        self.parentLayout.addWidget(skydomeHeader, 0, 0)
        self.parentLayout.addWidget(useTexture, 1, 0)
        self.parentLayout.addWidget(texturePathLabel, 2, 0)
        self.parentLayout.addWidget(self.texturePath, 2, 1, 1, 4)
        self.parentLayout.addWidget(self.searchTexture, 2, 5)
        self.parentLayout.addWidget(self.useSkydome, 3, 5)

        self.show()
        self.setLayout(self.parentLayout)
    
    def createSkydome(self):
        gafferThree = NodegraphAPI.CreateNode("GafferThree", self.root)
        rootPackage = gafferThree.getRootPackage()
        rootPackage.createChildPackage('EnvironmentLightPackage', 'envLight')

        light = rootPackage.getChildPackage('envLight')
        lightMatNode = light.getMaterialNode()
        lightShader = lightMatNode.addShaderType('dlEnvironmentShader')

        setEnvLight = UI4.FormMaster.CreateParameterPolicy(None, lightMatNode.getParameter('shaders.dlEnvironmentShader'))
        setEnvLight.setValue("environmentLight")
        lightMatNode.checkDynamicParameters()

        return gafferThree
    
    def textureBrowser(self):
                
        self.filePath = QFileDialog.getOpenFileName(self, "Select Asset",)

        if self.filePath:
            self.texturePath.insert(self.filePath[0])




turnTable = TurntableWindow()