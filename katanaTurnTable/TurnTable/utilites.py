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