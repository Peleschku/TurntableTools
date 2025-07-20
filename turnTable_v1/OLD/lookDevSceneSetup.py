# ---------------------------------------------------------------------------------------------------
# ------------------------- Functions for creating geo, shading and group nodes ---------------------
# ---------------------------------------------------------------------------------------------------

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
    terminal = networkMaterial.getNetworkMaterials()[0]

    terminalOut = terminal.getInputPort(terminalInput)
    shadingNodeOut = shadingNode.getOutputPort('outColor')

    terminalOut.connect(shadingNodeOut)


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

def getMaterialPath(nmc):

    nmcRootLocation = nmc.getParameterValue('rootLocation', NodegraphAPI.GetCurrentTime())
    
    material = nmc.getNetworkMaterials()[-1]
    materialName = material.getParameterValue('name', NodegraphAPI.GetCurrentTime())

    materialPath = nmcRootLocation + "/" + materialName

    return materialPath


root = NodegraphAPI.GetRootNode()

group = groupNodeSetup(root)

primitiveTest = geoCreate('gnome', group)
primName = primitiveTest.getParameterValue('name', NodegraphAPI.GetCurrentTime())

nmc = NodegraphAPI.CreateNode('NetworkMaterialCreate', group)


dlSurface = shadingNodeCreate('dlPrincipled', nmc)

dlToNMC = nmcConnect(nmc, dlSurface, 'dlSurface')
nmcTerminal = getMaterialPath(nmc)

assetNMCMerge = multiMerge([primitiveTest, nmc], group)

gnomeAssign = materialAssignSetup(primName, nmcTerminal, group)

mergeIntoAssign = connectTwoNodes(assetNMCMerge, gnomeAssign, 'out', 'input')