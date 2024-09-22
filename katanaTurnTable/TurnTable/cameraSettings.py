from Katana import (NodeGraphAPI,
                    UI4)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget,
                            QGridLayout,
                            QLabel,
                            QSpinBox,
                            QComboBox,
                            QCheckBox)



class CameraSettings(QWidget):
    def __init__(self):
        super().__init__()
        self._parentLayout = QGridLayout()
        self.createModule()
        self.root = NodeGraphAPI.GetRootNode()

    def createModule(self):

        camSettingsHeader = QLabel("Camera Settings")
        
        self._parentLayout.addWidget(camSettingsHeader, 0, 0)
        
        # FOV settings
        camFOVLabel = QLabel("FOV Amount")
        self._FOVValue = QSpinBox()
        self._FOVValue.setValue(70)
        self._FOVValue.setMaximum(1000)
        
        self._parentLayout.addWidget(camFOVLabel, 1, 0)
        self._parentLayout.addWidget(self._FOVValue, 1, 1, 1, 1, Qt.AlignLeft)
        
        # camera distance settings
        distanceLabel = QLabel("Camera Distance")
        self._setDistance = QSpinBox()
        self._setDistance.setMinimum(0)
        self._setDistance.setMaximum(1000)

        self._parentLayout.addWidget(distanceLabel, 1, 3, 1, 1, Qt.AlignLeft)
        self._parentLayout.addWidget(self._setDistance, 1, 4, 1, 1)        

        # camera resolution settings
        # TODO: add a json or soemthing containing different res types
        camRes = QLabel("Resolution")
        self._camResDropdown = QComboBox()

        self._parentLayout.addWidget(camRes, 2, 0)
        self._parentLayout.addWidget(self._camResDropdown, 2, 1, 1, 7)


        #  screen adjustment settings
        adjustmentTypes = ['No adjustment',
                           'Adjust height to match resolution',
                           'Adjust width to match resolution']
        
        screenWindow = QLabel("Window Adjustment")
        self._screenDropdown = QComboBox()
        self._screenDropdown.addItems(adjustmentTypes)

        self._parentLayout.addWidget(screenWindow, 3, 0)
        self._parentLayout.addWidget(self._screenDropDown, 3, 1, 1, 7)

        # Make interactive settings
        self._makeInteractive = QCheckBox("Lock Camera")
        self._parentLayout.addWidget(self._makeInteractive, 4, 7)

        self.show()
        self.setLayout(self._parentLayout)
    
    def _cameraCreate(self):
        
        #creating the CameraCreate node and setting a default transform value
        cameraCreate = NodeGraphAPI.CreateNode("CameraCreate", self.root)
        camtranslate = UI4.FormMaster.CreateParameterPolicy(None, cameraCreate.getParameter(
            "transform.translate"
        )).setValue([0, 1.5, 14])

        # camera FOV settings based on user input
        cameraFOV = UI4.FormMaster.CreateParameterPolicy(None, cameraCreate.getParameter(
            "fov"
        ))
        if self._FOVValue.text() !=70:
            cameraFOV.setValue(self._FOVValue.text())
        
        # make camera interactive based on user input
        makeInteractive = UI4.FormMaster.CreateParameterPolicy(None, cameraCreate.getParameter(
            "makeInteractive"
        ))
        if self._makeInteractive.setCheckable(False):
            makeInteractive.setValue("No")
        else:
            makeInteractive.setValue("Yes")


        return cameraCreate

    def dollyConstraintCreate(self, cameraPath, assetPath, offsetAmount):
        dollyConstraint = NodegraphAPI.CreateNode('DollyConstraint', self.root)

        dollyBasePath = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('basePath'))
        dollyBasePath.setValue(cameraPath)

        dollyTargetPath = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('targetPath.i0'))
        dollyTargetPath.setValue(assetPath)

        dollyTargetBounds = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('targetBounds'))
        dollyTargetBounds.setValue('box')

        dollyOffsetAngle = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('angleOffset'))
        dollyOffsetAngle.setValue(offsetAmount)

        dollyConstraintList = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('addToConstraintList'))
        dollyConstraintList.setValue(1.0)

        return dollyConstraint



