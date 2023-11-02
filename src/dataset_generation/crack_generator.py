import os

import bpy
import numpy as np
from mathutils import Vector

from crack_generation import CrackModelGenerator
from crack_generation.models import CrackParameters
from crack_generation.operations import ObjFileExporter
from dataset_generation.models import SurfaceParameters
from dataset_generation.operations.obj import ObjImporter

CRACK_WALL_DISPLACEMENT_PERCENT = 0.5


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

    def __call__(
            self,
            crack_parameters: CrackParameters,
            surface_parameters: SurfaceParameters,
            file_path: str
    ) -> bpy.types.Object:
        """
        Create a model, export it to a file
        """
        file_parts = file_path.split(os.pathsep)
        file_dir = os.path.join(os.getcwd(), *file_parts[:-1])
        file_name = file_parts[-1]

        model = (CrackModelGenerator())(crack_parameters, surface_parameters)
        self.__obj_file_exporter(model, file_path)
        [crack_obj] = self.__obj_file_importer(file_dir, [file_name])

        # Set to the correct position
        crack_obj.rotation_euler = [np.pi / 2, 0., 0.]
        crack_obj.scale = [1. / 10] * 3
        crack_obj.location += Vector(
            [
                model.point_means[0],
                model.point_means[2],
                model.point_means[1]
            ]) / surface_parameters.surface_map.grid_factor
        crack_obj.location += Vector([*surface_parameters.surface_map.bounding_box.min_vertex])
        apply_transformations(crack_obj)
        crack_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())

        # Move the crack into the wall
        crack_obj.location += Vector([0., CRACK_WALL_DISPLACEMENT_PERCENT * crack_obj.dimensions.y, 0.])
        apply_transformations(crack_obj)
        crack_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())

        # Create the crack intersection modifier
        intersection_mod = crack_obj.modifiers.new('crack_intersect', 'BOOLEAN')
        intersection_mod.operation = 'INTERSECT'
        intersection_mod.use_self = True

        return crack_obj
