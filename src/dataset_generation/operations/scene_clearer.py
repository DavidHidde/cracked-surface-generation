import bpy

from dataset_generation.models import Configuration


class SceneClearer:
    """
    Operation that clears the scene aside from a single marked collection
    """

    def __call__(self, config: Configuration) -> None:
        """
        Clear objects from the scene aside from the safe collection
        """
        for collection in bpy.data.collections:
            if collection.name not in config.asset_collection.safe_collections:
                for obj in collection.objects:
                    bpy.data.objects.remove(obj, do_unlink=True)
                bpy.data.collections.remove(collection, do_unlink=True)

        # Remove lingering objects
        for obj in bpy.context.scene.collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

        # Remove any unused garbage and set everything else to invisible
        for iterable in [bpy.data.meshes, bpy.data.cameras, bpy.data.objects]:
            for iter_object in iterable:
                if iter_object.users == 0:
                    iterable.remove(iter_object, do_unlink=True)
                elif type(iter_object) is bpy.types.Object:
                    iter_object.hide_render = True
