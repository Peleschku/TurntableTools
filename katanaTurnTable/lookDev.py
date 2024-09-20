#from Katana import UI4
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QWidget,
                            QGridLayout,
                            QLabel,
                            QSpinBox,
                            QComboBox,
                            QCheckBox)
from . import utilites as Utils

class LookDevSetup(QWidget):
    def __init__(self):
        super().__init__()
        self.createModule()
        self._parentLayout = QGridLayout()
        self._parentLayout.setVerticalSpacing(15)

    def createModule(self):

        lookdevHeading = QLabel("Look Development Assets")
        self._parentLayout.addWidget(lookdevHeading, 0, 0)

        # adding a backdrop to the lookdev scene
        backdrop = QLabel("Enable Backdrop")
        self._enableBackdrop = QCheckBox("Backdrop")

        self._parentLayout.addWidget(backdrop, 1, 0)
        self._parentLayout.addWidget(self._enableBackdrop, 2, 0)

        # add lookdev set up

        lookdevTools = QLabel("Lookdev Tools")
        self._enableAll = QCheckBox("Enable Lookdev Setup")

        self._parentLayout.addWidget(lookdevTools, 3, 0)
        self._parentLayout.addWidget(self._enableAll)

        self.show()
        self.setLayout(self._parentLayout)

    



