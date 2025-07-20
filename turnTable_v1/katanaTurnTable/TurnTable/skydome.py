from Katana import NodegraphAPI


from PyQt5.QtWidgets import (QWidget,
                            QGridLayout,
                            QLabel,
                            QCheckBox,
                            QLineEdit,
                            QPushButton,
                            QComboBox,
                            QDoubleSpinBox,
                            QSlider,
                            QFileDialog)
from PyQt5.QtCore import *



class SkydomeSetup(QWidget):
    def __init__(self):
        super().__init__()
        self._parentLayout = QGridLayout()
        self.root = NodegraphAPI.GetRootNode()
        self._createModule()

    def _createModule(self):

        # Assign textures

        lightingLabel = QLabel("Skydome Setup")
        texPathLabel = QLabel("Path to Texture")
        self._texturePath = QLineEdit()
        self._searchTexture = QPushButton("Search")
        self._searchTexture.clicked.connect(self._textureBrowser)

        self._parentLayout.addWidget(lightingLabel, 0, 0)
        self._parentLayout.addWidget(texPathLabel, 1, 0)
        self._parentLayout.addWidget(self._texturePath, 1, 1, 1, 6)
        self._parentLayout.addWidget(self._searchTexture, 1, 7, 1, 1, Qt.AlignLeft)

        # Light Colorspace settings
        colorSpaces = ['auto',
                       'sRGB',
                       'Rec, 709',
                       'linear']
        colorSpaceLabel = QLabel("Set COlorspace")
        self._selectColorspace = QComboBox()
        self._selectColorspace.addItems(colorSpaces)

        self._parentLayout.addWidget(colorSpaceLabel, 4, 0)
        self._parentLayout.addWidget(self._selectColorspace, 4, 1, 1, 7)

        # image mapping type
        mappingParams = ["Spherical (latlong)",
                         "Angular"]
        mappingLabel = QLabel("Set Image Mapping Type")
        self._mappingDropdown = QComboBox()
        self._mappingDropdown.addItems(mappingParams)

        self._parentLayout.addWidget(mappingLabel, 5, 0)
        self._parentLayout.addWidget(self._mappingDropdown, 5, 1, 1, 7)

        # enable texture
        self._enableTexture = QCheckBox("Assign texture to Skydome?")

        self._parentLayout.addWidget(self._enableTexture, 6, 7, 1, 1, Qt.AlignLeft)

        # light intensity
        intensityLabel = QLabel("Light Intensity")
        
        self._intensityValue = QDoubleSpinBox()
        self._intensityValue.setMinimum(-99.99)
        self._intensityValue.setMaximum(1000.00)
        
        self._intensitySlider = QSlider()
        self._intensitySlider.setRange(0, 10)
        self._intensitySlider.valueChanged.connect(self._intensityChanged)

        self._parentLayout.addWidget(intensityLabel, 7, 0)
        self._parentLayout.addWidget(self._intensityValue, 7, 1, 1, 1, Qt.AlignLeft)
        self._parentLayout.addWidget(self._intensitySlider, 7, 2, 1, 6)

        # Light exposure
        exposureLabel = QLabel("Light Exposure")

        self._exposureValue = QDoubleSpinBox()
        self._exposureValue.setMinimum(-99.99)
        self._exposureValue.setMaximum(1000.00)

        self._exposureSlider = QSlider()
        self._exposureSlider.setRange(0, 10)
        self._exposureSlider.valueChanged.connect(self._exposureChanged)

        self._parentLayout.addWidget(exposureLabel, 8, 0, 1, 1)
        self._parentLayout.addWidget(self._exposureValue, 8, 1, 1, 1, Qt.AlignLeft)
        self._parentLayout.addWidget(self._exposureSlider, 8, 2, 1, 6)

        # pack

        self.show()
        self.setLayout(self._parentLayout)

    
    def _textureBrowser(self):
        filePath = QFileDialog.getOpenFileName(self, "Select Texture")

        if filePath:
            self._texturePath.insert(filePath[0])

    def _intensityChanged(self):
        value = self._intensitySlider.value()
        self._intensityValue.setValue(value)

    def _exposureChanged(self):
        value = self._exposureSlider.value()
        self._exposureValue.setValue(value)
    
    def _createSkydome(self, parent):
        #create GafferThree node
        gafferThree = NodegraphAPI.CreateNode("GafferThree", parent)
        rootPackage = gafferThree.getRootPackage()
        rootPackage.createChildPackage("EnvironmentLightPackage", "envLight")

        # create skydome
        light = rootPackage.getChildPackage("envLight")
        lightMat = light.getMaterialNode()
        lightShader = lightMat.addShaderType("dlEnvironmentShader")

        envLight = UI4.FormMaster.CreateParameterPolicy(None,
                                                        lightMat.getParameter(
                                                            "shaders.dlEnvironmentShader"
                                                        ))
        envLight.setValue("environmentLight")
        lightMat.checkDynamicParameters()

        return gafferThree

    def _lightMaterial(self, gafferToEdit):
        
        # retrieves the material node within GafferThree node
        # is used later to change exposure/intensity/texture
        rootPkg = gafferToEdit.getRootPackage()
        lightPkg =  rootPkg.getChildPackage("envLight")
        lightMat = lightPkg.getMaterialNode()
        lightMat.checkDynamicParameters()

        return lightMat
        
