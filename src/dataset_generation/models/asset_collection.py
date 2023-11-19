from dataclasses import dataclass

import bpy

from .wall_set import WallSet


@dataclass
class AssetCollection:
    """
    Collection of all loaded assets in the scene.
    """
    
    safe_collections: list[str]
    
    label_material: bpy.types.Material
    world_textures: list[bpy.types.Image]
    wall_materials: list[bpy.types.Material]
    scenes: list[WallSet]
