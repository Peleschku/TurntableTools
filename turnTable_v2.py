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

        self.setGeometry(250, 250, 500, 250)
        self.setWindowTitle('Please work')

        self.populateUI()
        self.show()
    
    def populateUI(self):
        
        mainLayout = QGridLayout()
        mainLayout.setVerticalSpacing(15)

        skydomeLayout = QGridLayout()
        skydomeLayout.setVerticalSpacing(7)


        # creating the file browser
        assetLabel = QLabel("Path to Asset")
        self.assetPath = QLineEdit()

        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.assetBrowser)

        # adding the Skydome layout

        self.SkydomeLayout = SkydomeSetup(skydomeLayout)


        
        
        # adding asset browser to the UI layout
        mainLayout.addWidget(assetLabel, 0, 0, 1, 1)
        mainLayout.addWidget(self.assetPath, 0, 1, 1, 6)
        mainLayout.addWidget(self.searchButton, 0, 7, 1, 1)
        # adding the skydome layout
        mainLayout.addWidget(self.SkydomeLayout, 1, 0, 1, 8)
        
        self.show()
        self.setLayout(mainLayout)

    def assetBrowser(self):

        # means the file browser only reads alembic files
        filter = "alembic (*.abc)"

        self.filePath = QFileDialog.getOpenFileName(self, "Select Asset", "", filter)

        if self.filePath:
            self.assetPath.insert(self.filePath[0])

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

        self.useTexture = QCheckBox("Use HDRI")
        self.useSkydome = QCheckBox("Use Skydome")

        # light intensity

        intensityLabel = QLabel("Light Instensity")
        self.intensityValue = QDoubleSpinBox()        
        self.intensitySlider = UI4.Widgets.QT4Widgets.SliderWidget(self)
        self.intensitySlider.setRange(0, 10)
        self.intensitySlider.valueChanged.connect(self.intensityChanged)

        # light exposure
        exposureLabel = QLabel("Light Exposure")
        self.exposureValue = QDoubleSpinBox()
        self.exposureValue.setMinimum(-99.99)
        self.exposureSlider = UI4.Widgets.QT4Widgets.SliderWidget(self)
        self.exposureSlider.setRange(-5, 10)
        self.exposureSlider.valueChanged.connect(self.exposureChanged)

        # Assign a texture to the Light
        self.parentLayout.addWidget(texturePathLabel, 0, 0)
        self.parentLayout.addWidget(self.texturePath, 0, 1, 1, 6)
        self.parentLayout.addWidget(self.searchTexture, 0, 7, 1, 1)
        
        # Set Light's colorspace
        self.parentLayout.addWidget(colorSpace, 3, 0)
        self.parentLayout.addWidget(self.selectColorspace, 3, 1, 1, 7)
        self.parentLayout.addWidget(mapping, 4, 0)
        
        # Set the texture image's mapping type
        self.parentLayout.addWidget(self.mappingDrowdown, 4, 1, 1, 7)
        self.parentLayout.addWidget(self.useTexture, 5, 7, 1, 1, Qt.AlignLeft)

        # Light intensity Settings
        self.parentLayout.addWidget(intensityLabel, 6, 0)
        self.parentLayout.addWidget(self.intensityValue, 6, 1, 1, 1, Qt.AlignLeft)
        self.parentLayout.addWidget(self.intensitySlider, 6, 2, 1, 6)
        

        # Light Exposure Settings
        self.parentLayout.addWidget(exposureLabel, 7, 0, 1, 1)
        self.parentLayout.addWidget(self.exposureValue, 7, 1, 1, 1, Qt.AlignLeft)
        self.parentLayout.addWidget(self.exposureSlider, 7, 2, 1, 6)

        self.parentLayout.addWidget(self.useSkydome, 8, 7, 1, 1, Qt.AlignLeft)

        self.show()
        self.setLayout(self.parentLayout)
    
    # Opens a file browser when search button is clicked
    # then adds the image path to the search bar

    def textureBrowser(self):
                
        self.filePath = QFileDialog.getOpenFileName(self, "Select Asset",)

        if self.filePath:
            self.texturePath.insert(self.filePath[0])

    # when the sliders for intensity/exposure are changed, the
    # spin boxes update to reflect that

    def intensityChanged(self):
        value = self.intensitySlider.getValue()
        self.intensityValue.setValue(value)
    
    def exposureChanged(self):
        value = self.exposureSlider.getValue()
        self.exposureValue.setValue(value)

    # creates a gaffer three containing a skydome

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
    
    # grabs the material node inside the gaffer three

    def envLightMaterial(gafferToEdit):
        
        rootPkg = gafferToEdit.getRootPackage()
        lightPkg = rootPkg.getChildPackage('envLight')
        lightMat = lightPkg.getMaterialNode()
        lightMat.checkDynamicParameters()

        return lightMat



open = TurntableWindow()