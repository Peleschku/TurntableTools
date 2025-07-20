def assetCreate(parent, assetPath):
    alembicIn = NodegraphAPI.CreateNode('AlembicIn', parent)
    setAssetPath = UI4.FormMaster.CreateParameterPolicy(None, alembicIn.getParameter('abcAsset'))
    setAssetPath.setValue(str(assetPath))

    return alembicIn

def createCamera(parent, ):
    