from Katana import (
    NodegraphAPI,
    UI4
)

# ---------------------------------------------------------------------------------------------------
# ------------------------------------ Node Creation Functions --------------------------------------
# ---------------------------------------------------------------------------------------------------

def primitive_create(primitive_type:(str), parent_node:(str)):
    """
    Creates a PrimitiveCreate node, then sets the type based on the primitive_type name passed in
    the functions arguments when it is called.

    Parameters:
    primitive_type (str): Name of the primitive to be created
    parent (str): name of the parent/root node
    """
    primitive_create = NodegraphAPI.CreateNode('PrimitiveCreate', parent_node)
    policy = UI4.FormMaster.CreateParameterPolicy(None, primitive_create.getParameter('type'))
    policy.setValue(primitive_type, 0)

    return primitive_create

def shading_node_create(node_type:(str), parent:(str), shading_node_type = 'DlShadingNode'):
    """
    Creates a DlShadingNode, then sets the node type based on the node type that is passed as an
    argument when the function is called.

    Parameters:
    node_type (str): Name of the node type
    parent (str): Name of the parent node (Normally a NetworkMaterialCreate node)
    """
    
    shading_node = NodegraphAPI.CreateNode(shading_node_type, parent)
    shading_node.getParameter('nodeType').setValue(node_type, 0)
    shading_node.getParameter('name').setValue(node_type, 0)
    shading_node.checkDynamicParameters()

    return shading_node

def material_assign_create(asset_location:(str), material_name:(str), parent:(str)):
    """
    Creates a MaterialAssign node, then assigns the specified material to the specified asset
    location.

    Parameters:
    asset_location (str): The location of the asset in the scene graph. For example,
    '/root/world/geo/cube'
    material_name (str): The name of the material to be assigned.
    parent (str): The name of the parent/root node.
    """
    
    material_assign_node = NodegraphAPI.CreateNode('MaterialAssign', parent)
    material_assign_node.getParameter('CEL').setValue(
        asset_location,
        )
    material_assign_node.getParameter('args.materialAssign.enable').setValue(
        1, 0,
    )
    material_assign_node.getParameter('args.materialAssign.value').setValue(
        material_name, 0,
    )

    return material_assign_node

def group_node_create(parent:(str)):
    """
    Does all the internal setup for a group node. Nodes are not created within the resulting group,
    but the appropriate internal ports are creates and the Group node can be used as a parent node
    for other nodes as they are created.

    Parameters:
    parent (str): Name of the parent/root node.
    """
    group_node = NodegraphAPI.CreateNode('Group', parent)
    group_node.addOutputPort('groupOut')
    #The return port is a port that is internal to group nodes. This is the port that is visable
    #inside the Group node, and allows internal nodes to connect to a higher level Node Graph.
    group_node.getReturnPort('out')

    return group_node

def dolly_constraint_create(camera_path:(str), asset_path:(str), offset_amount:(float), parent:(str)):
    """
    Creates a DollyConstraint node, and then constrains a specified camera to a specified mesh/asset.

    Parameters:
    camera_path (str): The location of the camera to be constrained to a mesh. Will normally be
    the location of the Camera in the Scene Graph; for example '/root/world/cameras/camera'
    asset_path (str): The location of the asset/mesh to be constrained to a mesh. Will normally be
    the location of the Camera in the Scene Graph; for example '/root/world/geo/asset'
    offset_amount (float): The distance the camera should be from the asset it is constrained to.
    parent (str): The root/parent node.
    """
    dolly_constraint_node = NodegraphAPI.CreateNode('DollyConstraint', parent)
    
    UI4.FormMaster.CreateParameterPolicy(None, dolly_constraint_node.getParameter(
        'basePath')).setValue(camera_path)
    UI4.FormMaster.CreateParameterPolicy(None, dolly_constraint_node.getParameter(
        'targetPath.i0')).setValue(asset_path)
    UI4.FormMaster.CreateParameterPolicy(None, dolly_constraint_node.getParameter(
        'targetBounds')).setValue('box')
    UI4.FormMaster.CreateParameterPolicy(None, dolly_constraint_node.getParameter(
        'angleOffset')).setValue(offset_amount)
    UI4.FormMaster.CreateParameterPolicy(None, dolly_constraint_node.getParameter(
        'addToConstraintList')).setValue(1.0)
    
    return dolly_constraint_node


