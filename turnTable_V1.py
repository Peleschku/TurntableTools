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

        assetLabel = QLabel("Path to Asset")
        self.assetPath = QLineEdit()
        
        # button that opens the file browser. Once a .abc file is specificed
        # the file path is added to self.assetPath()

        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.assetBrowser)

        # create camera is checkbox is checked

        cameraHeader = QLabel("Camera Settings")
        self.createCamera = QCheckBox("Create Camera?")
        updateCamRes = QLabel("Resolution")
        self.cameraResSelect = UI4.Widgets.ResolutionComboBox(self)

        
        # button that assembles the turn table when clicked

        self.createTurnTable = QPushButton("Create Turn Table")
        self.createTurnTable.clicked.connect(self.generateTT)

        layout.addWidget(assetLabel, 0, 0)
        layout.addWidget(self.assetPath, 0, 1)
        layout.addWidget(self.searchButton, 0, 4)
        layout.addWidget(cameraHeader, 1, 0)
        layout.addWidget(self.createCamera, 2, 0)
        layout.addWidget(updateCamRes, 3, 0)
        layout.addWidget(self.cameraResSelect, 3, 1)
        layout.addWidget(self.createTurnTable, 4, 0, 1, 4)

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
    
    def generateTT(self):

        alembicCreate = NodegraphAPI.CreateNode('Alembic_In', self.root)
        assetSet = UI4.FormMaster.CreateParameterPolicy(None, alembicCreate.getParameter('abcAsset'))
        assetSet.setValue(str(self.assetPath.text()))

        if self.createCamera.isChecked():
            camera = NodegraphAPI.CreateNode('CameraCreate', self.root)
        
        camTranslate = UI4.FormMaster.CreateParameterPolicy(None, camera.getParameter('transform.translate'))
        camTranslate.setValue([0.0,
                               0.6,
                               1.6], 1)
        

        camAssetMerge = self.multiMerge([alembicCreate, camera])
        camMergeOut = camAssetMerge.getOutputPort('out')

        # creates render settings node and assigns the camera resolution
        # based on the selection in the UI's dropdown
        
        renderSettings = NodegraphAPI.CreateNode('RenderSettings', self.root)
        resolution = UI4.FormMaster.CreateParameterPolicy(None, renderSettings.getParameter('args.renderSettings.resolution'))
        resolution.setValue(str(self.cameraResSelect.currentText()))

        renderInput = renderSettings.getInputPort('input')

        camMergeOut.connect(renderInput)






turnTable = TurntableWindow()