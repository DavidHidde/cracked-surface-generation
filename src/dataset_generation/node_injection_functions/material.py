import bpy
import cv2
import numpy as np

UV_NODE_NAME = 'Crack UV Map Node'


def create_blurred_diff_texture(image: bpy.types.Image) -> bpy.types.Image:
    """Create a blurred version of the supplied image."""
    blurred_image = image.copy()
    width, height = blurred_image.size
    pixels = blurred_image.pixels
    pixel_arr = np.array(pixels).reshape((height, width, blurred_image.channels))

    # Blur 4 times with a small kernel
    for _ in range(4):
        pixel_arr = cv2.GaussianBlur(pixel_arr, ksize=(5, 5), sigmaX=5, sigmaY=5)

    blurred_image.pixels = pixel_arr.flatten()
    blurred_image.update()

    return blurred_image


def create_diff_texture_mix_path(
    tree: bpy.types.NodeTree,
    blurred: bpy.types.Image,
    mask: bpy.types.Image
) -> bpy.types.ShaderNodeMix:
    """Create the path which mixes the crack parts of the material with a blurred version."""
    mapping_node = tree.nodes['Mapping']
    uv_mapping_node = tree.nodes[UV_NODE_NAME]

    mask_node = tree.nodes.new('ShaderNodeTexImage')
    mask_node.image = mask
    tree.links.new(uv_mapping_node.outputs['UV'], mask_node.inputs['Vector'])

    aov_node = tree.nodes.new('ShaderNodeOutputAOV')
    aov_node.aov_name = 'Crack'
    tree.links.new(mask_node.outputs['Color'], aov_node.inputs['Color'])

    blurring_node = tree.nodes.new('ShaderNodeTexImage')
    blurring_node.image = blurred
    tree.links.new(mapping_node.outputs['Vector'], blurring_node.inputs['Vector'])

    mix_node = tree.nodes.new('ShaderNodeMix')
    mix_node.data_type = 'RGBA'
    mix_node.clamp_factor = True
    tree.links.new(mask_node.outputs['Color'], mix_node.inputs['Factor'])
    tree.links.new(blurring_node.outputs['Color'], mix_node.inputs['B'])
    return mix_node


def create_displacement_mix_path(
    tree: bpy.types.NodeTree,
    crack_displacement_tex: bpy.types.Image
) -> bpy.types.ShaderNodeMix:
    """Create the path which subtracts the crack from the displacement map"""
    mapping_node = tree.nodes[UV_NODE_NAME]

    crack_node = tree.nodes.new('ShaderNodeTexImage')
    crack_node.image = crack_displacement_tex
    crack_node.interpolation = 'Smart'
    tree.links.new(mapping_node.outputs['UV'], crack_node.inputs['Vector'])

    mix_node = tree.nodes.new('ShaderNodeMix')
    mix_node.data_type = 'RGBA'
    mix_node.clamp_factor = False
    mix_node.blend_type = 'SUBTRACT'
    tree.links.new(crack_node.outputs['Color'], mix_node.inputs['B'])
    return mix_node


def modify_material_for_cracking(
    material: bpy.types.Material,
    crack_mask_image: bpy.types.Image,
    crack_displacement_image: bpy.types.Image,
    crack_depth: float
) -> None:
    """
    Modify a material such that we can use the height map of the crack to create a crack in the wall.
    This flow relies on a couple of assumptions:
        1. Displacement is enabled for the material and for rendering.
        2. The material is setup using the standard material setup in Blender (Ctrl + Shift + T in the material editor).

    In summary, this function will try to add the following:
    1. A mix node for the diffuse texture, which mixes the standard texture with a blurred variant in the area of the
        crack to reduce artifacts.
    2. A subtract node for the displacement texture, which subtracts the crack height map from the regular displacement texture.
    """
    tree = material.node_tree

    # Create a UV map node which we will link to other texture nodes as input
    uv_map_node = tree.nodes.new('ShaderNodeUVMap')
    uv_map_node.name = UV_NODE_NAME

    # Modify diffuse texture
    bsdf_node = tree.nodes['Principled BSDF']
    diff_tex_node = bsdf_node.inputs['Base Color'].links[0].from_node
    tex_mix_node = create_diff_texture_mix_path(
        tree,
        create_blurred_diff_texture(diff_tex_node.image),
        crack_mask_image
    )

    tree.links.new(diff_tex_node.outputs['Color'], tex_mix_node.inputs['A'])
    tree.links.new(tex_mix_node.outputs['Result'], bsdf_node.inputs['Base Color'])

    # Modify displacement map
    displacement_node = tree.nodes['Displacement']
    displacement_tex_node = displacement_node.inputs['Height'].links[0].from_node

    displacement_mix_node = create_displacement_mix_path(tree, crack_displacement_image)
    displacement_mix_node.inputs['Factor'].default_value = crack_depth

    tree.links.new(displacement_tex_node.outputs['Color'], displacement_mix_node.inputs['A'])
    tree.links.new(displacement_mix_node.outputs['Result'], displacement_node.inputs['Height'])
