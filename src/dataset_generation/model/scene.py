from dataclasses import dataclass

import bpy

from crack_generation.model import Surface


@dataclass
class Scene:
    """A set containing a wall object, its material, the generated surface of the wall and the other visible objects."""

    wall: bpy.types.Object
    material: bpy.types.Material
    surface: Surface
    visible_objects: list[bpy.types.Object]
