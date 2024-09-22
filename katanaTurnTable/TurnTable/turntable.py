import os
from Katana import (NodegraphAPI,
                    UI4)

from PyQt5.QtWidgets import (QWidget,
                            QVBoxLayout,
                            QPushButton,
                            QLabel,
                            QCheckBox,
                            QLineEdit)

from . import utilites as Utils
from . import cameraSettings as Cam
from . import skydome as Lgt
from . import lookDev as Ld


class TurnTableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.root = NodegraphAPI.GetRootNode()
        self._parentLayout = QVBoxLayout()
        self._createWindow()
    
    def createWindow(self):

        self.setGeometry(250, 250, 500, 250)
        self.setWindowTitle("Peleschku Turntable Tool for Katana")

        self.populateUI()
        self.show()
    
    def populateUI(self):

        self._assetSearch = Utils.SearchBrowser()
        self._skydomeSetup = Lgt.SkydomeSetup()
        self._lookDevSetup = Ld.LookDevSetup()

        self._create = QPushButton("Generate Turn Table")
        self._create.clicked.connect(self._createTurnTable)

        self._parentLayout.addWidget(self._assetSearch, 0)
        self._parentLayout.addWidget(self._skydomeSetup, 1)
        self._parentLayout.addWidget(self._lookDevSetup, 2)
        self._parentLayout.addWidget(self._createNodes, 3)

        self.show()
        self.setLayout(self._parentLayout)

    def _importAsset(self):

        fileName, fileExtension = os.path.splitext(self._assetSearch._assetPath)

        if fileExtension == ".abc":
            alembicIn = NodegraphAPI.CreateNode("Alembic_In", self.root)
            assetImport = UI4.FormMaster.CreateParamaterPolicy(None, alembicIn.getParameter(
                "abcAsset"
            )).setValue(str(self._assetSearch._assetPath.text()))
            return alembicIn
        elif fileExtension == ".usd" or ".usda":
            usdIn = NodegraphAPI.CreateNode("UsdIn", self.root)
            assetImport = UI4.FormMaster.CreateParameterPolicy(None, usdIn.getParameters(
                "fileName"
            )).setValue(str(self._assetSearch._assetPath.text()))
            return usdIn

    #def 

    def _createNodes(self):
        
        assetImport = self._importAsset()
        cameraCreate = Cam.CameraSettings._cameraCreate()
        # camera location for dolly constraint
        camLocation = cameraCreate.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        






