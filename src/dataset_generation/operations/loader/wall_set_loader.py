import os
import pickle
from pathlib import Path

import bpy

from crack_generation.models.surface import SurfaceDimensions, Surface
from dataset_generation.models import WallSet
from dataset_generation.operations.generators import SurfaceMapGenerator

CACHE_DIRECTORY = 'cache'

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
        Path(CACHE_DIRECTORY).mkdir(parents=True, exist_ok=True)
        for scene_dict in scene_data:
            wall = bpy.data.objects[scene_dict['wall']]
            surface = self.load_cached_surface(wall, scene_dict)

            wall_set.append(WallSet(
                wall,
                surface,
                [bpy.data.objects[name] for name in scene_dict['other']]
            ))

        return wall_set

    def load_cached_surface(self, wall: bpy.types.Object, scene_dict: dict) -> Surface:
        """
        Load a surface file based on its name. If it doesn't exist, create it.
        """
        filename = os.path.join(CACHE_DIRECTORY, wall.name + '.surface')
        if os.path.exists(filename):
            with open(filename, 'rb') as surface_file:
                return pickle.load(surface_file)

        surface = Surface(
            self.__surface_map_generator(wall),
            SurfaceDimensions(**scene_dict['wall_properties'])
        )
        with open(filename, 'wb') as surface_file:
            pickle.dump(surface, surface_file)

        return surface