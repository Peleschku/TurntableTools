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
        skydomeLayout = QGridLayout()
        skydomeLayout.setVerticalSpacing(10)

        threePointLayout = QGridLayout()
        threePointLayout.setVerticalSpacing(10)

        assetLabel = QLabel("Path to Asset")
        self.assetPath = QLineEdit()
        
        # button that opens the file browser. Once a .abc file is specificed
        # the file path is added to self.assetPath()

        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.assetBrowser)
        
        # creating the lighting tabs
        self.lightingTabs = QTabWidget()
        
        # Skydome Tab
        self.skyDomeTab = QWidget()
        
        self.skydomeSetup = SkydomeSetup(skydomeLayout)
        
        self.skyDomeTab.setLayout(skydomeLayout)

        # three point lighting tab

        self.threePointTab = QWidget()
        test = QLabel("hello!")
        threePointLayout.addWidget(test, 0, 0)
        self.threePointTab.setLayout(threePointLayout)


        # adding tabs to tab widget

        self.lightingTabs.addTab(self.skyDomeTab, "Environment Lighting Setup")
        self.lightingTabs.addTab(self.threePointTab, "Three Point Lighting")
        
        # adding camera layout

        self.cameraSetup = CameraSettings() 

        # adding lookdev tools layout

        self.LookdevSetup = LookDevelopmentEnvironment()

        
        # button that assembles the turn table when clicked

        self.createTurnTable = QPushButton("Create Turn Table")
        self.createTurnTable.clicked.connect(self.generateTT)

        layout.addWidget(assetLabel, 0, 0)
        layout.addWidget(self.assetPath, 0, 1, 1, 3)
        layout.addWidget(self.searchButton, 0, 4)
        layout.addWidget(self.lightingTabs, 1, 0, 1, 5)
        layout.addWidget(self.cameraSetup, 2, 0, 1, 5)      
        layout.addWidget(self.LookdevSetup, 3, 0, 1, 5)
        layout.addWidget(self.createTurnTable, 4, 0, 1, 5)

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

        # if the use texture checkbox in the Skydome tab is checked:
        if self.skydomeSetup.useTexture.isChecked():
            lightMat = SkydomeSetup.envLightMaterial(skydome)

            texturePath = UI4.FormMaster.CreateParameterPolicy(None, lightMat.getParameter('shaders.dlEnvironmentParams.image'))
            texturePath.setValue(str(self.skydomeSetup.texturePath.text()))

            colorSpace = UI4.FormMaster.CreateParameterPolicy(None, lightMat.getParameter('shaders.dlEnvironmentParams.image_meta_colorspace'))
            colorSpace.setValue(str(self.skydomeSetup.selectColorspace.currentText()))
        
        
        # if there are values in the intensity/exposure boxes, do the following:

        intensity = UI4.FormMaster.CreateParameterPolicy(None, lightMat.getParameter('shaders.dlEnvironmentParams.intensity'))
        exposure = UI4.FormMaster.CreateParameterPolicy(None, lightMat.getParameter('shaders.dlEnvironmentParams.exposure'))
        
        if self.skydomeSetup.intensityValue.text() != "0":
            intensity.setValue(int(self.skydomeSetup.intensityValue.text()))
        
        if self.skydomeSetup.exposureValue.text() != "0":
            exposure.setValue(int(self.skydomeSetup.intensityValue.text()))
             



        allNodes = NodegraphAPI.GetAllNodes()
        NodegraphAPI.ArrangeNodes(allNodes, nodeGraphLengthSpacing = 250, nodeGraphWidthSpacing = 100)

class SkydomeSetup(QWidget):
    def __init__(self, parentLayout):
        super().__init__()
        self.parentLayout = parentLayout
        self.root = NodegraphAPI.GetRootNode()
        self.createModule()
    
    def createModule(self):

        # path to texture

        texturePathLabel = QLabel("Path to Texture")
        self.texturePath = QLineEdit()
        self.searchTexture = QPushButton("Search")
        self.searchTexture.clicked.connect(self.textureBrowser)

        colorSpaceList = ['auto',
                          'sRGB',
                          'Rec. 709',
                          'linear']
        colorSpace = QLabel("Set Colorspace")
        self.selectColorspace = UI4.Widgets.QtWidgets.QComboBox()
        self.selectColorspace.addItems(colorSpaceList)

        mappingParams = ["Spherical (latlong)",
                        "Angular"]
        
        mapping = QLabel("Set Mapping Type")
        self.mappingDrowdown = UI4.Widgets.QtWidgets.QComboBox()
        self.mappingDrowdown.addItems(mappingParams)

        self.useTexture = QCheckBox("Use HDRI Texture?")
        self.useSkydome = QCheckBox("Use Skydome Setup")

        intensityLabel = QLabel("Instensity")
        self.intensityValue = QLineEdit()
        self.intensityValue.setText("0")

        exposureLabel = QLabel("Exposure")
        self.exposureValue = QLineEdit()
        self.exposureValue.setText("0")

        self.parentLayout.addWidget(texturePathLabel, 0, 0)
        self.parentLayout.addWidget(self.texturePath, 0, 1, 1, 4)
        self.parentLayout.addWidget(self.searchTexture, 0, 5)
        self.parentLayout.addWidget(colorSpace, 3, 0)
        self.parentLayout.addWidget(self.selectColorspace, 3, 1, 1, 5)
        self.parentLayout.addWidget(mapping, 4, 0)
        self.parentLayout.addWidget(self.mappingDrowdown, 4, 1, 1, 5)
        self.parentLayout.addWidget(self.useTexture, 5, 5)
        self.parentLayout.addWidget(intensityLabel, 6, 0)
        self.parentLayout.addWidget(self.intensityValue, 6, 1)
        self.parentLayout.addWidget(exposureLabel, 6, 3)
        self.parentLayout.addWidget(self.exposureValue, 6, 4,)
        self.parentLayout.addWidget(self.useSkydome, 7, 5)

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
    
    def envLightMaterial(gafferToEdit):
        
        rootPkg = gafferToEdit.getRootPackage()
        lightPkg = rootPkg.getChildPackage('envLight')
        lightMat = lightPkg.getMaterialNode()
        lightMat.checkDynamicParameters()

        return lightMat

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

        self.show()
        self.setLayout(layout)

turnTable = TurntableWindow()