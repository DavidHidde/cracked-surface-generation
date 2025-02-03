from dataclasses import dataclass

import bpy

from .scene import Scene


@dataclass
class AssetCollection:
    """Collection of all loaded assets in the Blender scene which can be shuffled or are used ."""

    # Randomization
    scenes: list[Scene]
    world_textures: list[bpy.types.Image]

    # Placeholders used for creating cracks
    crack_displacement_texture: bpy.types.Image
    crack_displacement_mask: bpy.types.Image
