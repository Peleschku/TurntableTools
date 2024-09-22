from PyQt5.QtWidgets import (QWidget,
                            QGridLayout,
                            QLabel,
                            QFileDialog,
                            QLineEdit,
                            QPushButton)



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

class SearchBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self._parentLayout = QGridLayout()
        self._parentLayout.setVerticalSpacing(15)

        self._createModule()
    
    def _createModule(self):
        path = QLabel("Path")
        self._assetPath = QLineEdit()

        self._search = QPushButton("Search")
        self._search.clicked.connect(self._browser)

        self._parentLayout.addWidget(path, 0, 0, 1, 1)
        self._parentLayout.addWidget(self._assetPath, 0, 1, 1, 6)
        self._parentLayout.addWidget(self._search, 0, 7, 1, 1)

        self.show()
        self.setLayout(self._parentLayout)
    
    def _browser(self):
        filter = ["alembic (*.abc)",
                  "usda (*usda)",
                  "usd (*.usd)"]
        
        file = QFileDialog.getOpenFileName(self, "Open", "", filter)

        if file:
            self._assetPath.insert(file[0])