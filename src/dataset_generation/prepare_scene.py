import bpy
import cv2
import mathutils
import numpy as np

from dataset_generation.model import RenderIteration, Configuration, AssetCollection
from dataset_generation.node_injection_functions import UV_NODE_NAME


def align_camera(camera: bpy.types.Camera, render_iteration: RenderIteration) -> None:
    """Align a camera to a crack and move it using a rotation and translation factor."""
    # Move the camera to the crack and point to it. Take into account that image origin is top-left and X is inverse along Y+
    crack_height_map = np.flip(np.flip(render_iteration.crack.crack_height_map, axis=0), axis=1)
    center_factor = np.average((crack_height_map > 0).nonzero(), axis=1) / np.array(crack_height_map.shape)

    wall = render_iteration.scene.wall
    vertices = np.array([wall.data.vertices[vertex].co for vertex in render_iteration.face.vertices])
    min_vertex = np.min(vertices, axis=0)  # Assume convex hull for center
    max_vertex = np.max(vertices, axis=0)
    axis_align_idx = np.argmin(max_vertex - min_vertex)
    center_factor = mathutils.Vector(
        [
            center_factor[1] if axis_align_idx == 0 else np.average(center_factor),
            center_factor[1] if axis_align_idx != 0 else np.average(center_factor),
            center_factor[0]
        ]
    )
    crack_center = mathutils.Vector(min_vertex) + mathutils.Vector((max_vertex - min_vertex)) * center_factor

    camera.location = wall.matrix_world @ crack_center
    camera.rotation_euler = render_iteration.face.normal.to_track_quat('-Y', 'Z').to_euler()

    # Add iteration rotation and translation. For translation, we take the rotation into account.
    translation = mathutils.Vector(
        [
            render_iteration.camera_translation[0],
            -render_iteration.camera_translation[1],  # Make it negative to move away from the wall
            render_iteration.camera_translation[2]
        ]
    )
    translation.rotate(camera.rotation_euler)
    print('Base translation:', render_iteration.camera_translation, 'Rotated:', translation)
    camera.location = mathutils.Matrix.Translation(translation) @ camera.location

    rotation = render_iteration.camera_rotation
    camera.rotation_euler.x += np.pi / 2 + rotation[0]  # Camera points down by default, so we add 90 degrees
    camera.rotation_euler.y += rotation[1]
    camera.rotation_euler.z += rotation[2]


def make_all_invisible(exceptions: list[bpy.types.Object]) -> None:
    """Make all objects in the scene invisible aside from the objects listed."""
    for collection in bpy.data.collections:
        for obj in collection.objects:
            obj.hide_render = True

    for obj in exceptions:
        obj.hide_render = False


def apply_crack_texture(asset_collection: AssetCollection, render_iteration: RenderIteration) -> None:
    """Apply the crack displacement texture by modifying the set Blender images."""
    height_map = np.flip(render_iteration.crack.crack_height_map, axis=0)
    height_map = np.tile(np.expand_dims(height_map, axis=-1), [1, 1, 4])
    height_map[:, :, 3] = 1.
    height, width, _ = height_map.shape
    asset_collection.crack_displacement_texture.scale(width, height)
    asset_collection.crack_displacement_texture.pixels = height_map.flatten()
    asset_collection.crack_displacement_texture.update()

    mask_arr = np.flip(render_iteration.crack.crack_height_map, axis=0)
    mask = mask_arr > 0
    mask_arr[mask] = 1.
    mask_arr[~mask] = 0.
    mask_arr = cv2.dilate(mask_arr, np.ones((5, 5), dtype=np.uint8), iterations=1)
    mask_arr = np.tile(np.expand_dims(mask_arr, axis=-1), [1, 1, 4])
    mask_arr[:, :, 3] = 1.
    asset_collection.crack_displacement_mask.scale(width, height)
    asset_collection.crack_displacement_mask.pixels = mask_arr.flatten()
    asset_collection.crack_displacement_mask.update()

    render_iteration.scene.material.node_tree.nodes[UV_NODE_NAME].uv_map = render_iteration.uv_map.name


def prepare_scene(config: Configuration, render_iteration: RenderIteration) -> None:
    """Prepare the scene for rendering by applying the iteration settings."""
    make_all_invisible(render_iteration.scene.visible_objects + [render_iteration.scene.wall])
    bpy.data.worlds['World'].node_tree.nodes['Environment Texture'].image = render_iteration.world_texture
    apply_crack_texture(config.asset_collection, render_iteration)
    align_camera(config.camera_parameters.camera_obj, render_iteration)
