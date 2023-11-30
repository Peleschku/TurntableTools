import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class LookDevelopmentEnvironment(QWidget):
    def __init__(self):
        super().__init__()
        self.root = NodegraphAPI.GetRootNode()
        self.createLayout()

    def createWindow(self):

        self.setGeometry(150, 150, 200, 250)
        self.setWindowTitle('Look development Window')

        self.createUI()
        self.show()
    
    def createUI(self):

        layout = QGridLayout()

        lookdevHeading = QLabel("Look Development Assets")

        layout.addWidget(lookdevHeading, 0, 0)

        self.show()
        self.setLayout(layout)


lookDevWindow = LookDevelopmentEnvironment()