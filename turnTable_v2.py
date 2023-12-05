import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

def geoCreate(primitiveType, parent):
    primitiveCreate = NodegraphAPI.CreateNode('PrimitiveCreate', parent)
    changePrimType = UI4.FormMaster.CreateParameterPolicy(None, primitiveCreate.getParameter('type'))
    changePrimType.setValue(primitiveType, 0)

    return primitiveCreate

def shadingNodeCreate(nodeType, parent, dlShadingNodeType = 'DlShadingNode'):
    dlPrincipled = NodegraphAPI.CreateNode(dlShadingNodeType, parent)
    dlPrincipled.getParameter('nodeType').setValue(nodeType, 0)
    dlPrincipled.getParameter('name').setValue(nodeType, 0)
    dlPrincipled.checkDynamicParameters()
    
    return dlPrincipled


def materialAssignSetup(assetLocation, material, parent):
    
    materialAssign = NodegraphAPI.CreateNode('MaterialAssign', parent)
    materialAssign.getParameter('CEL').setValue(assetLocation, 0)
    materialAssign.getParameter('args.materialAssign.enable').setValue(1, 0)
    materialAssign.getParameter('args.materialAssign.value').setValue(material, 0)

    return materialAssign


def groupNodeSetup(parent):
    group = NodegraphAPI.CreateNode('Group', parent)
    group.addOutputPort('groupOut')
    groupReturn = group.getReturnPort('out')

    return group

# ---------------------------------------------------------------------------------------------------
# ------------------------------ Functions for connecting nodes together ----------------------------
# ---------------------------------------------------------------------------------------------------

def nmcConnect(networkMaterial, shadingNode, terminalInput):

    if networkMaterial.getType() == 'NetworkMaterialCreate':
        terminal = networkMaterial.getNetworkMaterials()[0]
        terminalIn = terminal.getInputPort(terminalInput)
    elif networkMaterial.getType() == 'NetworkMaterial':
        terminalIn = networkMaterial.addInputPort(terminalInput)
    
    shadingNodeOut = shadingNode.getOutputPort('outColor')
    terminalIn.connect(shadingNodeOut)

    print(networkMaterial.getParameter('NodeType') == 'NetworkMaterialCreate')


def connectTwoNodes(nodeOutput, nodeInput, outValue, inValue):

    nodeOutPort = nodeOutput.getOutputPort(outValue)
    nodeInPort = nodeInput.getInputPort(inValue)

    nodeOutPort.connect(nodeInPort)
    

def multiMerge (nodesToMerge, parent):
    mergeNode = NodegraphAPI.CreateNode('Merge', parent)

    for node in nodesToMerge:
        outputPort = node.getOutputPort('out')
        mergeInput = mergeNode.addInputPort('i')
        outputPort.connect(mergeInput)
    return mergeNode

# ---------------------------------------------------------------------------------------------------
# --------------------------------- Additional helpful functions ------------------------------------
# ---------------------------------------------------------------------------------------------------

def getMaterialPath(networkMaterialNode):

        
    materialName = networkMaterialNode.getParameterValue('name', NodegraphAPI.GetCurrentTime())

    nmc = networkMaterialNode.getParent()
    nmcRootLocation = nmc.getParameterValue('rootLocation', NodegraphAPI.GetCurrentTime())

    materialPath = nmcRootLocation + "/" + materialName

    return materialPath


def subDivideMesh( meshToSubdivide, parent):
    attributeSet = NodegraphAPI.CreateNode('AttributeSet', parent)
    meshLocation = meshToSubdivide.getParameterValue('name', NodegraphAPI.GetCurrentTime())
    path = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('paths.i0'))
    path.setValue(meshLocation)

    attributeName = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('attributeName'))
    attributeName.setValue('Type')

    attributeType = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('attributeType'))
    attributeType.setValue('string')

    subdivideMesh = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('stringValue.i0'))
    subdivideMesh.setValue('subdmesh')

    return attributeSet





class TurntableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.root = NodegraphAPI.GetRootNode()
        self.createWindow()
    
    def createWindow(self):

        self.setGeometry(250, 250, 500, 250)
        self.setWindowTitle('Please work')

        self.populateUI()
        self.show()
    
    def populateUI(self):
        
        mainLayout = QGridLayout()
        mainLayout.setVerticalSpacing(15)

        skydomeLayout = QGridLayout()
        skydomeLayout.setVerticalSpacing(7)


        # creating the file browser
        assetLabel = QLabel("Path to Asset")
        self.assetPath = QLineEdit()

        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.assetBrowser)

        # adding the Skydome layout

        self.skydomeSetup = SkydomeSetup(skydomeLayout)

        # adding camera layout

        self.cameraSetup = CameraSettings()

        # adding the LookDev Layout

        self.lookDevSetup = LookDevSetup()

        # create turntable button
        self.createTurnTable = QPushButton("Create Turn Table")
        self.createTurnTable.clicked.connect(self.generateTT)


        # adding asset browser to the UI layout
        mainLayout.addWidget(assetLabel, 0, 0, 1, 1)
        mainLayout.addWidget(self.assetPath, 0, 1, 1, 6)
        mainLayout.addWidget(self.searchButton, 0, 7, 1, 1)
        # adding additional widgets
        mainLayout.addWidget(self.skydomeSetup, 1, 0, 1, 8)
        mainLayout.addWidget(self.cameraSetup, 2, 0, 1, 8)
        mainLayout.addWidget(self.lookDevSetup, 3, 0, 1, 8)
        mainLayout.addWidget(self.createTurnTable, 4, 0, 1, 8)
        self.show()
        self.setLayout(mainLayout)

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
    
    def dollyConstraintCreate(self, cameraPath, assetPath, offsetAmount):
        dollyConstraint = NodegraphAPI.CreateNode('DollyConstraint', self.root)

        dollyBasePath = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('basePath'))
        dollyBasePath.setValue(cameraPath)
        
        dollyTargetPath = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('targetPath.i0'))
        dollyTargetPath.setValue(assetPath)

        dollyTargetBounds = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('targetBounds'))
        dollyTargetBounds.setValue('sphere')

        dollyOffsetAngle = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('angleOffset'))
        dollyOffsetAngle.setValue(offsetAmount)

        return dollyConstraint

    
    def generateTT(self):

        if self.lookDevSetup.enableGrey.isChecked() or self.lookDevSetup.enableChrome.isChecked() or self.lookDevSetup.enableChart.isChecked() or self.lookDevSetup.enableAll.isChecked() == True:
            networkMaterialCreate = NodegraphAPI.CreateNode('NetworkMaterialCreate', self.root)
            nmcTerminal = getMaterialPath(networkMaterialCreate.getNetworkMaterials()[0])

        if self.lookDevSetup.enableGrey.isChecked():
            greySphereSetup = self.lookDevSetup.createGreyBall(networkMaterialCreate, nmcTerminal, self.root)
        
        if self.lookDevSetup.enableChrome.isChecked():
            chromeSphereSetup = self.lookDevSetup.createChromeBall(networkMaterialCreate, nmcTerminal, self.root)
        
        if self.lookDevSetup.enableChart.isChecked():
            chartSetup = self.lookDevSetup.createMacbethChart(networkMaterialCreate, nmcTerminal, self.root)

        if self.lookDevSetup.enableGrey.isChecked() and self.lookDevSetup.enableChrome.isChecked():
            multiSetup = self.lookDevSetup.multiSetup(networkMaterialCreate, self.root)

        alembicCreate = NodegraphAPI.CreateNode('Alembic_In', self.root)
        assetSet = UI4.FormMaster.CreateParameterPolicy(None, alembicCreate.getParameter('abcAsset'))
        assetSet.setValue(str(self.assetPath.text()))

        assetLocation = alembicCreate.getParameterValue('name', NodegraphAPI.GetCurrentTime())

        camera = NodegraphAPI.CreateNode('CameraCreate', self.root)
        
        
        cameraFOV = UI4.FormMaster.CreateParameterPolicy(None, camera.getParameter('fov'))
        if self.cameraSetup.FOVValue.text() != 70:
            cameraFOV.setValue(self.cameraSetup.FOVValue.text())


        makeInteractive = UI4.FormMaster.CreateParameterPolicy(None, camera.getParameter('makeInteractive'))

        if self.cameraSetup.makeCamInteractive.setCheckable(False):
            makeInteractive.setValue('No')
        else:
            makeInteractive.setValue('Yes')
        

        camLocation = camera.getParameterValue('name', NodegraphAPI.GetCurrentTime())

        # creates nmc containing material that will be assigned to the asset
        assetNMC = NodegraphAPI.CreateNode('NetworkMaterialCreate', self.root)
        assetMaterialLocation = getMaterialPath(assetNMC.getNetworkMaterials()[0])

        assetShader = shadingNodeCreate('dlPrincipled', assetNMC)
        assetBaseColor = UI4.FormMaster.CreateParameterPolicy(None, assetShader.getParameter('parameters.color'))
        assetBaseColor.setValue([0.18,
                                 0.18,
                                 0.18])

        shaderConnect = nmcConnect(assetNMC, assetShader, 'dlSurface')


        # merging the geo, camera and NMC all together

        camAssetMerge = multiMerge([alembicCreate, camera, assetNMC], self.root)


        # creating the material assign and then connecting it

        assetMaterialAssign = materialAssignSetup(assetLocation, assetMaterialLocation, self.root)
        nmcIntoAssign = connectTwoNodes(camAssetMerge, assetMaterialAssign, 'out', 'input')
        
        # creates the dolly constraint and then connects it
        dollyConstraint = self.dollyConstraintCreate(camLocation, assetLocation, self.cameraSetup.setDistance.text())
        assignIntoDolly = connectTwoNodes(assetMaterialAssign, dollyConstraint, 'out', 'input')

        # creates render settings node and assigns the camera resolution
        # based on the selection in the UI's dropdown

        renderSettings = NodegraphAPI.CreateNode('RenderSettings', self.root)

        camResolution = UI4.FormMaster.CreateParameterPolicy(None, renderSettings.getParameter('args.renderSettings.resolution'))
        camResolution.setValue(str(self.cameraSetup.camResDropdown.currentText()))

        screenAdjustment = UI4.FormMaster.CreateParameterPolicy(None, renderSettings.getParameter('args.renderSettings.adjustScreenWindow'))
        screenAdjustment.setValue(str(self.cameraSetup.screenDropDown.currentText()))

        renderInput = renderSettings.getInputPort('input')

        
        # if the 'use skydome' check box is checked, create a skydome
        # note to self: the line in the if statement is calling a function
        # from within the SkydomeSetup class

        if self.skydomeSetup.useSkydome.isChecked():
            skydome = self.skydomeSetup.createSkydome(self.root)
            
            dollyToSkydome = connectTwoNodes(dollyConstraint, skydome, 'out', 'in')
            skydomeToRenderSettings = connectTwoNodes(skydome, renderSettings, 'out', 'input')
            
            lightMat = self.skydomeSetup.envLightMaterial(skydome)
            
            
            if self.skydomeSetup.intensityValue.text() != 0.00:
                intensity = UI4.FormMaster.CreateParameterPolicy(None, lightMat.getParameter('shaders.dlEnvironmentParams.intensity'))
                intensity.setValue(self.skydomeSetup.intensityValue.text())
            if self.skydomeSetup.exposureValue.text() != 0.00:
                exposure = UI4.FormMaster.CreateParameterPolicy(None, lightMat.getParameter('shaders.dlEnvironmentParams.exposure'))
                exposure.setValue(self.skydomeSetup.exposureValue.text())
        else:
            # if the checkbox is not checked, 
            dollyConnect = connectTwoNodes(dollyConstraint, renderSettings, 'out', 'input')

        # if the use texture checkbox in the Skydome tab is checked:
        if self.skydomeSetup.useTexture.isChecked():
            texturePath = UI4.FormMaster.CreateParameterPolicy(None, lightMat.getParameter('shaders.dlEnvironmentParams.image'))
            texturePath.setValue(str(self.skydomeSetup.texturePath.text()))

            colorSpace = UI4.FormMaster.CreateParameterPolicy(None, lightMat.getParameter('shaders.dlEnvironmentParams.image_meta_colorspace'))
            colorSpace.setValue(str(self.skydomeSetup.selectColorspace.currentText()))

        allNodes = NodegraphAPI.GetAllNodes()
        NodegraphAPI.ArrangeNodes(allNodes, nodeGraphLengthSpacing = 250, nodeGraphWidthSpacing = 100)

        
        


