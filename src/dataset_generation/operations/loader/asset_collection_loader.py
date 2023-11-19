import bpy

from .wall_set_loader import WallSetLoader
from dataset_generation.models import AssetCollection


class AssetCollectionLoader:
    """
    Loader class for loading in all assets for the config.
    """

    __wall_set_loader: WallSetLoader = WallSetLoader()

    def __call__(self, asset_collection_data) -> AssetCollection:
        """
        Load the asset collection from a yaml class.
        """
        return AssetCollection(
            asset_collection_data['safe_collections'],
            bpy.data.materials[asset_collection_data['label_material']],
            [bpy.data.images[hdri_name] for hdri_name in asset_collection_data['hdris']],
            [bpy.data.materials[material_name] for material_name in asset_collection_data['materials']],
            self.__wall_set_loader(asset_collection_data['scenes'])
        )
