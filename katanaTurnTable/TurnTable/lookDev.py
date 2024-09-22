import os
from Katana import UI4
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

def _chartMaterial(root):
    material = Utils.shadingNodeCreate("dlPrincipled", root)
    
    textureNode = Utils.shadingNodeCreate("file", root)
    place2d = Utils.shadingNodeCreate("place2dTexture", root)

    # TODO: figure out how to get file path for assets folder
    texturePath = "help??"
    importTexture = UI4.FormMaster.CreateParameterPolicy(None, textureNode.getParameter(
        "parameters.fileTextureName"
    )).setValue(str(texturePath))

    internalConnection = Utils.nmcConnect(root, material, "dlsurface")
    Utils.connectTwoNodes(place2d, textureNode, "outUV", "uvCoord")
    Utils.connectTwoNodes(textureNode, material, "outColor", "color")

    return material

'''
 TODO: Move over the functions for the backdrop then add them to turntable.py
'''        
    



