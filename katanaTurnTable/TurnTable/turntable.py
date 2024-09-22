from Katana import NodegraphAPI

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
        self._parentLayout.addWidget(self._create, 3)

        self.show()
        self.setLayout(self._parentLayout)

    def _create(self):
        print("Hello!")



