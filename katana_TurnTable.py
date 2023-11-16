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

        self.populateUI()
        self.show()
    
    def populateUI(self):

        layout = QGridLayout()
        threePointLayout = QGridLayout()
        skyDomeLayout = QVBoxLayout()
        studioLayout = QGridLayout()

        self.assetLabel = QLabel("Path to Asset")
        self.assetPath = QLineEdit()

        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.assetSearch)
        
        '''
        Tabs to specify lighting setups and the like
        '''
        self.lightingTabs = QTabWidget()

        # three point lighting layouts

        self.threePointTab = QWidget()

        self.lightOneSettings = self.lightSettings('Light One')

        self.enableThreepoint = QCheckBox("Enable Three Point Lighting")

        threePointLayout.addWidget(self.lightOneSettings, 0, 1)
        threePointLayout.addWidget(self.enableThreepoint, 1, 1)
        self.threePointTab.setLayout(threePointLayout)

        # skydome lighting setup
        
        self.skyDomeTab = QWidget()

        self.skyDome = QPushButton("Sky Dome")
        self.skyDome.clicked.connect(self.skyDomeSetup)

        skyDomeLayout.addWidget(self.skyDome)
        self.skyDomeTab.setLayout(skyDomeLayout)

        # studio lighting setup

        self.studioLightingTab = QWidget()
        
        self.studio = QPushButton("Studio Lighting")
        self.studio.clicked.connect(self.studioSetup)

        studioLayout.addWidget(self.studio, 0, 1)

        self.studioLightingTab.setLayout(studioLayout)

        # adding the tabs to the overall tab widget

        self.lightingTabs.addTab(self.threePointTab, "Three Point Setup")
        self.lightingTabs.addTab(self.skyDomeTab, "Sky Dome Setup")
        self.lightingTabs.addTab(self.studioLightingTab, "Studio Lighting Setup")

        self.createScene = QPushButton("Create Turntable Scene!")
        self.createScene.clicked.connect(self.generateTurnTable)
        


        
        
        layout.addWidget(self.assetLabel, 0, 0)
        layout.addWidget(self.assetPath, 0, 1, 1, 3)
        layout.addWidget(self.searchButton, 0, 4)
        layout.addWidget(self.lightingTabs, 1, 0, 1, 5)
        layout.addWidget(self.createScene, 2, 3)

        self.show()
        self.setLayout(layout)
    
    def assetSearch(self):
        self.filePath = QFileDialog.getOpenFileName(self, "Select Asset")

        if self.filePath:
            self.assetPath.insert(self.filePath[0])
    
    def lightSettings(self, lightName):
'''
this isn't working properly, so need to have a go at getting this to work. it might not actaully work though -
not really sure if i can build a while mini GUI and then just plop it into another window.
'''
        
        lightsLayout = QGridLayout()
        lightLabel = QLabel(lightName + " Settings:")
        
        intensityLabel =  QLabel("Intensity")

        lightsLayout.addWidget(lightLabel, 0, 0)
        lightsLayout.addWidget(intensityLabel, 1, 0)


        
        self.show()
        self.setLayout(lightsLayout)

        return lightLabel

    
    def skyDomeSetup(self):
        print('Sky Dome!')
    
    def studioSetup(self):
        print("Studio!")
    
    def generateTurnTable(self):
        
        #creating the root node
        root = NodegraphAPI.GetRootNode()
        
        #creates the alembic in containing the asset specified in the UI's file search
        assetIn = NodegraphAPI.CreateNode('Alembic_In', root)
        assetInPP = UI4.FormMaster.CreateParameterPolicy(None, assetIn.getParameter('abcAsset')).setValue(str(self.assetPath.text()))


# when launching IN katana, make sure to get rid of this line...
app = QApplication(sys.argv)

launchWindow = turntableMainWindow()

# and this line!
sys.exit(app.exec_())

'''
testing to see if changes made can be pushed via the command line xoxo
'''



