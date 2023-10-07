import os
import bpy


class ObjImporter:
    """
    Operator for importing one or multiple .objs model from specific files
    """
    
    def __call__(self, directory: str, files: list[str]) -> None:
        """
        Import .obj files specified by a path
        """
        paths = [{'name': file} for file in files]
        bpy.ops.wm.obj_import(
            filepath=os.path.join(directory, paths[0]['name']),
            directory=directory,
            files=paths
        )
        