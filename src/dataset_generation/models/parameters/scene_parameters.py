from dataclasses import dataclass

import bpy

from ...models.wall_set import WallSet


@dataclass
class SceneParameters:
    """
    Parameters detailing the configuration for the current scene.
    These should be randomly assigned (with reason).
    """
    wall_set: WallSet

    wall_material: bpy.types.Material
    world_texture: bpy.types.Image

    camera_translation: tuple[float, float, float]
    camera_rotation: tuple[float, float, float]
