import bpy

from dataset_generation.model.parameters import LabelParameters

IMAGE_OUTPUT_NAME = 'image-#'
LABEL_OUTPUT_NAME = 'label-#'


def clear_nodes(tree: bpy.types.NodeTree) -> None:
    """Clear the current compositor tree."""
    for node in tree.nodes:
        tree.nodes.remove(node)


def create_threshold_node(
    tree: bpy.types.NodeTree,
    threshold: float,
    input: bpy.types.NodeSocket
) -> bpy.types.NodeSocket:
    """
    Create the standard binary threshold node with a certain threshold and return its output.
    """
    threshold_node = tree.nodes.new('CompositorNodeValToRGB')
    threshold_node.color_ramp.interpolation = 'CONSTANT'
    threshold_node.color_ramp.elements[0].color = (1, 1, 1, 1)
    threshold_node.color_ramp.elements[1].position = threshold
    threshold_node.color_ramp.elements[1].color = (0, 0, 0, 0)

    tree.links.new(input, threshold_node.inputs[0])
    return threshold_node.outputs[0]


def create_ao_threshold_path(
    tree: bpy.types.NodeTree,
    input_socket: bpy.types.NodeSocket,
    ao_threshold: float
) -> bpy.types.NodeSocket:
    """
    Create and link the compositing node path that threshold the ambient occlusion layer.
    Return the output socket of the last operation.
    """
    # Step 1: normalize the AO layer
    normalize_node = tree.nodes.new('CompositorNodeNormalize')
    tree.links.new(input_socket, normalize_node.inputs['Value'])

    # Step 2: threshold the normalized map
    threshold_node = tree.nodes.new('CompositorNodeValToRGB')
    threshold_node.color_ramp.interpolation = 'CONSTANT'
    threshold_node.color_ramp.elements[0].color = (1, 1, 1, 1)
    threshold_node.color_ramp.elements[1].position = ao_threshold
    threshold_node.color_ramp.elements[1].color = (0, 0, 0, 0)
    tree.links.new(normalize_node.outputs['Value'], threshold_node.inputs['Fac'])

    # Step 3: Perform a closing to smooth out the label
    dilate_node = tree.nodes.new('CompositorNodeDilateErode')
    dilate_node.distance = 4
    tree.links.new(threshold_node.outputs['Image'], dilate_node.inputs['Mask'])

    erode_node = tree.nodes.new('CompositorNodeDilateErode')
    erode_node.distance = -4
    tree.links.new(dilate_node.outputs['Mask'], erode_node.inputs['Mask'])

    return erode_node.outputs['Mask']


def create_crack_threshold_path(
    tree: bpy.types.NodeTree,
    input_socket: bpy.types.NodeSocket,
    crack_threshold: float
) -> bpy.types.NodeSocket:
    """
    Create and link the compositing node path that threshold the crack pixel output.
    Return the output socket of the last operation.
    """
    # Step 1: normalize the layer
    normalize_node = tree.nodes.new('CompositorNodeNormalize')
    tree.links.new(input_socket, normalize_node.inputs['Value'])

    # Step 2: threshold the normalized map
    threshold_node = tree.nodes.new('CompositorNodeValToRGB')
    threshold_node.color_ramp.interpolation = 'CONSTANT'
    threshold_node.color_ramp.elements[0].color = (0, 0, 0, 0)
    threshold_node.color_ramp.elements[1].position = crack_threshold
    threshold_node.color_ramp.elements[1].color = (1, 1, 1, 1)
    tree.links.new(normalize_node.outputs['Value'], threshold_node.inputs['Fac'])

    return threshold_node.outputs['Image']


def create_compositor_flow(parameters: LabelParameters):
    """
    Create the compositor flow. This applies the following steps:
    1. Set all compositor options.
    2. Clear the current compositor tree.
    3. Create the required compositor flow, consisting of a crack extraction and shadow extraction step.
    """
    scene = bpy.context.scene
    tree = scene.node_tree
    clear_nodes(tree)

    scene.render.use_compositing = True
    scene.use_nodes = True
    scene.view_layers['ViewLayer'].use_pass_ambient_occlusion = True
    scene.view_layers['ViewLayer'].use_pass_uv = True
    if not scene.view_layers['ViewLayer'].aovs.get('Crack'):
        aov = scene.view_layers['ViewLayer'].aovs.add()
        aov.name = 'Crack'
        aov.type = 'COLOR'

    # Create input
    input_node = tree.nodes.new('CompositorNodeRLayers')

    # Create threshold paths
    crack_threshold_output = create_crack_threshold_path(tree, input_node.outputs['Crack'], parameters.crack_threshold)
    ao_threshold_output = create_ao_threshold_path(tree, input_node.outputs['AO'], parameters.ao_threshold)

    # Intersect output
    intersect_node = tree.nodes.new('CompositorNodeMath')
    intersect_node.operation = 'MULTIPLY'
    intersect_node.use_clamp = True
    tree.links.new(ao_threshold_output, intersect_node.inputs[0])
    tree.links.new(crack_threshold_output, intersect_node.inputs[1])

    # Save output
    output_node = tree.nodes.new('CompositorNodeOutputFile')
    output_node.base_path = parameters.base_output_directory
    output_node.format.file_format = 'PNG'
    output_node.file_slots.new(LABEL_OUTPUT_NAME)

    output_node.file_slots[0].path = IMAGE_OUTPUT_NAME
    output_node.file_slots[1].path = LABEL_OUTPUT_NAME

    tree.links.new(input_node.outputs['Image'], output_node.inputs[0])
    tree.links.new(intersect_node.outputs['Value'], output_node.inputs[1])

    composite_node = tree.nodes.new('CompositorNodeComposite')
    tree.links.new(input_node.outputs['Image'], composite_node.inputs['Image'])
