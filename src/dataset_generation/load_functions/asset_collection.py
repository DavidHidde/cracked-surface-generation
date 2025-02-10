import bpy
import cv2
import numpy as np

from crack_generation import create_surface_from_image
from dataset_generation.model import AssetCollection

from dataset_generation.model.scene import Scene
from dataset_generation.node_injection_functions import modify_material_for_cracking, UV_NODE_NAME

MAX_TEXTURE_DIM = 8192


def create_crack_uv_map(obj: bpy.types.Object, face: bpy.types.MeshPolygon) -> bpy.types.MeshUVLoopLayer:
    """Create a UV Map which will be used to fit the crack on the wall. We need this to avoid irregular uv maps."""
    mesh = obj.data
    uv_layer = mesh.uv_layers.new()

    # Set all UVs to (0,0)
    for other_face in mesh.polygons:
        for loop_idx in other_face.loop_indices:
            uv_layer.data[loop_idx].uv = (0, 0)

    # Normalize UV range to fit the new texture
    active_uv_layer = mesh.uv_layers.active
    uvs = np.array([active_uv_layer.data[loop_idx].uv for loop_idx in face.loop_indices])
    max_uv, min_uv = np.max(uvs, axis=0), np.min(uvs, axis=0)
    uv_range = max_uv - min_uv

    for loop_idx in face.loop_indices:
        old_uvs = active_uv_layer.data[loop_idx].uv
        new_uvs = uv_layer.data[loop_idx].uv
        new_uvs.x = (old_uvs.x - min_uv[0]) / uv_range[0]
        new_uvs.y = (old_uvs.y - min_uv[1]) / uv_range[1]

    return uv_layer


def load_surface_texture(obj: bpy.types.Object, face: bpy.types.MeshPolygon, image_obj: bpy.types.Image) -> np.array:
    """Load the texture of a surface into a numpy array. This replicates the texture as applied on the object."""
    img_width, img_height = image_obj.size
    pixel_array = np.array(image_obj.pixels).reshape(img_height, img_width, image_obj.channels)

    uv_layer = obj.data.uv_layers.active.data
    uv_coords = np.array([uv_layer[loop_idx].uv for loop_idx in face.loop_indices], dtype=np.float32)

    # Create the UV texture. This part assumes a rectangular face.
    [min_x, min_y] = np.rint(np.min(uv_coords, axis=0) * [img_width - 1, img_height - 1]).astype(np.int32)
    [max_x, max_y] = np.rint(np.max(uv_coords, axis=0) * [img_width - 1, img_height - 1]).astype(np.int32)
    X, Y = np.meshgrid(np.arange(min_x, max_x + 1), np.arange(min_y, max_y + 1))
    X, Y = X % img_width, Y % img_height
    uv_mapped = np.flip(
        (pixel_array[Y, X, 0] * 255).squeeze().astype(np.uint8),
        axis=0
    )  # (0,0) is bottom left in Blender

    scale_factor = np.max([uv_mapped.shape[0] / MAX_TEXTURE_DIM, uv_mapped.shape[1] / MAX_TEXTURE_DIM])
    if scale_factor > 1:
        uv_mapped = cv2.resize(
            uv_mapped,
            (int(uv_mapped.shape[1] / scale_factor), int(uv_mapped.shape[0] / scale_factor)),  # width & height flipped
            interpolation=cv2.INTER_AREA
        )

    return uv_mapped


def load_scene(
    scene_dict: dict,
    displacement_image: bpy.types.Image,
    displacement_mask: bpy.types.Image,
    crack_depth: float
) -> Scene:
    """Load a scene from a dict. This generates a surface given a wall model and modifies the material."""
    wall = bpy.data.objects[scene_dict['wall']]
    material = wall.active_material  # Assume a single material

    displacement_node_input_node = material.node_tree.nodes['Displacement'].inputs['Height'].links[0].from_node
    if not material.node_tree.nodes.get(UV_NODE_NAME):
        image_obj = displacement_node_input_node.image
        modify_material_for_cracking(material, displacement_mask, displacement_image, crack_depth)
    else:
        image_obj = displacement_node_input_node.inputs['A'].links[0].from_node.image

    surface_collection = []
    faces = [face for face in wall.data.polygons if face.use_freestyle_mark]
    for face in faces:
        surface_tex = load_surface_texture(wall, face, image_obj)
        surface = create_surface_from_image(surface_tex)
        uv_map = create_crack_uv_map(wall, face)
        surface_collection.append((face, uv_map, surface))

    return Scene(
        wall=wall,
        material=material,
        surfaces=surface_collection,
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
