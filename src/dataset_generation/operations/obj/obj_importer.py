import os
import bpy


class ObjImporter:
    """
    Operator for importing one or multiple .objs model from specific files
    """
    
    def __call__(self, directory: str, files: list[str]) -> list[bpy.types.Object]:
        """
        Import .obj files specified by a path
        """
        paths = [{'name': file} for file in files]
        bpy.ops.wm.obj_import(
            filepath=os.path.join(directory, paths[0]['name']),
            directory=directory,
            files=paths
        )
        objects = [bpy.data.objects[file_name[:-4]] for file_name in files] # We assume the file ends in .obj

        # Move the objects straight to the root collection
        scene_collection = bpy.context.scene.collection
        for obj in objects:
            if scene_collection not in obj.users_collection:
                for collection in obj.users_collection:
                    collection.objects.unlink(obj)
                scene_collection.objects.link(obj)

        return objects
        