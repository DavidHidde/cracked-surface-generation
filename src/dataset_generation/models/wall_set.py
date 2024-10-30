from dataclasses import dataclass

import bpy

from crack_generation.models.surface import Surface


@dataclass
class WallSet:
    """
    A set containing a wall object and the surface parameters.
    """
    
    wall: bpy.types.Object
    surface: Surface
    other_objects: list[bpy.types.Object]
