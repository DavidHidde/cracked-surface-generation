import bpy
import numpy as np

from crack_generation import create_surface_from_image
from dataset_generation.model import AssetCollection

from dataset_generation.model.scene import Scene
from dataset_generation.node_injection_functions import modify_material_for_cracking


def load_surface_texture(wall: bpy.types.Object, material: bpy.types.Material) -> np.array:
    """Load the texture of a surface into a numpy array. This replicates the texture as applied on the object."""
    image_obj = material.node_tree.nodes['Displacement'].inputs['Height'].links[0].from_node.image
    img_width, img_height = image_obj.size
    pixel_array = np.array(image_obj.pixels).reshape(img_height, img_width, image_obj.channels)
    pixel_array = np.flip(pixel_array, axis=0)  # (0,0) is bottom left in Blender

    # Find UVs using the most Y-facing component (object space).
    mesh = wall.data
    uv_layer = mesh.uv_layers.active.data
    max_y = -np.inf
    for face in mesh.polygons:
        if face.normal.y > max_y:
            max_y = face.normal.y
            chosen_face = face
    uv_coords = np.array([uv_layer[loop_idx].uv for loop_idx in chosen_face.loop_indices], dtype=np.float32)

    # Finally, create the UV texture. This part assumes a rectangular face.
    [min_x, min_y] = np.rint(np.min(uv_coords, axis=0) * [img_width - 1, img_height - 1]).astype(np.int32)
    [max_x, max_y] = np.rint(np.max(uv_coords, axis=0) * [img_width - 1, img_height - 1]).astype(np.int32)
    X, Y = np.meshgrid(np.arange(min_x, max_x + 1), np.arange(min_y, max_y + 1))
    X, Y = X % img_width, Y % img_height

    return (pixel_array[Y, X, 0] * 255).squeeze().astype(np.uint8)


def fix_object_normals(obj: bpy.types.Object) -> None:
    """Fix normals of an object."""
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for face in obj.data.polygons:
        face.select = True
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')


def load_scene(
    scene_dict: dict,
    displacement_image: bpy.types.Image,
    displacement_mask: bpy.types.Image,
    crack_depth: float
) -> Scene:
    """Load a scene from a dict. This generates a surface given a wall model and modifies the material."""
    wall = bpy.data.objects[scene_dict['wall']]
    fix_object_normals(wall)
    material = wall.active_material

    surface_tex = load_surface_texture(
        wall,
        material
    )  # Note: Loading the surface before changing the material is necessary
    modify_material_for_cracking(material, displacement_image, displacement_mask, crack_depth)

    return Scene(
        wall=wall,
        material=material,
        surface=create_surface_from_image(surface_tex),
        visible_objects=[bpy.data.objects[obj_name] for obj_name in scene_dict['other']],
    )


def load_asset_collection(asset_collection_data: dict, crack_depth: float) -> AssetCollection:
    """Load the asset collection from a dict."""
    crack_displacement_image = bpy.data.images.new('crack_displacement_image', 10, 10)
    crack_displacement_mask = bpy.data.images.new('crack_displacement_mask', 10, 10)

    return AssetCollection(
        scenes=[load_scene(scene_dict, crack_displacement_image, crack_displacement_mask, crack_depth) for scene_dict in
            asset_collection_data["scenes"]],
        world_textures=[bpy.data.images[hdri_name] for hdri_name in asset_collection_data['hdris']],
        crack_displacement_texture=crack_displacement_image,
        crack_displacement_mask=crack_displacement_mask
    )
