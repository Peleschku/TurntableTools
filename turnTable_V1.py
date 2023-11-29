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

        self.cameraSetup = CameraSettings()

        # HDRI setup

        self.skydomeSetup = SkydomeSetup()

        
        # button that assembles the turn table when clicked

        self.createTurnTable = QPushButton("Create Turn Table")
        self.createTurnTable.clicked.connect(self.generateTT)

        layout.addWidget(assetLabel, 0, 0)
        layout.addWidget(self.assetPath, 0, 1, 1, 3)
        layout.addWidget(self.searchButton, 0, 4)
        layout.addWidget(self.cameraSetup, 1, 0, 1, 5)
        layout.addWidget(self.skydomeSetup, 2, 0, 1, 5)       
        layout.addWidget(self.createTurnTable, 3, 0, 1, 5)

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
    
    def dollyConstraintCreate(self, cameraPath, assetPath, offsetAmount):
        dollyConstraint = NodegraphAPI.CreateNode('DollyConstraint', self.root)

        dollyBasePath = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('basePath'))
        dollyBasePath.setValue(cameraPath)
        
        dollyTargetPath = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('targetPath.i0'))
        dollyTargetPath.setValue(assetPath)

        dollyTargetBounds = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('targetBounds'))
        dollyTargetBounds.setValue('sphere')

        dollyOffsetAngle = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('angleOffset'))
        dollyOffsetAngle.setValue(offsetAmount)

        return dollyConstraint

    
    def generateTT(self):

        alembicCreate = NodegraphAPI.CreateNode('Alembic_In', self.root)
        assetSet = UI4.FormMaster.CreateParameterPolicy(None, alembicCreate.getParameter('abcAsset'))
        assetSet.setValue(str(self.assetPath.text()))

        assetLocation = alembicCreate.getParameterValue('name', NodegraphAPI.GetCurrentTime())

        camera = NodegraphAPI.CreateNode('CameraCreate', self.root)
        
        
        cameraFOV = UI4.FormMaster.CreateParameterPolicy(None, camera.getParameter('fov'))
        if self.cameraSetup.FOVValue.text() != "70":
            cameraFOV.setValue(int(self.cameraSetup.FOVValue.text()))


        makeInteractive = UI4.FormMaster.CreateParameterPolicy(None, camera.getParameter('makeInteractive'))

        if self.cameraSetup.makeCamInteractive.setCheckable(False):
            makeInteractive.setValue('No')
        else:
            makeInteractive.setValue('Yes')
        
        camLocation = camera.getParameterValue('name', NodegraphAPI.GetCurrentTime())

        camAssetMerge = self.multiMerge([alembicCreate, camera])
        camMergeOut = camAssetMerge.getOutputPort('out')

        # creates the dolly constraint that snaps the camera to the Asset

        dollyConstraint = self.dollyConstraintCreate(camLocation, assetLocation, -30)
        dollyInputPort = dollyConstraint.getInputPort('input')
        dollyOutputPort = dollyConstraint.getOutputPort('out')

        camMergeOut.connect(dollyInputPort)

        # creates render settings node and assigns the camera resolution
        # based on the selection in the UI's dropdown

        renderSettings = NodegraphAPI.CreateNode('RenderSettings', self.root)

        camResolution = UI4.FormMaster.CreateParameterPolicy(None, renderSettings.getParameter('args.renderSettings.resolution'))
        camResolution.setValue(str(self.cameraSetup.camResDropdown.currentText()))

        screenAdjustment = UI4.FormMaster.CreateParameterPolicy(None, renderSettings.getParameter('args.renderSettings.adjustScreenWindow'))
        screenAdjustment.setValue(str(self.cameraSetup.screenDropDown.currentText()))

        renderInput = renderSettings.getInputPort('input')

        
        # if the 'use skydome' check box is checked, create a skydome
        # note to self: the line in the if statement is calling a function
        # from within the SkydomeSetup class

        if self.skydomeSetup.useSkydome.isChecked():
            skydome = SkydomeSetup.createSkydome(self)
            
            # hooking the skydome up to the dolly constraint above it
            # and the render settings below it

            skydomeInput = skydome.getInputPort('in')
            skydomeOutput = skydome.getOutputPort('out')
            skydomeInput.connect(dollyOutputPort)
            skydomeOutput.connect(renderInput)

        else:
            # if the checkbox is not checked, 
            dollyOutputPort.connect(renderInput)


        allNodes = NodegraphAPI.GetAllNodes()
        NodegraphAPI.ArrangeNodes(allNodes, nodeGraphLengthSpacing = 250, nodeGraphWidthSpacing = 100)

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

class CameraSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.parentLayout = QGridLayout()
        self.createModule()
    
    def createModule(self):
        
        cameraSettingsHeader = QLabel("Camera Settings")
        camFOVLabel = QLabel('FOV Amount')
        self.FOVValue = QLineEdit()
        self.FOVValue.setText("70")
        
        makeCamInteractiveLabel = QLabel("Disable Make Camera Interactive?")
        self.makeCamInteractive = QCheckBox()
        
        camResolution = QLabel("Resolution")
        self.camResDropdown = UI4.Widgets.ResolutionComboBox(self)
        

        adjustmentTypes = ['No adjustment',
                           'Adjust height to match resolution',
                           'Adjust width to match resolution']
        
        screenWindow = QLabel("Adjust Screen Window")
        self.screenDropDown = UI4.Widgets.QtWidgets.QComboBox()
        self.screenDropDown.addItems(adjustmentTypes)



        self.parentLayout.addWidget(cameraSettingsHeader, 0, 0)
        self.parentLayout.addWidget(camFOVLabel, 1, 0)
        self.parentLayout.addWidget(self.FOVValue, 1, 1)
        self.parentLayout.addWidget(makeCamInteractiveLabel, 1, 2)
        self.parentLayout.addWidget(self.makeCamInteractive, 1, 3)
        self.parentLayout.addWidget(camResolution, 2, 0)
        self.parentLayout.addWidget(self.camResDropdown, 2, 1, 1, 3)
        self.parentLayout.addWidget(screenWindow, 3, 0)
        self.parentLayout.addWidget(self.screenDropDown, 3, 1, 1, 3)
        
        self.show()
        self.setLayout(self.parentLayout)
    


turnTable = TurntableWindow()