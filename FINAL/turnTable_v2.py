import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os

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


def subDivideMesh( meshLocation, parent):
    attributeSet = NodegraphAPI.CreateNode('AttributeSet', parent)
    path = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('paths.i0'))
    path.setValue(meshLocation)

    attributeName = UI4.FormMaster.CreateParameterPolicy(None, attributeSet.getParameter('attributeName'))
    attributeName.setValue('type')

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
        self.setWindowTitle("Adele's TurnTable Window!")

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
    
    
    def dollyConstraintCreate(self, cameraPath, assetPath, offsetAmount):
        dollyConstraint = NodegraphAPI.CreateNode('DollyConstraint', self.root)

        dollyBasePath = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('basePath'))
        dollyBasePath.setValue(cameraPath)
        
        dollyTargetPath = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('targetPath.i0'))
        dollyTargetPath.setValue(assetPath)

        dollyTargetBounds = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('targetBounds'))
        dollyTargetBounds.setValue('box')

        dollyOffsetAngle = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('angleOffset'))
        dollyOffsetAngle.setValue(offsetAmount)

        dollyConstraintList = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('addToConstraintList'))
        dollyConstraintList.setValue(1.0)

        return dollyConstraint

    
    def generateTT(self):

        alembicCreate = NodegraphAPI.CreateNode('Alembic_In', self.root)
        assetSet = UI4.FormMaster.CreateParameterPolicy(None, alembicCreate.getParameter('abcAsset'))
        assetSet.setValue(str(self.assetPath.text()))

        assetLocation = alembicCreate.getParameterValue('name', NodegraphAPI.GetCurrentTime())

        camera = NodegraphAPI.CreateNode('CameraCreate', self.root)
        camTranslate = UI4.FormMaster.CreateParameterPolicy(None, camera.getParameter('transform.translate'))
        camTranslate.setValue([0,
                               1.5,
                               14])
        
        
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

        if self.lookDevSetup.enableBackdrop.isChecked() and self.lookDevSetup.enableAll.isChecked():
            createBackdrop = self.lookDevSetup.addBackdrop(self.root)
            createLookdevSetup = self.lookDevSetup.createLookdevScene(self.root)
            backdropGroupOut = createBackdrop.getOutputPort('groupOut')
            lookdevGroupOut = createLookdevSetup.getOutputPort('groupOut')
            groupsMerge = NodegraphAPI.CreateNode('Merge', self.root)
            mergeInOne = groupsMerge.addInputPort('i0')
            mergeInTwo = groupsMerge.addInputPort('i1')
            backdropGroupOut.connect(mergeInOne)             
            lookdevGroupOut.connect(mergeInTwo)
            
            groupsMergeOut = groupsMerge.getOutputPort('out')
            camAssetMerge = multiMerge([alembicCreate, camera, assetNMC], self.root)
            newPort = camAssetMerge.addInputPort('i3')
            groupsMergeOut.connect(newPort)
        
        elif self.lookDevSetup.enableAll.isChecked() and not self.lookDevSetup.enableBackdrop.isChecked():
            createLookdevSetup = self.lookDevSetup.createLookdevScene(self.root)
            lookdevGroupOut = createLookdevSetup.getOutputPort('groupOut')
            camAssetMerge = multiMerge([alembicCreate, camera, assetNMC], self.root)
            newPort = camAssetMerge.addInputPort('i3')
            lookdevGroupOut.connect(newPort)

        elif self.lookDevSetup.enableBackdrop.isChecked() and not self.lookDevSetup.enableAll.isChecked():
            createBackdrop = self.lookDevSetup.addBackdrop(self.root)
            backdropGroupOut = createBackdrop.getOutputPort('groupOut')
            camAssetMerge = multiMerge([alembicCreate, camera, assetNMC], self.root)
            newPort = camAssetMerge.addInputPort('i3')
            backdropGroupOut.connect(newPort)
        
        elif self.lookDevSetup.enableBackdrop.isChecked() != True and self.lookDevSetup.enableAll.isChecked() != True:
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

        skydome = self.skydomeSetup.createSkydome(self.root)
        
        lightMat = self.skydomeSetup.envLightMaterial(skydome)
                    
        if self.skydomeSetup.intensityValue.text() != 0.00:
            intensity = UI4.FormMaster.CreateParameterPolicy(None, lightMat.getParameter('shaders.dlEnvironmentParams.intensity'))
            intensity.setValue(self.skydomeSetup.intensityValue.text())
        if self.skydomeSetup.exposureValue.text() != 0.00:
            exposure = UI4.FormMaster.CreateParameterPolicy(None, lightMat.getParameter('shaders.dlEnvironmentParams.exposure'))
            exposure.setValue(self.skydomeSetup.exposureValue.text())

        # constraining the lookdev scene to the camera if it is created
        if self.lookDevSetup.enableAll.isChecked():
            parentChildConstraint = NodegraphAPI.CreateNode('ParentChildConstraint', self.root)
            parentChildConstraint.getParameter('basePath').setValue('/root/world/LookDevScene', 1)
            parentChildConstraint.getParameter('targetPath').setValue('/root/world/cam/camera', 1)
            parentChildConstraint.getParameter('addToConstraintList').setValue(1, 1)
            constraintResolve = NodegraphAPI.CreateNode('ConstraintResolve', self.root)

            dollyIntoParentConstraint = connectTwoNodes(dollyConstraint, parentChildConstraint, 'out', 'input')
            parentIntoResolver = connectTwoNodes(parentChildConstraint, constraintResolve, 'out', 'input')
            parentChildIntoGaffer = connectTwoNodes(constraintResolve, skydome, 'out', 'in')
        else:
            dollyToSkydome = connectTwoNodes(dollyConstraint, skydome, 'out', 'in')

        
        # if the use texture checkbox in the Skydome tab is checked:
        if self.skydomeSetup.useTexture.isChecked():
            texturePath = UI4.FormMaster.CreateParameterPolicy(None, lightMat.getParameter('shaders.dlEnvironmentParams.image'))
            texturePath.setValue(str(self.skydomeSetup.texturePath.text()))

            colorSpace = UI4.FormMaster.CreateParameterPolicy(None, lightMat.getParameter('shaders.dlEnvironmentParams.image_meta_colorspace'))
            colorSpace.setValue(str(self.skydomeSetup.selectColorspace.currentText()))

    
        skydomeToRenderSettings = connectTwoNodes(skydome, renderSettings, 'out', 'input')

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

        lightingLabel = QLabel("Skydome Setup")
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

        self.useTexture = QCheckBox("Assign texture to Skydome?")

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
        self.parentLayout.addWidget(lightingLabel, 0, 0)
        
        self.parentLayout.addWidget(texturePathLabel, 1, 0)
        self.parentLayout.addWidget(self.texturePath, 1, 1, 1, 6)
        self.parentLayout.addWidget(self.searchTexture, 1, 7, 1, 1, Qt.AlignLeft)
        
        # Set Light's colorspace
        self.parentLayout.addWidget(colorSpace, 4, 0)
        self.parentLayout.addWidget(self.selectColorspace, 4, 1, 1, 7)
        self.parentLayout.addWidget(mapping, 5, 0)
        
        # Set the texture image's mapping type
        self.parentLayout.addWidget(self.mappingDrowdown, 5, 1, 1, 7)
        self.parentLayout.addWidget(self.useTexture, 6, 7, 1, 1, Qt.AlignLeft)

        # Light intensity Settings
        self.parentLayout.addWidget(intensityLabel, 7, 0)
        self.parentLayout.addWidget(self.intensityValue, 7, 1, 1, 1, Qt.AlignLeft)
        self.parentLayout.addWidget(self.intensitySlider, 7, 2, 1, 6)
        

        # Light Exposure Settings
        self.parentLayout.addWidget(exposureLabel, 8, 0, 1, 1)
        self.parentLayout.addWidget(self.exposureValue, 8, 1, 1, 1, Qt.AlignLeft)
        self.parentLayout.addWidget(self.exposureSlider, 8, 2, 1, 6)

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

        self.enableAll = QCheckBox("Enable LookDev Setup")


        layout.addWidget(lookdevHeading, 0, 0)
        layout.addWidget(backgrounds, 1, 0)
        #layout.addWidget(self.enablePlatform, 2, 0)
        layout.addWidget(self.enableBackdrop, 2, 0)
        layout.addWidget(lookdevTools, 3, 0)
        layout.addWidget(self.enableAll, 4, 0)

        self.show()
        self.setLayout(layout)
    
    def createLookdevScene(self, parent):
        

        lookdevGroup = groupNodeSetup(parent)
        primGroup = groupNodeSetup(lookdevGroup)

        networkMaterialCreate = NodegraphAPI.CreateNode('NetworkMaterialCreate', primGroup)
        nmcLocation = getMaterialPath(networkMaterialCreate.getNetworkMaterials()[0])

        # Grey Spehere Create
        self.greySphere = geoCreate('poly sphere', primGroup)
        greyNameSet = self.greySphere.getParameter('name').setValue('/root/world/LookDevScene/greySphere', 0)
        greySphereLocation = self.greySphere.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        greySphereInteractive = UI4.FormMaster.CreateParameterPolicy(None, self.greySphere.getParameter('makeInteractive'))
        greySphereInteractive.setValue('No')

        # Grey Sphere Transform
        self.greySphereTransform = NodegraphAPI.CreateNode('Transform3D', primGroup)
        transformPath = UI4.FormMaster.CreateParameterPolicy(None, self.greySphereTransform.getParameter('path'))
        transformPath.setValue(greySphereLocation)
        transformTranslate = UI4.FormMaster.CreateParameterPolicy(None, self.greySphereTransform.getParameter('translate'))
        transformTranslate.setValue([-1.5,
                                     3.0,
                                     0])
        transformInteractive = UI4.FormMaster.CreateParameterPolicy(None, self.greySphereTransform.getParameter('makeInteractive'))
        transformInteractive.setValue('No')
        primitiveIntoTransform = connectTwoNodes(self.greySphere, self.greySphereTransform, 'out', 'in')

        # Grey Sphere subdivide
        self.greyAttributeSet = subDivideMesh(greySphereLocation, primGroup)
        greyAttributeConnect = connectTwoNodes(self.greySphereTransform, self.greyAttributeSet, 'out', 'A')
        
        # Grey Sphere material setup
        greyMat = shadingNodeCreate('dlPrincipled', networkMaterialCreate)
        greyBaseColor = UI4.FormMaster.CreateParameterPolicy(None, greyMat.getParameter('parameters.color'))
        greyBaseColor.setValue([0.18,
                                0.18,
                                0.18])
        greyRoughness = UI4.FormMaster.CreateParameterPolicy(None, greyMat.getParameter('parameters.roughness'))
        greyRoughness.setValue(1)
        greyConnectInsideNMC = nmcConnect(networkMaterialCreate, greyMat, 'dlSurface')

        
        # creating Chrome Sphere
        self.chromeSphere = geoCreate('poly sphere', primGroup)
        chromeNameSet = self.chromeSphere.getParameter('name').setValue('/root/world/LookDevScene/chromeSphere', 0)
        chromeSphereLocation = self.chromeSphere.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        chromeSphereInteractive = UI4.FormMaster.CreateParameterPolicy(None, self.chromeSphere.getParameter('makeInteractive'))
        chromeSphereInteractive.setValue('No')

        # Moving the Chrome Sphere
        self.chromeSphereTransform = NodegraphAPI.CreateNode('Transform3D', primGroup)
        transformPath = UI4.FormMaster.CreateParameterPolicy(None, self.chromeSphereTransform.getParameter('path'))
        transformPath.setValue(chromeSphereLocation)
        transformTranslate = UI4.FormMaster.CreateParameterPolicy(None, self.chromeSphereTransform.getParameter('translate'))
        transformTranslate.setValue([1.5,
                                     3.0,
                                     0])
        transformInteractive = UI4.FormMaster.CreateParameterPolicy(None, self.chromeSphereTransform.getParameter('makeInteractive'))
        transformInteractive.setValue('No')
        primitiveIntoTransform = connectTwoNodes(self.chromeSphere, self.chromeSphereTransform, 'out', 'in')
        
        # subdividing the sphere
        self.chromeAttributeSet = subDivideMesh(chromeSphereLocation, primGroup)
        chromeAttributeConnect = connectTwoNodes(self.chromeSphereTransform, self.chromeAttributeSet, 'out', 'A')

        # creating the Chrome material
        chromeNetworkMaterial = NodegraphAPI.CreateNode('NetworkMaterial', networkMaterialCreate)
        chromeMaterialLocation = getMaterialPath(chromeNetworkMaterial)

        chromeMaterial = shadingNodeCreate('dlPrincipled', networkMaterialCreate)
        chromeMaterialColor = UI4.FormMaster.CreateParameterPolicy(None, chromeMaterial.getParameter('parameters.color'))
        chromeMaterialColor.setValue([1,
                                      1,
                                      1])
        chromeMaterialRoughness = UI4.FormMaster.CreateParameterPolicy(None, chromeMaterial.getParameter('parameters.roughness'))
        chromeMaterialRoughness.setValue(0)
        chromeMaterialMetallic = UI4.FormMaster.CreateParameterPolicy(None, chromeMaterial.getParameter('parameters.metallic'))
        chromeMaterialMetallic.setValue(1)
        chromeConnectInsideNMC = nmcConnect(chromeNetworkMaterial, chromeMaterial, 'dlSurface')
    
        # creating the MacBeth chart
        self.chart = geoCreate('poly plane', primGroup)
        chartNameSet = self.chart.getParameter('name').setValue('/root/world/LookDevScene/colorChart', 0)
        chartLocation = self.chart.getParameterValue('name', NodegraphAPI.GetCurrentTime())
        chartInteractive = UI4.FormMaster.CreateParameterPolicy(None, self.chart.getParameter('makeInteractive'))
        chartInteractive.setValue('No')

        # transforming the chart
        self.chartTransform = NodegraphAPI.CreateNode('Transform3D', primGroup)
        transformPath = UI4.FormMaster.CreateParameterPolicy(None, self.chartTransform.getParameter('path'))
        transformPath.setValue(chartLocation)
        transformRotate = UI4.FormMaster.CreateParameterPolicy(None, self.chartTransform.getParameter('rotate'))
        transformRotate.setValue([90,
                                  0,
                                  0])
        transformScale = UI4.FormMaster.CreateParameterPolicy(None, self.chartTransform.getParameter('scale'))
        transformScale.setValue([5.0,
                                 3.0,
                                 3.0])
        transformInteractive = UI4.FormMaster.CreateParameterPolicy(None, self.chart.getParameter('makeInteractive'))
        transformInteractive.setValue('No')
        geoIntoTransform = connectTwoNodes(self.chart, self.chartTransform, 'out', 'in')

        # subdividing the chart
        self.chartAttributeSet = subDivideMesh(chartLocation, primGroup)
        transformIntoAttributeSet = connectTwoNodes(self.chartTransform, self.chartAttributeSet, 'out', 'A')

        # creating the chart material
        chartNetworkMaterial = NodegraphAPI.CreateNode('NetworkMaterial', networkMaterialCreate)
        chartMaterialLocation = getMaterialPath(chartNetworkMaterial)
        chartMaterial = shadingNodeCreate('dlPrincipled', networkMaterialCreate)
        chartTexture = shadingNodeCreate('file', networkMaterialCreate)
        texturePath = UI4.FormMaster.CreateParameterPolicy(None, chartTexture.getParameter('parameters.fileTextureName'))
        texturePath.setValue('C:/Users/AdelePeleschka/TurntableTools/FINAL/sRGB_ColorChecker.tdl')
        
        placeTexture = shadingNodeCreate('place2dTexture', networkMaterialCreate)
        uvCoordsIntoTexture = connectTwoNodes(placeTexture, chartTexture, 'outUV', 'uvCoord')
        textureIntoSurface = connectTwoNodes(chartTexture, chartMaterial, 'outColor', 'color')
        connectChartInsideNMC = nmcConnect(chartNetworkMaterial, chartMaterial, 'dlSurface')

        # merging all the primitves together
        primsMerge = multiMerge([self.greyAttributeSet, self.chromeAttributeSet, self.chartAttributeSet], primGroup)
        primsNMCMerge = multiMerge([primsMerge, networkMaterialCreate], primGroup)

        # connecting the final merge to the prim group out port
        primsNMCMergeOut = primsNMCMerge.getOutputPort('out')
        primGroupReturnPort = primGroup.getReturnPort('groupOut')
        primsNMCMergeOut.connect(primGroupReturnPort)

        
        # creating object settings

        removeShadows = NodegraphAPI.CreateNode('DlObjectSettings', lookdevGroup)
        shadowsGeoLocation = UI4.FormMaster.CreateParameterPolicy(None, removeShadows.getParameter('CEL'))
        shadowsGeoLocation.setValue('/root/world/LookDevScene/')
        castShadows = UI4.FormMaster.CreateParameterPolicy(None, removeShadows.getParameter('args.dlObjectSettings.visibility.shadow'))
        castShadows.setValue(0)

        primGroupToRemoveShadows = connectTwoNodes(primGroup, removeShadows, 'groupOut', 'input')
        
        lookdevTransform = NodegraphAPI.CreateNode('Transform3D', lookdevGroup)
        setTransformPath = UI4.FormMaster.CreateParameterPolicy(None, lookdevTransform.getParameter('path'))
        setTransformPath.setValue('/root/world/LookDevScene')
        scaleLookdev = UI4.FormMaster.CreateParameterPolicy(None, lookdevTransform.getParameter('scale'))
        scaleLookdev.setValue([0.1,
                               0.1,
                               0.1])

        transformLookdev = UI4.FormMaster.CreateParameterPolicy(None, lookdevTransform.getParameter('translate'))
        transformLookdev.setValue([-1.2,
                                   -0.6,
                                   -2.0])

        shadowsToTransform = connectTwoNodes(removeShadows, lookdevTransform, 'out', 'in')

        # creating the Material Assign Stack
        self.materialAssignStack = NodegraphAPI.CreateNode('GroupStack', lookdevGroup)
        self.materialAssignStack.setChildNodeType('MaterialAssign')

        # setting up the Material Assigns
        greyMaterialAssign = materialAssignSetup(greySphereLocation, nmcLocation, self.materialAssignStack)
        chromeMaterialAssign = materialAssignSetup(chromeSphereLocation, chromeMaterialLocation, self.materialAssignStack)
        chartMaterialAssign = materialAssignSetup(chartLocation, chartMaterialLocation, self.materialAssignStack)


        transformToAssignStack = connectTwoNodes(lookdevTransform, self.materialAssignStack, 'out', 'in')
        
        materialAssignStackOut = self.materialAssignStack.getOutputPort('out')
        lookdevGroupReturnPort = lookdevGroup.getReturnPort('groupOut')
        materialAssignStackOut.connect(lookdevGroupReturnPort)

        materialAssignStackSendPort = self.materialAssignStack.getSendPort('in')
        materialAssignStackReturnPort = self.materialAssignStack.getReturnPort('out')

        greyMaterialAssignIn = greyMaterialAssign.getInputPort('input')
        greyMaterialAssignIn.connect(materialAssignStackSendPort)

        greyToChrome = connectTwoNodes(greyMaterialAssign, chromeMaterialAssign, 'out', 'input')
        chromeToChart = connectTwoNodes(chromeMaterialAssign, chartMaterialAssign, 'out', 'input')

        chartMaterialAssignOut = chartMaterialAssign.getOutputPort('out')
        chartMaterialAssignOut.connect(materialAssignStackReturnPort)

        return lookdevGroup
    
    def addBackdrop(self, parent):

        backdropGroup = groupNodeSetup(parent)

        backdropCreate = NodegraphAPI.CreateNode('Alembic_In', backdropGroup)
        backdropSetName = backdropCreate.getParameter('name').setValue('/root/world/backdrop', 0)
        backdropLocation = backdropCreate.getParameterValue('name', NodegraphAPI.GetCurrentTime())

        backdropGeoIn = UI4.FormMaster.CreateParameterPolicy(None, backdropCreate.getParameter('abcAsset'))
        backdropGeoIn.setValue('C:/Users/AdelePeleschka/TurntableTools/FINAL/ground.abc')

        backdropAttributeSet = subDivideMesh(backdropLocation + '/groundPlane/groundPlaneShape', backdropGroup)

        backdropIntoAttributeSet = connectTwoNodes(backdropCreate, backdropAttributeSet, 'out', 'A')

        removeShadows = NodegraphAPI.CreateNode('DlObjectSettings', backdropGroup)
        shadowsGeoLocation = UI4.FormMaster.CreateParameterPolicy(None, removeShadows.getParameter('CEL'))
        shadowsGeoLocation.setValue(backdropLocation + '/groundPlane/groundPlaneShape')
        castShadows = UI4.FormMaster.CreateParameterPolicy(None, removeShadows.getParameter('args.dlObjectSettings.visibility.shadow'))
        castShadows.setValue(0)

        attributeSetIntoShadows = connectTwoNodes(backdropAttributeSet, removeShadows, 'out', 'input')

        backdropNMC = NodegraphAPI.CreateNode('NetworkMaterialCreate', backdropGroup)
        backdropMaterial = getMaterialPath(backdropNMC.getNetworkMaterials()[0])

        dlPrincipled = shadingNodeCreate('dlPrincipled', backdropNMC)
        dlRoughness = UI4.FormMaster.CreateParameterPolicy(None, dlPrincipled.getParameter('parameters.roughness'))
        dlRoughness.setValue(1)
        dlSpec = UI4.FormMaster.CreateParameterPolicy(None, dlPrincipled.getParameter('parameters.specular_level'))
        dlSpec.setValue(0)
        
        dlTexture = shadingNodeCreate('file', backdropNMC)
        texturePath = UI4.FormMaster.CreateParameterPolicy(None, dlTexture.getParameter('parameters.fileTextureName'))
        texturePath.setValue('C:/Users/AdelePeleschka/TurntableTools/FINAL/Floor_Color_50percent.tdl')
        placeTexture = shadingNodeCreate('place2dTexture', backdropNMC)

        uvCoordsIntoTexture = connectTwoNodes(placeTexture, dlTexture, 'outUV', 'uvCoord')
        textureIntoSurface = connectTwoNodes(dlTexture, dlPrincipled, 'outColor', 'color')
        connectChartInsideNMC = nmcConnect(backdropNMC, dlPrincipled, 'dlSurface')

        attributeSetNMCMerge = multiMerge([removeShadows, backdropNMC], backdropGroup)

        backdropMatAssign = materialAssignSetup(backdropLocation, backdropMaterial, backdropGroup)
        mergeIntoMatAssign = connectTwoNodes(attributeSetNMCMerge, backdropMatAssign, 'out', 'input')

        matAssignOutput = backdropMatAssign.getOutputPort('out')
        backdropGroupReturnPort = backdropGroup.getReturnPort('groupOut')

        matAssignOutput.connect(backdropGroupReturnPort)

        return backdropGroup

        


open = TurntableWindow()