import bpy

from dataset_generation.models import WallSet, SurfaceParameters
from dataset_generation.surface_map_generator import SurfaceMapGenerator

WALLS = [
    'Base wall',
    'Door wall'
]


class WallSetLoader:
    """
    Class aimed at loading all available wall sets.
    """

    __surface_map_generator: SurfaceMapGenerator = SurfaceMapGenerator()

    def __call__(self) -> list[WallSet]:
        """
        Load all specified walls, their duplicates and their parameters.
        """

        wall_set = []

        for wall_name in WALLS:
            wall = bpy.data.objects[wall_name]
            wall_surface = self.__surface_map_generator(wall)

            surface_parameters = SurfaceParameters(
                wall.modifiers['GeometryNodes']['Input_15'],
                wall.modifiers['GeometryNodes']['Input_16'],
                wall.modifiers['GeometryNodes']['Input_6'],
                wall_surface
            )

            wall_duplicate = bpy.data.objects[wall_name + ' duplicate']
            wall_set.append(WallSet(wall, wall_duplicate, surface_parameters))

        return wall_set
