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
    for idx, face in enumerate(mesh.polygons):
        if face.normal.y > max_y:
            max_y = face.normal.y
            chosen_face = face
    uv_coords = np.array([uv_layer[loop_idx].uv for loop_idx in chosen_face.loop_indices], dtype=np.float32)

    # Finally, create the UV texture. This part assumes a rectangular face.
    [min_x, min_y] = np.rint(np.min(uv_coords, axis=0) * [img_width - 1, img_height - 1]).astype(np.int32)
    [max_x, max_y] = np.rint(np.max(uv_coords, axis=0) * [img_width - 1, img_height - 1]).astype(np.int32)
    X, Y = np.meshgrid(np.arange(min_x, max_x + 1), np.arange(min_y, max_y + 1))
    X, Y = X % img_width, Y % img_height

    return (pixel_array[Y, X, 0] * 255).squeeze()


def load_scene(scene_dict: dict) -> Scene:
    """Load a scene from a dict. This generates a surface given a wall model and modifies the material."""
    wall = bpy.data.objects[scene_dict['wall']]
    material = wall.active_material

    surface_tex = load_surface_texture(
        wall,
        material
    )  # Note: Loading the surface before changing the material is necessary
    modify_material_for_cracking(material)

    return Scene(
        wall=wall,
        material=material,
        surface=create_surface_from_image(surface_tex),
        visible_objects=[bpy.data.objects[obj_name] for obj_name in scene_dict['other']],
    )


def load_asset_collection(asset_collection_data: dict) -> AssetCollection:
    """Load the asset collection from a dict."""
    return AssetCollection(
        scenes=[load_scene(scene_dict) for scene_dict in asset_collection_data["scenes"]],
        world_textures=[bpy.data.images[hdri_name] for hdri_name in asset_collection_data['hdris']]
    )
