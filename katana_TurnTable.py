import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class turntableMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.createWindow()
    
    def createWindow(self):
        

        self.setGeometry(150, 150, 200, 250)
        self.setWindowTitle("Turn Table Creator")

        self.populateUI()
        self.show()
    
    def populateUI(self):

        layout = QGridLayout()
        threePointLayout = QGridLayout()
        skyDomeLayout = QGridLayout()

        self.assetLabel = QLabel("Path to Asset")
        self.assetPath = QLineEdit()

        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.assetSearch)
        
        '''
        Tabs to specify lighting setups and the like
        '''
        self.lightingTabs = QTabWidget()

        # three point lighting layouts

        self.threePointTab = QWidget()

        keyLight = ThreePointSelectors(threePointLayout, 'Key Light', 0)

        pointLight = ThreePointSelectors(threePointLayout, 'Point Light', 1)

        fillLight = ThreePointSelectors(threePointLayout, 'Fill Light', 2)
        
        self.threePointTab.setLayout(threePointLayout)

        # skydome lighting setup
        
        self.skyDomeTab = QWidget()

        skydomeSetup = HDRISetup(skyDomeLayout)

        self.skyDomeTab.setLayout(skyDomeLayout)

        # adding the tabs to the overall tab widget

        self.lightingTabs.addTab(self.threePointTab, "Three Point Setup")
        self.lightingTabs.addTab(self.skyDomeTab, "HDRI Lighting Setup")

        # camera settings widget

        self.cameraSettings = CameraSettings()
        
        # lookdev scene create
        self.lookdevSettings = LookdevSettings()

        self.createScene = QPushButton("Create Turntable Scene!")
        self.createScene.clicked.connect(self.generateTurnTable)

 
        layout.addWidget(self.assetLabel, 0, 0)
        layout.addWidget(self.assetPath, 0, 1)
        layout.addWidget(self.searchButton, 0, 4)
        layout.addWidget(spacer, 1, 0)
        layout.addWidget(self.lightingTabs, 2, 0, 1, 5)
        layout.addWidget(self.cameraSettings, 3, 0, 1, 5)
        layout.addWidget(self.lookdevSettings, 4, 0, 1, 5)
        layout.addWidget(self.createScene, 5, 0, 1, 5)

        self.show()
        self.setLayout(layout)
    
    def assetSearch(self):
        self.filePath = QFileDialog.getOpenFileName(self, "Select Asset")

        if self.filePath:
            self.assetPath.insert(self.filePath[0])
    
    
    def skyDomeSetup(self):
        print('Sky Dome!')
    
    def studioSetup(self):
        print("Studio!")
    
    def generateTurnTable(self):
        
        #creating the root node
        root = NodegraphAPI.GetRootNode()
        
        #creates the alembic in containing the asset specified in the UI's file search
        assetIn = NodegraphAPI.CreateNode('Alembic_In', root)
        assetInPP = UI4.FormMaster.CreateParameterPolicy(None, assetIn.getParameter('abcAsset')).setValue(str(self.assetPath.text()))



class ThreePointSelectors(QWidget):
    def __init__(self, parentLayout, lightName, row):
        super().__init__()
        self.parentLayout = parentLayout
        self.lightName = lightName
        self.row = row
        #self.parent = turntableMainWindow
        self.createModule()

    
    def createModule(self):

        lightSettingsHead = QLabel(f"{self.lightName} Settings")

        colorLabel = QLabel("Color")
        #colorPicker = UI4.FormMaster.Editors.KatanaColor.KatanaColorFormWidget()
        

        intensityLabel = QLabel("Light Intensity")        
        inputIntensity = QLineEdit()
        inputSlider = UI4.FormMaster.Editors.UserParametersDialogs.QtWidgets.QSlider()
        #inputIntensity.addItem(int(inputSlider))

        exposureLabel = QLabel("Light Exposure")
        inputExposure = QLineEdit()

        #number of rows in the layout 
        numberOfRows = 3
        
        self.parentLayout.addWidget(lightSettingsHead, self.row*numberOfRows+0, 0)
        self.parentLayout.addWidget(colorLabel, self.row*numberOfRows+1, 0)
        #self.parentLayout.addWidget(colorPicker, self.row*numberOfRows+2, 0)
        self.parentLayout.addWidget(intensityLabel, self.row*numberOfRows+1, 1)
        self.parentLayout.addWidget(inputIntensity, self.row*numberOfRows+2, 1)
        self.parentLayout.addWidget(exposureLabel, self.row*numberOfRows+1, 2)
        self.parentLayout.addWidget(inputExposure, self.row*numberOfRows+2, 2)
        
