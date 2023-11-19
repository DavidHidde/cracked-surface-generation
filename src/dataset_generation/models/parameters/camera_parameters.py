import bpy

from dataclasses import dataclass


@dataclass
class CameraParameters:
    """
    Parameters concerning the allowed rotation of a camera.
    """

    camera_obj: bpy.types.Object

    rotation_min: tuple[float, float, float]
    rotation_max: tuple[float, float, float]

    translation_min: tuple[float, float, float]
    translation_max: tuple[float, float, float]