# ---------------------------------------------------------------------------------------------------
# -------------------------------- Functions for connecting nodes together --------------------------
# ---------------------------------------------------------------------------------------------------

def connect_two_nodes(out_node:(str), out_port:(str), in_node:(str), in_port:(str)):
    """
    Connects two nodes based on their input and output port names.
    
    Parameters:
    out_node (str): Takes the name of the node the output port belongs to
    out_port (str): Takes the name of the output port on the out node
    in_node (str): Takes the name of the node the input port belongs to
    in_port (str) Takes the name of the input port.
    """
    node_out_port = out_node.getOutputPort(out_port)
    node_in_port = in_node.getInputPort(in_port)

    node_out_port.connect(node_in_port)

def merge_multiple_nodes(nodes_to_merge:(list), parent_node:(str)):
    """
    Merges mutliple specified nodes in to a single merge node.

    Parameters:
    nodes_to_merge (list): Names of the nodes to be merged.
    parent_node (str): Takes the name of the root node.
    """

    merge_node = NodegraphAPI.CreateNode('Merge', parent_node)

    for node in nodes_to_merge:
        output_port = node.getOutputPort('out')
        merge_input_ports = merge_node.addInputPort('i')
        output_port.connect(merge_input_ports)
    
    return merge_node

def nmc_internal_connections(network_material:(str), shading_node:(str), terminal_input:(str)):
    """
    Connects a shading node to the terminal sidebar within a NetworkMaterialCreate or NetworkMaterial
    node.

    Parameters:
    network_material (str): Takes the name of your NetworkMaterial/NetworkMaterialCreate node
    shaidng_node (str): Takes the name of the shading node to be connected to the terminal
    terminal_input (str): Takes the name of the input port on the terminal to be connected to
    """
    
    if network_material.getType == 'NetworkMaterialCreate':
        terminal = network_material.getNetworkMaterials()[0]
        terminal_connect_in = terminal.getInputPort(terminal_input)
    elif network_material.getType() == 'NetworkMaterial':
        terminal_connect_in = network_material.addInputPort(terminal_input)

    shading_node_output = shading_node.getOutputPort('outColor')
    terminal_connect_in.connect(shading_node_output)

# ---------------------------------------------------------------------------------------------------
# --------------------------------- Additional helpful functions ------------------------------------
# ---------------------------------------------------------------------------------------------------

def get_material_path(network_material_create:(str)):
    """
    Function for getting the full path of a NetworkMaterialCreate node. Returns a string value.

    Parameters:
    network_material_create (str): Name of the NetworkMaterialCreate whose path you want to get.
    """
    material_name = network_material_create.getParameterValue('name', 
                                                                   NodegraphAPI.GetCurrentTime(),
                                                                   )
    nmc_parent = network_material_create.getParent()
    root_location = nmc_parent.getParameterValue('rootLocation',
                                                              NodegraphAPI.GetCurrentTime(),
                                                              )
    full_material_path = f"{root_location}/{material_name}"

    return full_material_path

def mesh_subDivide(mesh_location:(str), parent:(str)):
   """
   Creates an AttributeSet node that subdivides the mesh at a location that is passed as an
   argument when the function is run.

   Parameters:
   mesh_location (str): Location of the asset to be subdivided. Normally, this will be a path to
   it's location in the Scene Graph; for example '/root/world/geo/cube'
   parent (str): The parent/root node.
   """
    attribute_set_node = NodegraphAPI.CreateNode('AttributeSet', parent)
    path_parameter = UI4.FormMaster.CreateParameterPolicy(None, attribute_set_node.getParameter('paths'))
    path_parameter.getChild('i0').setValue(mesh_location)

    UI4.FormMaster.CreateParameterPolicy(None, attribute_set_node.getParameter('attributeName')).setValue(
        'type'
    )
    UI4.FormMaster.CreateParameterPolicy(None, attribute_set_node.getParameter('attributeType')).setValue(
        'string'
    )

    string_value = UI4.FormMaster.CreateParameterPolicy(None, attribute_set_node.getParameter(
        'stringValue'
        )
    )
    string_value.getChild('i0').setValue(
        'subdmesh',
    )

    return attribute_set_node