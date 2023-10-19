import os

import bpy
import numpy as np
from mathutils import Vector

from crack_generation import CrackModelGenerator
from crack_generation.models import CrackParameters
from crack_generation.util import ObjFileExporter
from dataset_generation.models import SurfaceMap
from dataset_generation.operations.obj import ObjImporter


def apply_transformations(crack: bpy.types.Object):
    """
    Apply the transformations to an object
    """
    matrix_basis = crack.matrix_basis
    if hasattr(crack.data, "transform"):
        crack.data.transform(matrix_basis)
    for child in crack.children:
        child.matrix_local = matrix_basis @ child.matrix_local

    crack.matrix_basis.identity()


class CrackGenerator:
    """
    Class that creates a crack based on a surface and imports it into Blender.
    """

    __obj_file_importer: ObjImporter = ObjImporter()
    __obj_file_exporter: ObjFileExporter = ObjFileExporter()

    def __call__(self, parameters: CrackParameters, surface_map: SurfaceMap, file_path: str) -> bpy.types.Object:
        """
        Create a model, export it to a file
        """
        file_parts = file_path.split(os.pathsep)
        file_dir = os.path.join(os.getcwd(), *file_parts[:-1])
        file_name = file_parts[-1]

        model = (CrackModelGenerator())(parameters, surface_map)
        self.__obj_file_exporter(model, file_path)
        [crack_obj] = self.__obj_file_importer(file_dir, [file_name])

        # Set to the correct position
        crack_obj.rotation_euler = [np.pi / 2, 0., 0.]
        crack_obj.scale = [1. / 10] * 3
        crack_obj.location += Vector([model.point_means[0], model.point_means[2], model.point_means[1]]) / 1000
        crack_obj.location += Vector([*surface_map.bounding_box.min_vertex])
        apply_transformations(crack_obj)
        crack_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())

        # Move 90% of the crack into the wall
        crack_obj.location += Vector([0., 0.9 * crack_obj.dimensions.y, 0.])
        apply_transformations(crack_obj)
        crack_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())

        return crack_obj
