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

        layout = QGridLayout()

        self.assetLabel = QLabel("Path to Asset")
        self.assetPath = QLineEdit()
        
        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.assetSearch)

        
        
        layout.addWidget(self.assetLabel, 0, 0)
        layout.addWidget(self.assetPath, 0, 1)
        layout.addWidget(self.searchButton, 0, 2)

        self.show()
        self.setLayout(layout)
    
    def assetSearch(self):
        self.filePath = QFileDialog.getOpenFileName(self, "Select Asset")

        if self.filePath:
            self.assetPath.insert(self.filePath[0])




app = QApplication(sys.argv)

launchWindow = turntableMainWindow()
sys.exit(app.exec_())

'''
testing to see if changes made can be pushed via the command line xoxo
'''