class SkydomeSetup(QWidget):
    def __init__(self, parentLayout):
        super().__init__()
        self.parentLayout = parentLayout
        self.root = NodegraphAPI.GetRootNode()
        self.createModule()
    
    def createModule(self):

        # path to texture

        texturePathLabel = QLabel("Path to Texture")
        self.texturePath = QLineEdit()
        self.searchTexture = QPushButton("Search")
        self.searchTexture.clicked.connect(self.textureBrowser)

        colorSpaceList = ['auto',
                          'sRGB',
                          'Rec. 709',
                          'linear']
        colorSpace = QLabel("Set Colorspace")
        self.selectColorspace = UI4.Widgets.QtWidgets.QComboBox()
        self.selectColorspace.addItems(colorSpaceList)

        mappingParams = ["Spherical (latlong)",
                        "Angular"]
        
        mapping = QLabel("Set Mapping Type")
        self.mappingDrowdown = UI4.Widgets.QtWidgets.QComboBox()
        self.mappingDrowdown.addItems(mappingParams)

        self.useTexture = QCheckBox("Use HDRI")
        self.useSkydome = QCheckBox("Use Skydome")

        # light intensity

        intensityLabel = QLabel("Light Instensity")
        self.intensityValue = QDoubleSpinBox()
        self.intensityValue.setMinimum(-99.99)
        self.intensityValue.setMaximum(1000.00)
        self.intensitySlider = UI4.Widgets.QT4Widgets.SliderWidget(self)
        self.intensitySlider.setRange(0, 10)
        self.intensitySlider.valueChanged.connect(self.intensityChanged)

        # light exposure
        exposureLabel = QLabel("Light Exposure")
        self.exposureValue = QDoubleSpinBox()
        self.exposureValue.setMinimum(-99.99)
        self.exposureValue.setMaximum(1000.00)
        self.exposureSlider = UI4.Widgets.QT4Widgets.SliderWidget(self)
        self.exposureSlider.setRange(-5, 10)
        self.exposureSlider.valueChanged.connect(self.exposureChanged)

        # Assign a texture to the Light
        self.parentLayout.addWidget(texturePathLabel, 0, 0)
        self.parentLayout.addWidget(self.texturePath, 0, 1, 1, 6)
        self.parentLayout.addWidget(self.searchTexture, 0, 7, 1, 1)
        
        # Set Light's colorspace
        self.parentLayout.addWidget(colorSpace, 3, 0)
        self.parentLayout.addWidget(self.selectColorspace, 3, 1, 1, 7)
        self.parentLayout.addWidget(mapping, 4, 0)
        
        # Set the texture image's mapping type
        self.parentLayout.addWidget(self.mappingDrowdown, 4, 1, 1, 7)
        self.parentLayout.addWidget(self.useTexture, 5, 7, 1, 1, Qt.AlignLeft)

        # Light intensity Settings
        self.parentLayout.addWidget(intensityLabel, 6, 0)
        self.parentLayout.addWidget(self.intensityValue, 6, 1, 1, 1, Qt.AlignLeft)
        self.parentLayout.addWidget(self.intensitySlider, 6, 2, 1, 6)
        

        # Light Exposure Settings
        self.parentLayout.addWidget(exposureLabel, 7, 0, 1, 1)
        self.parentLayout.addWidget(self.exposureValue, 7, 1, 1, 1, Qt.AlignLeft)
        self.parentLayout.addWidget(self.exposureSlider, 7, 2, 1, 6)

        self.parentLayout.addWidget(self.useSkydome, 8, 7, 1, 1, Qt.AlignLeft)

        self.show()
        self.setLayout(self.parentLayout)
    
    # Opens a file browser when search button is clicked
    # then adds the image path to the search bar

    def textureBrowser(self):
                
        self.filePath = QFileDialog.getOpenFileName(self, "Select Asset",)

        if self.filePath:
            self.texturePath.insert(self.filePath[0])

    # when the sliders for intensity/exposure are changed, the
    # spin boxes update to reflect that

    def intensityChanged(self):
        value = self.intensitySlider.getValue()
        self.intensityValue.setValue(value)
    
    def exposureChanged(self):
        value = self.exposureSlider.getValue()
        self.exposureValue.setValue(value)

    # creates a gaffer three containing a skydome

    def createSkydome(self, parent):
        gafferThree = NodegraphAPI.CreateNode("GafferThree", parent)
        rootPackage = gafferThree.getRootPackage()
        rootPackage.createChildPackage('EnvironmentLightPackage', 'envLight')

        light = rootPackage.getChildPackage('envLight')
        lightMatNode = light.getMaterialNode()
        lightShader = lightMatNode.addShaderType('dlEnvironmentShader')

        setEnvLight = UI4.FormMaster.CreateParameterPolicy(None, lightMatNode.getParameter('shaders.dlEnvironmentShader'))
        setEnvLight.setValue("environmentLight")
        lightMatNode.checkDynamicParameters()

        return gafferThree
    
    # grabs the material node inside the gaffer three

    def envLightMaterial(self, gafferToEdit):
        
        rootPkg = gafferToEdit.getRootPackage()
        lightPkg = rootPkg.getChildPackage('envLight')
        lightMat = lightPkg.getMaterialNode()
        lightMat.checkDynamicParameters()

        return lightMat

class CameraSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.parentLayout = QGridLayout()
        self.createModule()
    
    def createModule(self):
        
        cameraSettingsHeader = QLabel("Camera Settings")
        camFOVLabel = QLabel('FOV Amount')
        self.FOVValue = QSpinBox()
        self.FOVValue.setValue(70)
        self.FOVValue.setMaximum(1000)
        
        self.makeCamInteractive = QCheckBox('Lock Camera')
        
        camResolution = QLabel("Resolution")
        self.camResDropdown = UI4.Widgets.ResolutionComboBox(self)
        

        adjustmentTypes = ['No adjustment',
                           'Adjust height to match resolution',
                           'Adjust width to match resolution']
        
        screenWindow = QLabel("Window Adjustment")
        self.screenDropDown = UI4.Widgets.QtWidgets.QComboBox()
        self.screenDropDown.addItems(adjustmentTypes)

        distanceLabel = QLabel('Camera Distance')
        self.setDistance = QSpinBox()
        self.setDistance.setMinimum(0)
        self.setDistance.setMaximum(1000)


        self.parentLayout.addWidget(cameraSettingsHeader, 0, 0)
        self.parentLayout.addWidget(camFOVLabel, 1, 0)
        self.parentLayout.addWidget(self.FOVValue, 1, 1, 1, 1, Qt.AlignLeft)
        self.parentLayout.addWidget(distanceLabel, 1, 3, 1, 1, Qt.AlignLeft)
        self.parentLayout.addWidget(self.setDistance, 1, 4, 1, 1)
        self.parentLayout.addWidget(camResolution, 2, 0)
        self.parentLayout.addWidget(self.camResDropdown, 2, 1, 1, 7)
        self.parentLayout.addWidget(screenWindow, 3, 0)
        self.parentLayout.addWidget(self.screenDropDown, 3, 1, 1, 7)
        self.parentLayout.addWidget(self.makeCamInteractive, 4, 7)
        
        self.show()
        self.setLayout(self.parentLayout)

