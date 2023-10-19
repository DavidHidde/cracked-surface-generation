import bpy

from dataset_generation.operations import MaterialLoader, CrackRenderer
from dataset_generation.operations.obj import CameraAligner, ObjDuplicator

HDRIS = []


class SceneGenerator:
    """
    Generator aimed at generating a scene using a crack, wall and a camera
    """

    __camera_aligner: CameraAligner = CameraAligner()
    __crack_renderer: CrackRenderer = CrackRenderer()
    __obj_duplicator: ObjDuplicator = ObjDuplicator()


    def __call__(
            self,
            wall: bpy.types.Object,
            camera: bpy.types.Object,
            crack: bpy.types.Object,
            materials: dict[str, dict[str, bpy.types.Material]]
    ) -> None:
        """
        Generate a scene using a wall and a crack. This consist of the following steps:
        - Create a crack marker, which is the intersection between the crack and the wall.
        - 'Carve the crack out of the wall' by calculating the difference between the wall and crack.
        - Align the camera with the crack.
        - Render the wall with and without crack.
        """
        wall = bpy.data.objects[wall.name]  # Get unevaluated object
        crack.hide_render = True

        # Create a copy of the crack to serve as a marker and calculate the intersection with the wall.
        crack_marker = self.__obj_duplicator(crack)
        crack_marker.data.materials.append(materials[MaterialLoader.KEYWORD_FOREGROUND])

        intersection_mod = crack_marker.modifiers.new('crack_intersect', 'BOOLEAN')
        intersection_mod.operation = 'INTERSECT'
        intersection_mod.use_self = True
        intersection_mod.use_hole_tolerant = True
        intersection_mod.object = wall

        # Carve the crack out of the wall
        wall.modifiers['Boolean'].object = crack

        # Move camera to object
        self.__camera_aligner(camera, crack, (0., 0., 0.), (0., 0., 0.))

        # Start rendering
        self.__crack_renderer(crack_marker, 'crack')
