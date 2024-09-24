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
from . import nodes as Nodes


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
        assetNmc = Nodes._assetNMC(self.root)
        
        # camera nodes + settings
        cameraCreate = Cam.CameraSettings._cameraCreate()
        camLocation = cameraCreate.getParameterValue('name', NodegraphAPI.GetCurrentTime())

        '''
        TODO: all the material subdiv nodes should eventually go in to a merge, with all the
        material assigns eventually living under that merge node. 
        Everything in the Lookdev group also eventually needs to live inside of a group, so
        `lookdevParentNmc` as the root node for all the materials will need to be switched out,
        and all the `self.root`s for the look dev geo/associated nodes will need to be swapped
        with the eventual group.

        '''
        
        # Lookdev setup

        if self._lookDevSetup._enableBackdrop.isChecked() and self._lookDevSetup._enableBackdrop.isChecked():
            lookdevGroup = Utils.groupNodeSetup(self.root)
            lookdevParentNmc = NodegraphAPI.CreateNode("NetworkMaterialCreate", lookdevGroup)
            lookdevSetup = Ld._lookDevGroup(lookdevGroup, lookdevParentNmc)
            # add backdrop, finish off if statement

        
        
        '''
        # grey lookdev sphere setup
        greySphere = Ld._shaderBall(self.root, "grey")
        greyLocation = greySphere.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        greySubdiv = Utils.subDivideMesh(greyLocation, self.root)
        greyMaterial = Ld._shaderBallMaterial(lookdevParentNmc, "grey")
        greyMatAssign = Utils.materialAssignSetup(greyLocation, greyMaterial, self.root)
        Utils.connectTwoNodes(greySphere, greySubdiv, "out", "in")
        Utils.connectTwoNodes(greySubdiv, greyMatAssign"out", "in")


        #chrome lookdev sphere setup
        chromeSphere = Ld._shaderBall(self.root, "chrome")
        chromeLocation = chromeSphere.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        chromeSubdiv = Utils.subDivideMesh(chromeLocation, self.root)
        chromeMaterial = Ld._shaderBallMaterial(lookdevParentNmc, "chrome")
        chromeMatAssign = Utils.materialAssignSetup(chromeLocation, chromeMaterial, self.root)
        Utils.connectTwoNodes(chromeSphere, chromeSubdiv, "out", "in")
        Utils.connectTwoNodes(chromeSubdiv, chromeMatAssign, "out", "in")

        # macbeth chart setup
        macbethChart = Ld._macbethChartGeo(self.root)
        chartLocation = macbethChart.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        chartSubdiv = Utils.subDivideMesh(chartLocation)
        chartMaterial = Ld._chartMaterial(lookdevParentNmc)
        chartMatAssign = Utils.materialAssignSetup(chartLocation, chartMaterial, self.root)
        Utils.connectTwoNodes(macbethChart, chartSubdiv, "out", "in")
        Utils.connectTwoNodes(chartSubdiv, chartMatAssign, "out", "in")

        # backdrop setup
        backdrop = Ld._backdropPrim(self.root)
        backdropLocation = backdrop.getParameterValue("name", NodegraphAPI.GetCurrentTime())
        backdropSubdiv = Utils.subDivideMesh(backdropLocation)
        backdropMaterial = Ld._backdropMaterial(lookdevParentNmc)
        backdropMatAssign = Utils.materialAssignSetup(backdropLocation, backdropMaterial, self.root)
        Utils.connectTwoNodes(backdrop, backdropSubdiv, "out", "in")
        Utils.connectTwoNodes(backdropSubdiv, backdropMatAssign, "in", "out")
    '''


        






