import bpy

from dataset_generation.model.parameters import LabelParameters

IMAGE_OUTPUT_NAME = 'image-#'
LABEL_OUTPUT_NAME = 'label-#'


def clear_nodes(tree: bpy.types.NodeTree) -> None:
    """Clear the current compositor tree."""
    for node in tree.nodes:
        tree.nodes.remove(node)


def create_closing_nodes(
    tree: bpy.types.NodeTree,
    input: bpy.types.NodeSocket,
    closing_steps: int
) -> bpy.types.NodeSocket:
    """Create and connect a closing node. Returns the output socket of the last node."""
    dilate_node = tree.nodes.new('CompositorNodeDilateErode')
    dilate_node.distance = closing_steps
    tree.links.new(input, dilate_node.inputs['Mask'])

    erode_node = tree.nodes.new('CompositorNodeDilateErode')
    erode_node.distance = -closing_steps
    tree.links.new(dilate_node.outputs['Mask'], erode_node.inputs['Mask'])

    return erode_node.outputs['Mask']


def create_normalize_and_mask_input_nodes(
    tree: bpy.types.NodeTree,
    input_node: bpy.types.Node
) -> tuple[bpy.types.NodeSocket, bpy.types.NodeSocket]:
    """Normalize the crack and image and then mask them. Returns the output socket of the mask and the normalized image."""
    normalize_crack_node = tree.nodes.new('CompositorNodeNormalize')
    tree.links.new(input_node.outputs['Crack'], normalize_crack_node.inputs['Value'])
    closing_output_socket = create_closing_nodes(tree, normalize_crack_node.outputs['Value'], 2)

    normalize_image_node = tree.nodes.new('CompositorNodeNormalize')
    tree.links.new(input_node.outputs['Image'], normalize_image_node.inputs['Value'])
    invert_color_node = tree.nodes.new('CompositorNodeInvert')
    tree.links.new(normalize_image_node.outputs['Value'], invert_color_node.inputs['Color'])

    masking_node = tree.nodes.new('CompositorNodeAlphaOver')
    tree.links.new(closing_output_socket, masking_node.inputs[0])
    masking_node.inputs[1].default_value = (0, 0, 0, 1)
    tree.links.new(invert_color_node.outputs['Color'], masking_node.inputs[2])

    return masking_node.outputs['Image'], normalize_image_node.outputs['Value']


def create_shape_preservation_nodes(
    tree: bpy.types.NodeTree,
    mask_output_socket: bpy.types.NodeSocket,
    normalized_image_socket: bpy.types.NodeSocket
) -> bpy.types.NodeSocket:
    """Creates the nodes for preserving the crack shape. This is handled by subtracting the base image."""
    multiply_node = tree.nodes.new('CompositorNodeMath')
    multiply_node.operation = 'MULTIPLY'
    multiply_node.inputs[1].default_value = 3
    tree.links.new(normalized_image_socket, multiply_node.inputs[0])

    subtract_node = tree.nodes.new('CompositorNodeMath')
    subtract_node.operation = 'SUBTRACT'
    subtract_node.use_clamp = True
    tree.links.new(mask_output_socket, subtract_node.inputs[0])
    tree.links.new(multiply_node.outputs['Value'], subtract_node.inputs[1])

    return create_closing_nodes(tree, subtract_node.outputs['Value'], 1)


def create_save_nodes(
    tree: bpy.types.NodeTree,
    output_dir: str,
    image_input_socket: bpy.types.NodeSocket,
    label_input_socket: bpy.types.NodeSocket
) -> None:
    """Create the nodes saving the results. Saves to a separate label and image file."""
    output_node = tree.nodes.new('CompositorNodeOutputFile')
    output_node.base_path = output_dir
    output_node.format.file_format = 'PNG'
    output_node.file_slots.new(LABEL_OUTPUT_NAME)

    output_node.file_slots[0].path = IMAGE_OUTPUT_NAME
    output_node.file_slots[1].path = LABEL_OUTPUT_NAME

    tree.links.new(image_input_socket, output_node.inputs[0])
    tree.links.new(label_input_socket, output_node.inputs[1])

    composite_node = tree.nodes.new('CompositorNodeComposite')
    tree.links.new(image_input_socket, composite_node.inputs['Image'])


def create_compositor_flow(parameters: LabelParameters):
    """
    Create the compositor flow. This applies the following steps:
    1. Set all compositor options.
    2. Clear the current compositor tree.
    3. Create the required compositor flow.
    """
    scene = bpy.context.scene
    tree = scene.node_tree
    clear_nodes(tree)

    scene.render.use_compositing = True
    scene.use_nodes = True
    if not scene.view_layers['ViewLayer'].aovs.get('Crack'):
        aov = scene.view_layers['ViewLayer'].aovs.add()
        aov.name = 'Crack'
        aov.type = 'COLOR'

    # Node flow
    input_node = tree.nodes.new('CompositorNodeRLayers')
    mask_output_socket, normalized_image_output_socket = create_normalize_and_mask_input_nodes(tree, input_node)
    shape_preservation_output_socket = create_shape_preservation_nodes(
        tree,
        mask_output_socket,
        normalized_image_output_socket
    )
    create_save_nodes(
        tree,
        parameters.base_output_directory,
        input_node.outputs['Image'],
        shape_preservation_output_socket
    )
