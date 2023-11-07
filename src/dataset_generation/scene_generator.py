import bpy

from dataset_generation.models import SceneParameters
from dataset_generation.operations import CrackRenderer
from dataset_generation.operations.obj import CameraAligner, ObjDuplicator


class SceneGenerator:
    """
    Generator aimed at generating a scene using a crack, wall and a camera
    """

    __camera_aligner: CameraAligner = CameraAligner()
    __crack_renderer: CrackRenderer = CrackRenderer()
    __obj_duplicator: ObjDuplicator = ObjDuplicator()

    def __call__(
            self,
            camera: bpy.types.Object,
            crack: bpy.types.Object,
            parameters: SceneParameters
    ) -> None:
        """
        Generate a scene using a wall and a crack. This consist of the following steps:
        - Set all the correct materials
        - Align the camera
        - Make all relevant objects visible
        - Render the crack
        """
        wall = parameters.wall_set.wall

        # Set world and object materials
        crack.data.materials.append(parameters.crack_material)
        wall.data.materials[0] = parameters.wall_material
        bpy.data.worlds['World'].node_tree.nodes['Environment Texture'].image = parameters.world_texture

        # Move camera to object
        self.__camera_aligner(camera, crack, parameters.camera_rotation, parameters.camera_translation)

        # Make all dependent objects visible for the render
        wall.hide_render = False
        for obj in parameters.wall_set.other_objects:
            obj.hide_render = False

        # Start rendering
        self.__crack_renderer(crack, wall, parameters.output_file_name)
