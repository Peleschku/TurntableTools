import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class turntableMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.root = NodegraphAPI.GetRootNode()
        self.createWindow()
    
    def createWindow(self):

        layout = QGridLayout()
        threePointLayout = QGridLayout()
        skyDomeLayout = QGridLayout()

        self.assetLabel = QLabel("Path to Asset")
        self.assetPath = QLineEdit()

        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.assetSearch)

        # turntable create
        self.createScene = QPushButton("Create Turntable Scene!")
        self.createScene.clicked.connect(self.generateTurnTable)

        #turntable edit
        self.updateSceneButton = QPushButton("Update Turntable Scene")
        self.updateSceneButton.clicked.connect(self.updateScene)

        layout.addWidget(self.assetLabel, 0, 0)
        layout.addWidget(self.assetPath, 0, 1)
        layout.addWidget(self.searchButton, 0, 4)

        layout.addWidget(self.createScene, 1, 0)
        layout.addWidget(self.updateSceneButton, 1, 1)

        self.show()
        self.setLayout(layout)


    def assetSearch(self):
        self.filePath = QFileDialog.getOpenFileName(self, "Select Asset")

        if self.filePath:
            self.assetPath.insert(self.filePath[0])

    def attributeSetCreate(self, newType):
        attributeSet = NodegraphAPI.CreateNode('AttributeSet', self.root)
        assetPath = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('paths')).setValue('/root/world/geo/asset')
        attributeName = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('attributeName')).setValue('Type')
        attributeType = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('attributeType')).setValue('string')
        attributeType = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('stringValue')).setValue(newType)

        return attributeSet

    def alembicCreate(self):
        alembicIn = NodegraphAPI.CreateNode('Alembic_In', self.root)
        assetInPP = UI4.FormMaster.CreateParameterPolicy(None, alembicIn.getParameter('abcAsset')).setValue(str(self.assetPath.text()))

        return alembicIn
    
    def multiMerge (nodesToMerge):
        mergeNode = NodegraphAPI.CreateNode('Merge', self.root)

        for node in nodesToMerge:

            # grabbing the output ports of the nodes made outside of the function
            outputPort = node.getOutputPort('out')

            #adding input ports to the merge node  based on how many nodes were created
            mergeInput = mergeNode.addInputPort('i')

            #connecting the nodes
            outputPort.connect(mergeInput)
        
        return mergeNode
    
    
    def generateTurnTable(self):

        assetIn = self.alembicCreate()
        assetOut = assetIn.getOutputPort('out')

        attributeSet = self.attributeSetCreate('Subdmesh')
        attributeIn = attributeSet.getInputPort('A')
        attributeOut = attributeSet.getInputPort('out')

        assetOut.connect(attributeIn)




        
    def updateScene(self):
        print('hello!')
    

launchWindow = turntableMainWindow()