class HDRISetup(QWidget):
    def __init__(self, parentLayout):
        super().__init__()
        self.parentLayout = parentLayout
        self.createModule()
    
    def createModule(self):
        lightSettingsHead = QLabel("HDRI Settings")
        lightSettingsHead.setAlignment(Qt.AlignCenter)
        
        mappingParams = ["Spherical (latlong)",
                         "Angular"]
        
        nameLabel = QLabel("HDRI Path")
        self.hdriPath = QLineEdit()
        self.hdriSearch = QPushButton("Search for Texture")
        self.hdriSearch.clicked.connect(self.setHDRIPath)

        colorspaceLabel = QLabel("Set Color Space")
        selectColorspace = UI4.Widgets.ColorspaceSelectionWidget(self)

        mappingLabel = QLabel("Set Mapping Type")

        self.parentLayout.addWidget(lightSettingsHead, 0, 0 )
        self.parentLayout.addWidget(nameLabel, 1, 0)
        self.parentLayout.addWidget(self.hdriPath, 2, 0, 1, 3)
        self.parentLayout.addWidget(self.hdriSearch, 2, 3)
        self.parentLayout.addWidget(colorspaceLabel, 3, 0)
        self.parentLayout.addWidget(selectColorspace, 4, 0, 1, 4)
        self.parentLayout.addWidget(mappingLabel, 6, 0)
        #self.parentLayout.addWidget(mappingParams, 6, 0)
    
    def setHDRIPath(self):
        self.filePath = QFileDialog.getOpenFileName(self, "Select Asset")

        if self.filePath:
            self.hdriPath.insert(self.filePath[0])

class CameraSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.parentLayout = QGridLayout()
        self.createModule()
    
    def createModule(self):
        
        cameraSettingsHeader = QLabel("Camera Settings")
        camFOVLabel = QLabel('FOV Amount')
        self.FOVValue = QLineEdit()
        
        makeCamInteractiveLabel = QLabel("Make Camera Interactive?")
        self.makeCamInteractive = QCheckBox()
        
        camResolution = QLabel("Resolution")
        self.camResDropdown = UI4.Widgets.ResolutionComboBox(self)


        self.parentLayout.addWidget(cameraSettingsHeader, 0, 0)
        self.parentLayout.addWidget(camFOVLabel, 1, 0)
        self.parentLayout.addWidget(self.FOVValue, 1, 1)
        self.parentLayout.addWidget(makeCamInteractiveLabel, 1, 2)
        self.parentLayout.addWidget(self.makeCamInteractive, 1, 3)
        self.parentLayout.addWidget(camResolution, 2, 0)
        self.parentLayout.addWidget(self.camResDropdown, 2, 1, 2, 3)
        
        self.show()
        self.setLayout(self.parentLayout)

class LookdevSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.parentLayout = QGridLayout()
        self.createModule()
    
    def createModule(self):
        
        lookdevHeader = QLabel("Look Dev Scene Settings")
        self.enableBackdrop = QCheckBox("Enable Backdrop")
        self.enableMacbethChart = QCheckBox("Enable Macbeth Chart")
        self.enableShaderBalls = QCheckBox("Enable Shader Balls")

        self.parentLayout.addWidget(lookdevHeader, 0, 0)
        self.parentLayout.addWidget(self.enableBackdrop, 1, 0)
        self.parentLayout.addWidget(self.enableMacbethChart, 1, 1)
        self.parentLayout.addWidget(self.enableShaderBalls, 1, 2)
        
        self.show()
        self.setLayout(self.parentLayout)

launchWindow = turntableMainWindow()
