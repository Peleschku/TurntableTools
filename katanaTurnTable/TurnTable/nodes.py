from . import utilites as Utils
from Katana import (NodegraphAPI,
                    UI4)

def _assetNMC(root):
    nmc = NodegraphAPI.CreateNode("NetworkMaterialCreate", root)
    materialLoc = Utils.getMaterialPath(nmc.getNetworkMaterials()[0])

    dlPrincipled = Utils.shadingNodeCreate("dlPrincipled", nmc)
    base = UI4.FormMaster.CreateParameterPolicy(None, dlPrincipled.getParameter(
        "parameters.color"
    )).setValue([0.18,
                 0.18,
                 0.18])
    
    internalConnection = Utils.nmcConnect(nmc, dlPrincipled, "dlSurface")

    return nmc

# DlObjectSettings node used to remove shadows in render
def _objectSettings(root, object, objectPath):
    objectSettings = NodegraphAPI.CreateNode("DlObjectSettings", root)
    objectLocation = object.getParameterValue("name", NodegraphAPI.GetCurrentTime())
    cel = UI4.FormMaster.CreateParameterPolicy(None, objectSettings.getParameter(
        'CEL'
    )).setValue(objectLocation + str(objectPath))
    removeShadows = UI4.FormMaster.CreateParameterPolicy(None, objectSettings.getParameter(
        'args.dlObjectSettings.visibility.shadow'
    )).setValue(0)

    return objectSettings
    