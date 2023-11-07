import bpy

from dataset_generation.models import WallSet, SurfaceParameters
from dataset_generation.surface_map_generator import SurfaceMapGenerator

SCENES = [
    ('Base wall', 'Base mortar', ['Pavement']),
    ('Door wall', 'Door mortar', ['Pavement 2', 'Plastic door'])
]


# Harcode these for now for performance
BRICK_WIDTH = 0.21
BRICK_HEIGHT = 0.05
MORTAR_SIZE = 0.01

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

        for wall_name, mortar_name, other_object_names in SCENES:
            wall = bpy.data.objects[wall_name]
            mortar = bpy.data.objects[mortar_name]

            wall_surface = self.__surface_map_generator(mortar)

            surface_parameters = SurfaceParameters(
                BRICK_WIDTH,
                BRICK_HEIGHT,
                MORTAR_SIZE,
                wall_surface
            )

            wall_set.append(WallSet(
                wall,
                mortar,
                [bpy.data.objects[name] for name in other_object_names],
                surface_parameters
            ))

        return wall_set
