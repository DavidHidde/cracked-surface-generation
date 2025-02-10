import bpy

from dataclasses import dataclass

from crack_generation.model import Crack, Surface
from .scene import Scene


@dataclass
class RenderIteration:
    """A single iteration of the dataset generation. This represents what the state of Blender should be in when rendering."""

    index: int

    scene: Scene
    surface: Surface
    face: bpy.types.MeshPolygon
    uv_map: bpy.types.MeshUVLoopLayer
    world_texture: bpy.types.Image
    crack: Crack

    camera_translation: tuple[float, float, float]
    camera_rotation: tuple[float, float, float]
