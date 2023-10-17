import bpy


class ObjDuplicator:
    """
    Operation for duplicating objects.
    """
    
    def __call__(self, src_obj: bpy.types.Object) -> bpy.types.Object:
        """
        Duplciate the specified object, link it to the base scene collection
        and return it.
        """
        new_obj = src_obj.copy()
        new_obj.data = src_obj.data.copy()
        bpy.context.scene.collection.objects.link(new_obj)
        return new_obj
