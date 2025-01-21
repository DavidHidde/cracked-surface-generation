from dataclasses import dataclass

import bpy

from .scene import Scene


@dataclass
class AssetCollection:
    """Collection of all loaded assets in the Blender scene which can be shuffled."""

    scenes: list[Scene]
    world_textures: list[bpy.types.Image]
