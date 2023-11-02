from dataclasses import dataclass

import bpy

from .surface_parameters import SurfaceParameters


@dataclass
class WallSet:
    """
    A set containg a wall object, it's duplicate and the surface parameters.
    """
    
    wall: bpy.types.Object
    mortar: bpy.types.Object
    other_objects: list[bpy.types.Object]
    surface_parameters: SurfaceParameters
