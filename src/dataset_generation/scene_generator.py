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
        - Create a crack marker, which is the intersection between the crack and the wall.
        - 'Carve the crack out of the wall' by calculating the difference between the wall and crack.
        - Align the camera with the crack.
        - Set the right materials for the world, wall and crack
        - Render the wall with and without crack.
        """
        crack.hide_render = True

        # Create a copy of the crack to serve as a marker and calculate the intersection with the wall.
        crack_marker = self.__obj_duplicator(crack)

        intersection_mod = crack_marker.modifiers.new('crack_intersect', 'BOOLEAN')
        intersection_mod.operation = 'INTERSECT'
        intersection_mod.use_self = True
        intersection_mod.use_hole_tolerant = True
        intersection_mod.object = parameters.wall_set.wall_duplicate

        # Carve the crack out of the wall
        wall = parameters.wall_set.wall
        wall.modifiers['Boolean'].object = crack

        # Move camera to object
        self.__camera_aligner(camera, crack, parameters.camera_rotation, parameters.camera_translation)

        # Set world and object materials
        crack_marker.data.materials.append(parameters.crack_material)
        wall.modifiers['GeometryNodes']['Input_13'] = parameters.wall_material
        bpy.data.worlds['World'].node_tree.nodes['Environment Texture'].image = parameters.world_texture

        # Start rendering
        self.__crack_renderer(crack_marker, parameters.output_file_name)
