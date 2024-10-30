import bpy

from dataset_generation.models import Configuration
from dataset_generation.models.parameters import SceneParameters
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
            crack: bpy.types.Object,
            config: Configuration,
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
        self.__camera_aligner(
            config.camera_parameters.camera_obj,
            crack,
            parameters.camera_rotation,
            parameters.camera_translation
        )

        # Make all dependent objects visible for the render and set the crack in the wall
        wall.hide_render = False
        crack.hide_render = True
        wall.modifiers.get('crack_difference', self.add_crack_modifier(wall)).object = crack
        for obj in parameters.wall_set.other_objects:
            obj.hide_render = False

        # Start rendering
        self.__crack_renderer(
            crack,
            wall,
            config.label_parameters,
            parameters,
            config.output_images_directory,
            config.output_labels_directory
        )

    def add_crack_modifier(self, wall: bpy.types.Object):
        """
        Create a new boolean modifier to handle creating a crack in the wall and return it.
        """
        modifier = wall.modifiers.new(name='crack_difference', type='BOOLEAN')
        modifier.operation = 'DIFFERENCE'
        modifier.operand_type = 'OBJECT'
        modifier.solver = 'EXACT'
        modifier.show_render = True
        return modifier
