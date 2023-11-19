from dataclasses import dataclass

import bpy

from crack_generation.models.surface import Surface


@dataclass
class WallSet:
    """
    A set containg a wall object, it's duplicate and the surface parameters.
    """
    
    wall: bpy.types.Object
    mortar: bpy.types.Object
    surface: Surface
    other_objects: list[bpy.types.Object]
