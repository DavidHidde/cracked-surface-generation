import os

import bpy
import numpy as np
from mathutils import Vector

from crack_generation.crack_generator import CrackGenerator
from crack_generation.models.crack.parameters.crack_generation_parameters import CrackGenerationParameters
from crack_generation.models.surface.surface import Surface
from crack_generation.operations import ObjFileExporter
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


class CrackModelGenerator:
    """
    Class that creates a crack based on a surface and imports it into Blender.
    """

    __obj_file_importer: ObjImporter = ObjImporter()
    __obj_file_exporter: ObjFileExporter = ObjFileExporter()

    def __call__(
            self,
            crack_parameters: CrackGenerationParameters,
            surface: Surface,
            file_path: str
    ) -> bpy.types.Object:
        """
        Create a model, export it to a file
        """
        file_parts = file_path.split(os.pathsep)
        file_dir = os.path.join(os.getcwd(), *file_parts[:-1])
        file_name = file_parts[-1]

        model = (CrackGenerator())(crack_parameters, surface)
        self.__obj_file_exporter(model, file_path)
        [crack_obj] = self.__obj_file_importer(file_dir, [file_name])

        # Set to the correct position
        crack_obj.rotation_euler = [np.pi / 2, 0., 0.]
        crack_obj.scale = [1. / 1000] * 3
        crack_obj.location += Vector(
            [
                model.mesh.vertex_means[0],
                model.mesh.vertex_means[2],
                model.mesh.vertex_means[1]
            ]) / surface.map.grid_factor
        crack_obj.location += Vector([*surface.map.bounding_box.min_vertex])
        apply_transformations(crack_obj)
        crack_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())

        # Move the crack into the wall
        crack_obj.location += Vector([0., CRACK_WALL_DISPLACEMENT_PERCENT * crack_obj.dimensions.y, 0.])
        apply_transformations(crack_obj)
        crack_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())

        return crack_obj
