from dataclasses import dataclass

import bpy


@dataclass
class SceneParameters:
    """
    Parameters for the current scene.
    These should be randomly assigned (with reason).
    """

    brick_material: bpy.types.Material
    mortar_material: bpy.types.Material
    crack_material: bpy.types.Material

    world_texture: bpy.types.Image

    camera_translation: tuple[float, float, float]
    camera_rotation: tuple[float, float, float]

    output_file_name: str
