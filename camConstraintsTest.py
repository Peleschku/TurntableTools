def multiMerge (nodesToMerge, parent):
    mergeNode = NodegraphAPI.CreateNode('Merge', parent)

    for node in nodesToMerge:

        # grabbing the output ports of the nodes made outside of the function
        outputPort = node.getOutputPort('out')

        #adding input ports to the merge node  based on how many nodes were created
        mergeInput = mergeNode.addInputPort('i')

        #connecting the nodes
        outputPort.connect(mergeInput)

    return mergeNode



root = NodegraphAPI.GetRootNode()

pony = NodegraphAPI.CreateNode('PonyCreate', root)

camera = NodegraphAPI.CreateNode('CameraCreate', root)

ponyCamMerge = multiMerge([pony, camera], root)

ponyCamMergeOut = ponyCamMerge.getOutputPort('out')

dollyConstraint = NodegraphAPI.CreateNode('DollyConstraint', root)

dollyBasePath = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('basePath'))
dollyBasePath.setValue('/root/world/cam/camera')

dollyTargetPath = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('targetPath.i0'))
dollyTargetPath.setValue('/root/world/geo/asset')

dollyTargetBounds = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('targetBounds'))
dollyTargetBounds.setValue('sphere')

dollyOffsetAngle = UI4.FormMaster.CreateParameterPolicy(None, dollyConstraint.getParameter('angleOffset')).setValue(-30)

dollyInputPort = dollyConstraint.getInputPort('input')
dollyOutputPort = dollyConstraint.getOutputPort('out')

ponyCamMergeOut.connect(dollyInputPort)


allNodes = NodegraphAPI.GetAllNodes()
NodegraphAPI.ArrangeNodes(allNodes, nodeGraphLengthSpacing = 250, nodeGraphWidthSpacing = 100)