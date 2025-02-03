import bpy
import cv2
import mathutils
import numpy as np

from crack_generation.model import Crack
from dataset_generation.model import RenderIteration, Configuration, AssetCollection


def align_camera(camera: bpy.types.Camera, render_iteration: RenderIteration) -> None:
    """Align a camera to a crack and move it using a rotation and translation factor."""
    # Move the camera to the crack and point to it. Take into account that image origin is top-left and X is inverse along Y+
    crack_height_map = np.flip(np.flip(render_iteration.crack.crack_height_map, axis=0), axis=1)
    center_factor = np.average((crack_height_map > 0).nonzero(), axis=1) / np.array(crack_height_map.shape)
    center_factor = mathutils.Vector(
        [center_factor[1], np.average(center_factor), center_factor[0]]
    )  # width, depth, height

    wall = render_iteration.scene.wall
    max_y = -np.inf
    for face in wall.data.polygons:
        if face.normal.y > max_y:
            max_y = face.normal.y
            chosen_face = face
    vertices = np.array([wall.data.vertices[vertex].co for vertex in chosen_face.vertices])
    vertex_sums = np.sum(vertices, axis=1)  # Assume mostly x-aligned rectangle, simple sums will work for finding min/max
    min_vertex = vertices[np.argmin(vertex_sums), :]
    max_vertex = vertices[np.argmax(vertex_sums), :]
    crack_center = mathutils.Vector(min_vertex) + mathutils.Vector((max_vertex - min_vertex)) * center_factor

    camera.location = wall.matrix_world @ crack_center
    camera.rotation_euler = chosen_face.normal.to_track_quat('-Y', 'Z').to_euler()

    # Add iteration rotation and translation - we do not take the normal direction into account for this.
    rotation = render_iteration.camera_rotation
    translation = render_iteration.camera_translation
    camera.rotation_euler.x += np.pi / 2 + rotation[0]  # Camera points down by default, so we add 90 degrees
    camera.rotation_euler.y += rotation[1]
    camera.rotation_euler.z += rotation[2]
    camera.location = mathutils.Matrix.Translation(translation) @ camera.location


def make_all_invisible(exceptions: list[bpy.types.Object]) -> None:
    """Make all objects in the scene invisible aside from the objects listed."""
    for collection in bpy.data.collections:
        for obj in collection.objects:
            obj.hide_render = True

    for obj in exceptions:
        obj.hide_render = False


def apply_crack_texture(asset_collection: AssetCollection, crack: Crack) -> None:
    """Apply the crack displacement texture by modifying the set Blender images."""
    height_map = np.flip(crack.crack_height_map, axis=0)
    height_map = np.tile(np.expand_dims(height_map, axis=-1), [1, 1, 4])
    height_map[:, :, 3] = 1.
    height, width, _ = height_map.shape
    asset_collection.crack_displacement_texture.scale(width, height)
    asset_collection.crack_displacement_texture.pixels = height_map.flatten()
    asset_collection.crack_displacement_texture.update()

    mask_arr = np.flip(crack.crack_height_map, axis=0)
    mask = mask_arr > 0
    mask_arr[mask] = 1.
    mask_arr[~mask] = 0.
    mask_arr = cv2.dilate(mask_arr, np.ones((5, 5), dtype=np.uint8), iterations=1)
    mask_arr = np.tile(np.expand_dims(mask_arr, axis=-1), [1, 1, 4])
    mask_arr[:, :, 3] = 1.
    asset_collection.crack_displacement_mask.scale(width, height)
    asset_collection.crack_displacement_mask.pixels = mask_arr.flatten()
    asset_collection.crack_displacement_mask.update()


def prepare_scene(config: Configuration, render_iteration: RenderIteration) -> None:
    """Prepare the scene for rendering by applying the iteration settings."""
    make_all_invisible(render_iteration.scene.visible_objects + [render_iteration.scene.wall])
    bpy.data.worlds['World'].node_tree.nodes['Environment Texture'].image = render_iteration.world_texture
    apply_crack_texture(config.asset_collection, render_iteration.crack)
    align_camera(config.camera_parameters.camera_obj, render_iteration)
