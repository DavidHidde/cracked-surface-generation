import bpy

from dataset_generation.models.parameters import LabelGenerationParameters


def clear_nodes(tree: bpy.types.NodeTree) -> None:
    """
    Clear the current compositor tree.
    """
    for node in tree.nodes:
        tree.nodes.remove(node)


def create_intersect_node(
        tree: bpy.types.NodeTree,
        input_a: bpy.types.NodeSocket,
        input_b: bpy.types.NodeSocket
) -> bpy.types.NodeSocket:
    """
    Create a mask intersection (multiply) node and return its output.
    """
    multiply_node = tree.nodes.new('CompositorNodeMath')
    multiply_node.operation = 'MULTIPLY'
    multiply_node.use_clamp = True
    tree.links.new(input_a, multiply_node.inputs[0])
    tree.links.new(input_b, multiply_node.inputs[1])

    return multiply_node.outputs[0]


def create_threshold_node(
        tree: bpy.types.NodeTree,
        threshold: float,
        input: bpy.types.NodeSocket
) -> bpy.types.NodeSocket:
    """
    Create the standard binary threshold node with a certain threshold and return its output.
    """
    threshold_node = tree.nodes.new('CompositorNodeValToRGB')
    threshold_node.color_ramp.color_mode = 'RGB'
    threshold_node.color_ramp.interpolation = 'CONSTANT'
    threshold_node.color_ramp.elements[0].color = (1, 1, 1, 1)
    threshold_node.color_ramp.elements[1].position = threshold
    threshold_node.color_ramp.elements[1].color = (0, 0, 0, 0)

    tree.links.new(input, threshold_node.inputs[0])
    return threshold_node.outputs[0]


def create_image_threshold_path(
        tree: bpy.types.NodeTree,
        input_socket: bpy.types.NodeSocket,
        image_threshold: float
) -> bpy.types.NodeSocket:
    """
    Create and link the compositing node path that threshold the RGB image.
    Return the output socket of the last operation.
    """
    return create_threshold_node(tree, image_threshold, input_socket)


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
    tree.links.new(input_socket, normalize_node.inputs[0])  # Value, Value

    # Step 2: threshold the normalized map
    threshold_node_output = create_threshold_node(tree, ao_threshold, normalize_node.outputs[0])

    # Step 3: Perform a closing to smooth out the label
    dilate_node = tree.nodes.new('CompositorNodeDilateErode')
    dilate_node.mode = 'STEP'
    dilate_node.distance = 2
    tree.links.new(threshold_node_output, dilate_node.inputs[0])  # Image, Mask

    erode_node = tree.nodes.new('CompositorNodeDilateErode')
    erode_node.mode = 'STEP'
    erode_node.distance = -2
    tree.links.new(dilate_node.outputs[0], erode_node.inputs[0])  # Mask, Mask

    return erode_node.outputs[0]


def create_uv_threshold_path(
        tree: bpy.types.NodeTree,
        input_socket: bpy.types.NodeSocket,
        uv_threshold: float
) -> bpy.types.NodeSocket:
    ## Step 1: separate colors
    separate_node = tree.nodes.new('CompositorNodeSeparateColor')
    separate_node.mode = 'RGB'
    tree.links.new(input_socket, separate_node.inputs[0])  # UV, Image

    ## Step 2: normalize and threshold red and green channels and intersect.
    sockets = [separate_node.outputs[0], separate_node.outputs[1]]  # Red, Green
    for idx in range(len(sockets)):
        normalize_node = tree.nodes.new('CompositorNodeNormalize')
        tree.links.new(sockets[idx], normalize_node.inputs[0])  # Value, Value
        sockets[idx] = create_threshold_node(tree, uv_threshold, normalize_node.outputs[0])

    intersect_output = create_intersect_node(tree, *sockets)

    ## Step 3: Erode the blue channel and use as mask over intersection.
    # We erode to remove AA artifacts
    erode_node = tree.nodes.new('CompositorNodeDilateErode')
    erode_node.mode = 'STEP'
    erode_node.distance = -1
    tree.links.new(separate_node.outputs[2], erode_node.inputs[0])  # Blue, Mask

    mask_node = tree.nodes.new('CompositorNodeSetAlpha')
    mask_node.mode = 'APPLY'
    tree.links.new(intersect_output, mask_node.inputs[0])  # Value, Image
    tree.links.new(erode_node.outputs[0], mask_node.inputs[1])  # Mask, Alpha

    return mask_node.outputs[0]


class CompositorInitializer:
    """
    Class that sets up the compositor flow.
    """

    IMAGE_NAME = 'image-#'
    LABEL_NAME = 'label-#'

    def __call__(self, parameters: LabelGenerationParameters) -> None:
        """
        Setup the compositor flow. The compositor saves the image and the label. This function clears the previous nodes.
        """
        scene = bpy.context.scene
        tree = scene.node_tree

        scene.render.use_compositing = True
        scene.use_nodes = True
        scene.view_layers['ViewLayer'].use_pass_combined = True
        scene.view_layers['ViewLayer'].use_pass_ambient_occlusion = True
        scene.view_layers['ViewLayer'].use_pass_uv = True
        clear_nodes(tree)

        # Create input
        input_node = tree.nodes.new('CompositorNodeRLayers')

        # Create compositing steps and intersect
        image_threshold_output = create_image_threshold_path(tree, input_node.outputs[0], parameters.image_threshold)
        uv_threshold_output = create_uv_threshold_path(tree, input_node.outputs[2], parameters.uv_threshold)
        ao_threshold_output = create_ao_threshold_path(tree, input_node.outputs[3], parameters.ao_threshold)

        intersect_output = create_intersect_node(tree, image_threshold_output, uv_threshold_output)
        intersect_output = create_intersect_node(tree, intersect_output, ao_threshold_output)

        # Create output
        output_node = tree.nodes.new('CompositorNodeOutputFile')
        output_node.base_path = parameters.base_output_directory
        output_node.format.file_format = 'PNG'
        output_node.file_slots.new(self.LABEL_NAME)

        output_node.file_slots[0].path = self.IMAGE_NAME
        output_node.file_slots[1].path = self.LABEL_NAME

        tree.links.new(input_node.outputs['Image'], output_node.inputs[0])
        tree.links.new(intersect_output, output_node.inputs[1])

        composite_node = tree.nodes.new('CompositorNodeComposite')
        tree.links.new(input_node.outputs['Image'], composite_node.inputs[0])
