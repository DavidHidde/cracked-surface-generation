import bpy
import mathutils
import numpy as np
from mathutils import Vector


class CameraAligner:
    """
    Class that aims to align a camera given a set of parameters
    """

    def __call__(
            self,
            camera: bpy.types.Object,
            crack: bpy.types.Object,
            rotation: tuple[float, float, float],
            translation: tuple[float, float, float]
    ) -> None:
        """
        Align a camera to a crack and move it using a rotation and translation factor.
        The basis rotation is parallel to the x-axis and the camera is 1 meter horizontally away
        from the crack.
        """
        crack_center = sum((Vector(vertex) for vertex in crack.bound_box), Vector()) / 8.
        camera.location = crack.matrix_world @ crack_center

        # Set rotation and translation
        camera.rotation_euler = [np.pi / 2 + rotation[0], rotation[1], rotation[2]]
        camera.location = mathutils.Matrix.Translation(translation) @ camera.location
