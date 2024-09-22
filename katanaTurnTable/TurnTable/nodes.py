from . import utilites as Utils


def _assetNMC(self, root):
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

