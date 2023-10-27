from dataclasses import dataclass

import bpy


@dataclass
class MaterialsContainer:
    """
    Class holding all materials/textures used for scene generation.
    The goal is to ensure that we only load these once and reuse them throughout the generation.
    """
    
    wall_materials: list[bpy.types.Material]
    crack_materials: list[bpy.types.Material]
    
    world_textures: list[bpy.types.Image]
