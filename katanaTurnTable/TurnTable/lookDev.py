import os
from Katana import (NodegraphAPI,
                    UI4)
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QWidget,
                            QGridLayout,
                            QLabel,
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

    def _shaderBall(root, sphereType):
        sphere = Utils.geoCreate("poly sphere", root)
        
        if sphereType == "grey":
            # giving a unique name so that it's easier to assign a material to later
            nameSet = sphere.getParameter("name").setValue("/root/world/LookDevScene/greySphere", 0)

            setInteractive = UI4.FormMaster.CreateParameterPolicy(None, sphere.getParameter(
                "makeInteractive"
            )).setValue("No")

            transform = UI4.FormMaster.CreateParameterPolicy(None, sphere.getParameter(
                "transform.translate"
            )).setValue([-1.5,
                            3.0,
                            0])
        elif sphereType == "chrome":
            nameSet = sphere.getParameter("name").setValue("/root/world/LookDevScene/chromeSphere", 0)

            setInteractive = UI4.FormMaster.CreateParameterPolicy(None, sphere.getParameter(
                "makeInteractive"
            )).setValue("No")

            transform = UI4.FormMaster.CreateParameterPolicy(None, sphere.getParameter(
                "transform.translate"
            )).setValue([1.5,
                        3.0,
                        0])
        else:
            return sphere
        
        return sphere

    def _shaderBallMaterial(root, sphereType):

        material = Utils.shadingNodeCreate("dlPrincipled", root)
        
        if sphereType == "chrome":
            
            base = UI4.FormMaster.CreateParameterPolicy(None, material.getParameter(
                "parameters.color"
            )).setValue([1,
                            1,
                            1])

            roughness = UI4.FormMaster.CreateParameterPolicy(None, material.getParameter(
                "parameters.roughness"
            )).setValue(0)

            metallic = UI4.FormMaster.CreateParameterPolicy(None, material.getParameter(
                "parameters.metallic"
            )).setValue(1)
        elif sphereType == "grey":
        
            base = UI4.FormMaster.CreateParameterPolicy(None, material.getParameter(
                "parameters.color"
            )).setValue([0.18,
                        0.18,
                        0.18])

            roughness = UI4.FormMaster.CreateParameterPolicy(None, material.getParameter(
                "parameters.roughness"
            )).setValue(1)
        else:
            internalConnection = Utils.nmcConnect(root, material, "dlSurface")
            return material

            
        internalConnection = Utils.nmcConnect(root, material, "dlSurface")

        return material
        
    def _macbethChartGeo(root):
        chart = Utils.geoCreate('poly plane', root)
        nameSet = chart.getParameterValue("name").setValue(
            "/root/world/LookDevScene/colorChart", 0
        )
        
        makeInteractive = UI4.FormMaster.CreateParameterPolicy(None, chart.getParameter(
            "makeInteractive"
        )).setValue("No")
        
        transform = UI4.CreateParameterPolicy(None, chart.getParameter(
            "transform.translate"
        )).setValue([90,
                    0,
                    0])
        
        scale = UI4.CreateParameterPolicy(None, chart.getParameters(
            "transform.scale"
        )).setValue([5.0,
                    3.0,
                    3.0])
        
        return chart

    def _chartMaterial(self, root):
        material = Utils.shadingNodeCreate("dlPrincipled", root)
        
        textureNode = Utils.shadingNodeCreate("file", root)
        place2d = Utils.shadingNodeCreate("place2dTexture", root)

        texturePath = os.getcwd() + "assets\sRGB_ColorChecker.tdl"
        importTexture = UI4.FormMaster.CreateParameterPolicy(None, textureNode.getParameter(
            "parameters.fileTextureName"
        )).setValue(str(texturePath))

        internalConnection = Utils.nmcConnect(root, material, "dlsurface")
        Utils.connectTwoNodes(place2d, textureNode, "outUV", "uvCoord")
        Utils.connectTwoNodes(textureNode, material, "outColor", "color")

        return material
        
    def _backdropPrim(self, root):
        assetPath = os.getcwd() + "assets\ground.abc"
        backdropImport = NodegraphAPI.CreateNode("Alembic_In", root)
        name = UI4.FormMaster.CreateParameterPolicy(None, backdropImport.getParameter(
            "name"
        )).setValue("/root/world/backdrop", 0)

        fileIn = UI4.CreateParameterPolicy(None, backdropImport.getParameter(
            "absAsset"
        )).setValue(str(assetPath))

        return backdropImport

    def _backdropMaterial(self, root):
        material = Utils.shadingNodeCreate("dlPrincipled", root)
        roughness = UI4.CreateParameterPolicy(None, material.getParameter(
            "parameters.roughness"
        )).setValue(1)
        specular = UI4.CreateParameterPolicy(None, material.getParameter(
            "parameters.specular_level"
        )).setValue(0)
        
        textureNode = Utils.shadingNodeCreate("file", root)
        place2d = Utils.shadingNodeCreate("place2dTexture", root)

        texturePath = os.getcwd() + "assets\Floor_Color_50percent.tdl"
        importTexture = UI4.FormMaster.CreateParameterPolicy(None, textureNode.getParameter(
            "parameters.fileTextureName"
        )).setValue(str(texturePath))

        internalConnection = Utils.nmcConnect(root, material, "dlsurface")
        Utils.connectTwoNodes(place2d, textureNode, "outUV", "uvCoord")
        Utils.connectTwoNodes(textureNode, material, "outColor", "color")

        return material

    def _lookDevGroup(self, group, nmc):
        group = group

        parentNmc = nmc

        # grey sphere setup
        greySphere = self._shaderBall(group, "grey")
        greyLocation = greySphere.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        greySubdiv = Utils.subDivideMesh(greyLocation, group)
        greyMaterial = self._shaderBallMaterial(parentNmc, "grey")
        Utils.nmcConnect(parentNmc, greySphere, "dlSurface")
        Utils.connectTwoNodes(greySphere, greySubdiv, "out", "in")

        # chrome sphere setup
        chromeSphere = self._shaderBall(group, "chrome")
        chromeLocation = chromeSphere.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        chromeSubdiv = Utils.subDivideMesh(chromeLocation, group)
        chromeMaterial = self._shaderBallMaterial(parentNmc, "chrome")
        Utils.nmcConnect(parentNmc, chromeMaterial, "dlSurface")
        Utils.connectTwoNodes(chromeSphere, chromeSubdiv, "out", "in")

        # macbeth chart setup
        chart = self._macbethChartGeo(group)
        chartLocation = chart.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        chartSubdiv = Utils.subDivideMesh(chartLocation)
        chartMaterial = self._chartMaterial(parentNmc)
        Utils.nmcConnect(parentNmc, chartMaterial, "dlSurface")
        Utils.connectTwoNodes(chart, chartSubdiv, "out", "in")

        # merging everything together
        self.primMerge = Utils.multiMerge([greySphere,
                                    chromeSphere,
                                    chart], group)
        self.nmcMerge = Utils.multiMerge([self.primMerge, parentNmc], group)

        #creating material assigns
        greyMatAssign = Utils.materialAssignSetup(greyLocation, greyMaterial, group)
        chromeMatAssign = Utils.materialAssignSetup(chromeLocation, chromeMaterial, group)
        self.chartMatAssign = Utils.materialAssignSetup(chartLocation, chartMaterial, group)

        #connecting everything
        Utils.connectTwoNodes(self.nmcMerge, greyMatAssign, "out", "in")
        Utils.connectTwoNodes(greyMatAssign, chromeMatAssign, "out", "in")
        Utils.connectTwoNodes(chromeMatAssign, self.chartMatAssign, "out", "in")

        return group

    def _backdropSetup(self, parentGroup, parentNmc):
        group = parentGroup
        nmc = parentNmc

        if self._enableBackdrop.isChecked() and self._enableAll.isChecked() == True:
            
            backdrop = self._backdropPrim(group)
            backdropLocation = backdrop.getParameterValue('name', NodegraphAPI.GetCurrentTime())
            subdiv = Utils.subDivideMesh(backdropLocation, group)
            Utils.connectTwoNodes(backdrop, subdiv, "out", "in")

            backdropMat = self._backdropMaterial(parentNmc)
            self.backdropMatAssign = Utils.materialAssignSetup(backdropLocation, backdropMat)
            lookdevSetup = self._lookDevGroup()

            Utils.nmcConnect(nmc, self.backdropMat, "dlSurface")

            primMerge = self.primMerge.addInputPort("i3")
            Utils.connectTwoNodes(subdiv, primMerge, "out", "i3")
            Utils.connectTwoNodes(self.chartMatAssign, self.backdropMatAssign, "out", "in")

            return group
        elif self._enableBackdrop.isChecked() and not self._enableAll.isChecked():







