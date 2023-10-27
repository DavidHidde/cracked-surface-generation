import bpy

from dataset_generation.models import MaterialsContainer

WALL_MATERIALS = [
    'Red brick - white mortar'
]

CRACK_MATERIALS = [
    'Marker - foreground'
]

WORLD_TEXTURES = [
    'pond_bridge_night_4k.exr',
    'rotes_rathaus_4k.exr',
    'studio_garden_4k.exr',
    'stuttgart_suburbs_4k.exr',
    'urban_street_01_4k.exr'
]


class MaterialLoader:
    """
    Simple class loading all materials and textures.
    """

    def __call__(self) -> MaterialsContainer:
        """
        Load all materials.
        """

        return MaterialsContainer(
            [bpy.data.materials[material_name] for material_name in WALL_MATERIALS],
            [bpy.data.materials[material_name] for material_name in CRACK_MATERIALS],
            [bpy.data.images[image_name] for image_name in WORLD_TEXTURES]
        )
