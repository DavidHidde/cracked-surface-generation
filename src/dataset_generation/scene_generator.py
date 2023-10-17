import bpy
from mathutils import Vector

from dataset_generation.operations import MaterialLoader

BRICK_MATERIALS = [
    'Brick - red',
    'Brick - gray'
]
MORTAR_MATERIALS = ['Mortar - white']
CRACK_MATERIAL = 'Crack marker'
HDRIS = []


class SceneGenerator:
    """
    Generator aimed at generating a scene using a crack, wall and a camera
    """

    def __call__(
            self,
            wall: bpy.types.Object,
            camera: bpy.types.Object,
            crack: bpy.types.Object,
            materials: dict[str, dict[str, bpy.types.Material]]
    ) -> None:
        wall = bpy.data.objects[wall.name]  # Get unevaluated object
        crack.hide_render = True

        # Create a copy of the crack to serve as a marker
        crack_marker = crack.copy()
        crack_marker.data = crack.data.copy()
        bpy.context.scene.collection.objects.link(crack_marker)
        crack_marker.data.materials.append(materials[MaterialLoader.KEYWORD_CRACK][MaterialLoader.CRACK_MATERIALS[0]])

        # Carve the crack out of the wall
        wall.modifiers['Boolean'].object = crack

        # Set the marker as the intersection of the wall and the crack
        intersection_mod = crack_marker.modifiers.new('crack_intersect', 'BOOLEAN')
        intersection_mod.operation = 'INTERSECT'
        intersection_mod.use_self = True
        intersection_mod.object = wall

        # Move camera to object
        crack_center = sum((Vector(vert) for vert in crack.bound_box), Vector()) / 8.
        camera.location = crack.matrix_world @ crack_center
        camera.location.y -= 1.

        # Start rendering
        bpy.context.scene.render.filepath = 'crack.png'
        bpy.ops.render.render(write_still=True)
        crack_marker.hide_render = False
        bpy.context.scene.render.filepath = 'crack-label.png'
        bpy.ops.render.render(write_still=True)
