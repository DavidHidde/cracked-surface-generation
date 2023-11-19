import bpy

from crack_generation.models.surface import SurfaceDimensions, Surface
from dataset_generation.models import WallSet
from dataset_generation.operations.generators import SurfaceMapGenerator


class WallSetLoader:
    """
    Class aimed at loading all available wall sets.
    """

    __surface_map_generator: SurfaceMapGenerator = SurfaceMapGenerator()

    def __call__(self, scene_data: list[dict]) -> list[WallSet]:
        """
        Load all specified walls, their duplicates and their parameters.
        """

        wall_set = []

        for scene_dict in scene_data:
            wall = bpy.data.objects[scene_dict['wall']]
            mortar = bpy.data.objects[scene_dict['mortar']]

            surface = Surface(
                self.__surface_map_generator(mortar),
                SurfaceDimensions(**scene_dict['wall_properties'])
            )

            wall_set.append(WallSet(
                wall,
                mortar,
                surface,
                [bpy.data.objects[name] for name in scene_dict['other']]
            ))

        return wall_set
