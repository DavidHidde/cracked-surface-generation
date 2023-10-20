import bpy
import time

from crack_generation.models import CrackParameters
from dataset_generation.crack_generator import CrackGenerator
from dataset_generation.operations import SceneClearer, MaterialLoader, SceneParameterGenerator
from dataset_generation.scene_generator import SceneGenerator
from dataset_generation.surface_map_generator import SurfaceMapGenerator


def main(dataset_size: int = 1):
    """
    Main entrypoint
    """

    print('-- Starting rendering pipeline... --')
    start_time = time.time()

    # Setup of constants
    crack_parameters = CrackParameters(
        20.,
        5.,
        300,
        0.1,
        0,
        5,
        5,
        1.,
        0.2,
        0.1,
        0.1
    )
    scene_clearer = SceneClearer()
    materials = (MaterialLoader())()
    surface_generator = SurfaceMapGenerator()
    crack_generator = CrackGenerator()
    scene_generator = SceneGenerator()
    scene_parameters_generator = SceneParameterGenerator()

    wall = bpy.data.objects['Wall']
    wall = wall.evaluated_get(bpy.context.evaluated_depsgraph_get())
    wall_surface = surface_generator([wall])
    wall = bpy.data.objects['Wall']  # Return to unevaluated version
    camera = bpy.data.objects['Camera']

    """
    Main generation loop:
        - Clear the scene.
        - Generate a new crack.
        - Generate new scene parameters.
        - Generate a new scene and render.
    """
    for idx in range(dataset_size):
        file_name = f'crack-{idx}'
        scene_clearer()
        crack = crack_generator(crack_parameters, wall_surface, file_name + '.obj')
        scene_parameters = scene_parameters_generator(file_name, materials)
        scene_generator(wall, camera, crack, scene_parameters)

    print(f'-- Rendering done after {round((time.time() - start_time) / 60, 2)} minutes --')


# Main entrypoint
if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Something caused the script to crash')
        print(error)