class LookDevSetup(QWidget):
    def __init__(self):
        super().__init__()
        self.createUI()
    
    def createUI(self):

        layout = QGridLayout()
        layout.setVerticalSpacing(15)

        lookdevHeading = QLabel("Look Development Assets")

        backgrounds = QLabel("Backgrounds")

        self.enablePlatform = QCheckBox("Enable Platform")
        self.enableBackdrop = QCheckBox("Backdrop")

        lookdevTools = QLabel("LookDev Tools")

        self.enableGrey = QCheckBox("Enable Grey Ball")
        self.enableChrome = QCheckBox("Enable Chrome Ball")
        self.enableChart = QCheckBox("Enable Macbeth Chart")
        self.enableAll = QCheckBox("Enable All")


        layout.addWidget(lookdevHeading, 0, 0)
        layout.addWidget(backgrounds, 1, 0)
        layout.addWidget(self.enablePlatform, 2, 0)
        layout.addWidget(self.enableBackdrop, 2, 1)
        layout.addWidget(lookdevTools, 3, 0)
        layout.addWidget(self.enableGrey, 4, 0)
        layout.addWidget(self.enableChrome, 4, 1)
        layout.addWidget(self.enableChart, 4, 2)
        layout.addWidget(self.enableAll, 5, 1, Qt.AlignCenter)

        self.show()
        self.setLayout(layout)
    
    def createGreyBall(self, nmc, nmcLocation, parent):
        networkMaterialCreate = nmc

        self.greySphere = geoCreate('poly sphere', parent)
        greyNameSet = self.greySphere.getParameter('name').setValue('/root/world/geo/greySphere', 0)
        greySphereLocation = self.greySphere.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        greySphereInteractive = UI4.FormMaster.CreateParameterPolicy(None, self.greySphere.getParameter('makeInteractive'))
        greySphereInteractive.setValue('No')

        self.greySphereTransform = NodegraphAPI.CreateNode('Transform3D', parent)
        transformPath = UI4.FormMaster.CreateParameterPolicy(None, self.greySphereTransform.getParameter('path'))
        transformPath.setValue(greySphereLocation)
        transformTranslate = UI4.FormMaster.CreateParameterPolicy(None, self.greySphereTransform.getParameter('translate'))
        transformTranslate.setValue([-1.5,
                                     3.0,
                                     0])
        transformInteractive = UI4.FormMaster.CreateParameterPolicy(None, self.greySphereTransform.getParameter('makeInteractive'))
        transformInteractive.setValue('No')
        
        primitiveIntoTransform = connectTwoNodes(self.greySphere, self.greySphereTransform, 'out', 'in')

        self.greyAttributeSet = subDivideMesh(self.greySphere, parent)

        greyAttributeConnect = connectTwoNodes(self.greySphereTransform, self.greyAttributeSet, 'out', 'A')

        # setting up the material
        greyMat = shadingNodeCreate('dlPrincipled', networkMaterialCreate)
        greyBaseColor = UI4.FormMaster.CreateParameterPolicy(None, greyMat.getParameter('parameters.color'))
        greyBaseColor.setValue([0.18,
                                0.18,
                                0.18])
        greyRoughness = UI4.FormMaster.CreateParameterPolicy(None, greyMat.getParameter('parameters.roughness'))
        greyRoughness.setValue(1)

        greyConnectInsideNMC = nmcConnect(networkMaterialCreate, greyMat, 'dlSurface')

        self.greyGeoNMCMerge = multiMerge([self.greyAttributeSet, networkMaterialCreate], parent)

        self.greyMaterialAssign = materialAssignSetup(greySphereLocation, nmcLocation, parent)
        self.greyMaterialIntoAssign = connectTwoNodes(self.greyGeoNMCMerge, self.greyMaterialAssign, 'out', 'input')
    
    def createChromeBall(self, nmc, nmcLocation, parent):
        networkMaterialCreate = nmc

        self.chromeSphere = geoCreate('poly sphere', parent)
        chromeNameSet = self.chromeSphere.getParameter('name').setValue('/root/world/geo/chromeSphere', 0)
        chromeSphereLocation = self.chromeSphere.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        chromeSphereInteractive = UI4.FormMaster.CreateParameterPolicy(None, self.chromeSphere.getParameter('makeInteractive'))
        chromeSphereInteractive.setValue('No')

        self.chromeSphereTransform = NodegraphAPI.CreateNode('Transform3D', parent)
        transformPath = UI4.FormMaster.CreateParameterPolicy(None, self.chromeSphereTransform.getParameter('path'))
        transformPath.setValue(chromeSphereLocation)
        transformTranslate = UI4.FormMaster.CreateParameterPolicy(None, self.chromeSphereTransform.getParameter('translate'))
        transformTranslate.setValue([1.5,
                                     3.0,
                                     0])
        transformInteractive = UI4.FormMaster.CreateParameterPolicy(None, self.chromeSphereTransform.getParameter('makeInteractive'))
        transformInteractive.setValue('No')
        
        primitiveIntoTransform = connectTwoNodes(self.chromeSphere, self.chromeSphereTransform, 'out', 'in')

        self.chromeAttributeSet = subDivideMesh(self.chromeSphere, parent)

        chromeAttributeConnect = connectTwoNodes(self.chromeSphereTransform, self.chromeAttributeSet, 'out', 'A')

        if self.enableGrey.isChecked() == True:
            chromeNetworkMaterial = NodegraphAPI.CreateNode('NetworkMaterial', nmc)
            chromeMaterialLocation = getMaterialPath(chromeNetworkMaterial)
        else:
            chromeMaterialLocation = nmcLocation
        
        chromeMaterial = shadingNodeCreate('dlPrincipled', nmc)

        chromeMaterialColor = UI4.FormMaster.CreateParameterPolicy(None, chromeMaterial.getParameter('parameters.color'))
        chromeMaterialColor.setValue([1,
                                      1,
                                      1])
        chromeMaterialRoughness = UI4.FormMaster.CreateParameterPolicy(None, chromeMaterial.getParameter('parameters.roughness'))
        chromeMaterialRoughness.setValue(0)
        chromeMaterialMetallic = UI4.FormMaster.CreateParameterPolicy(None, chromeMaterial.getParameter('parameters.metallic'))
        chromeMaterialMetallic.setValue(1)
        

        if self.enableGrey.isChecked() == True:
            chromeConnectInsideNMC = nmcConnect(chromeNetworkMaterial, chromeMaterial, 'dlSurface')
        else:
            chromeConnectInsideNMC = nmcConnect(nmc, chromeMaterial, 'dlSurface')

        if self.enableGrey.isChecked() != True:
            self.chromeMaterialMerge = multiMerge([self.chromeAttributeSet, nmc], parent)
            self.chromeMaterialAssign = materialAssignSetup(chromeSphereLocation, chromeMaterialLocation, parent)
            chromeMaterialIntoAssign = connectTwoNodes(self.chromeMaterialMerge, self.chromeMaterialAssign, 'out', 'input')

    def createMacbethChart(self, nmc, nmcLocation, parent):
        networkMaterialCreate = nmc

        self.chart = geoCreate('poly plane', parent)
        chartNameSet = self.chart.getParameter('name').setValue('/root/world/geo/colorChart', 0)
        chartLocation = self.chart.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        chartInteractive = UI4.FormMaster.CreateParameterPolicy(None, self.chart.getParameter('makeInteractive'))
        chartInteractive.setValue('No')

        self.chartTransform = NodegraphAPI.CreateNode('Transform3D', parent)
        transformPath = UI4.FormMaster.CreateParameterPolicy(None, self.chartTransform.getParameter('path'))
        transformPath.setValue(chartLocation)
        transformRotate = UI4.FormMaster.CreateParameterPolicy(None, self.chartTransform.getParameter('rotate'))
        transformRotate.setValue([90,
                                  0,
                                  0])
        transformScale = UI4.FormMaster.CreateParameterPolicy(None, self.chartTransform.getParameter('scale'))
        transformScale.setValue([5,
                                 0,
                                 3])
        transformInteractive = UI4.FormMaster.CreateParameterPolicy(None, self.chart.getParameter('makeInteractive'))
        transformInteractive.setValue('No')

        geoIntoTransform = connectTwoNodes(self.chart, self.chartTransform, 'out', 'in')

        if self.enableGrey.isChecked() or self.enableChrome.isChecked() == True:
            chartNetworkMaterial = NodegraphAPI.CreateNode('NetworkMaterial', nmc)
            chartMaterialLocation = getMaterialPath(chartNetworkMaterial)
        else:
            chartMaterialLocation = nmcLocation
        
        chartMaterial = shadingNodeCreate('dlPrincipled', nmc)
        chartTexture = shadingNodeCreate('dlTexture', nmc)
        placeTexture = shadingNodeCreate('place2dTexture', nmc)

        uvCoordsIntoTexture = connectTwoNodes(placeTexture, chartTexture, 'outUV', 'uvCoord')
        textureIntoSurface = connectTwoNodes(chartTexture, chartMaterial, 'outColor', 'color')
        
        
        if self.enableGrey.isChecked() or self.enableChrome.isChecked() == True:
            chartConnectInsideNMC = nmcConnect(chartNetworkMaterial, chartMaterial, 'dlSurface')
        else:
            chartConnectInsideNMC = nmcConnect(nmc, chartMaterial, 'dlSurface')

        '''
        if self.enableGrey.isChecked() or self.enableChrome.isChecked() != True:
            self.chromeMaterialMerge = multiMerge([self.chromeAttributeSet, nmc], parent)
            self.chromeMaterialAssign = materialAssignSetup(chromeSphereLocation, chromeMaterialLocation, parent)
            chromeMaterialIntoAssign = connectTwoNodes(self.chromeMaterialMerge, self.chromeMaterialAssign, 'out', 'input')
        '''
    def multiSetup(self, nmc, parent):

        lookdevGroup = groupNodeSetup(parent)
        primGroup = groupNodeSetup(lookdevGroup)

        self.greySphere.setParent(primGroup)
        self.greySphereTransform.setParent(primGroup)
        self.greyAttributeSet.setParent(primGroup)

        self.chromeSphere.setParent(primGroup)
        self.chromeSphereTransform.setParent(primGroup)
        self.chromeAttributeSet.setParent(primGroup)
        
        nmc.setParent(primGroup)

        self.greyGeoNMCMerge.setParent(primGroup)
        if self.enableGrey.isChecked() and self.enableChrome.isChecked():
            addMergePort = self.greyGeoNMCMerge.addInputPort('i2')
            chromeMergeOut = self.chromeAttributeSet.getOutputPort('out')
            addMergePort.connect(chromeMergeOut)
        
        nmcOut = self.greyGeoNMCMerge.getOutputPort('out')
        primGroupReturn = primGroup.getReturnPort('groupOut')

        nmcOut.connect(primGroupReturn)

        materialAssignStack = NodegraphAPI.CreateNode('GroupStack', lookdevGroup)

        self.greyMaterialAssign.setParent(materialAssignStack)

        groupOut = connectTwoNodes(primGroup, materialAssignStack, 'groupOut', 'in')






open = TurntableWindow()