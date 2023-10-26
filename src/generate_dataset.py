import pickle

import bpy
import time

from dataset_generation.crack_generator import CrackGenerator
from dataset_generation.models import SurfaceParameters
from dataset_generation.operations import SceneClearer, MaterialLoader, SceneParameterGenerator, \
    CrackParametersGenerator
from dataset_generation.scene_generator import SceneGenerator
from dataset_generation.surface_map_generator import SurfaceMapGenerator

DUMP_SURFACE = False


def main(dataset_size: int = 1):
    """
    Main entrypoint
    """

    print('-- Starting rendering pipeline... --')
    start_time = time.time()

    # Setup of constants
    scene_clearer = SceneClearer()
    materials = (MaterialLoader())()
    surface_generator = SurfaceMapGenerator()
    crack_generator = CrackGenerator()
    scene_generator = SceneGenerator()
    crack_parameters_generator = CrackParametersGenerator()
    scene_parameters_generator = SceneParameterGenerator()

    wall = bpy.data.objects['Wall']
    wall = wall.evaluated_get(bpy.context.evaluated_depsgraph_get())
    wall_surface = surface_generator([wall])

    surface_parameters = SurfaceParameters(
        wall.modifiers['GeometryNodes']['Input_15'],
        wall.modifiers['GeometryNodes']['Input_16'],
        wall.modifiers['GeometryNodes']['Input_6'],
        wall.modifiers['GeometryNodes']['Input_7'],
        wall_surface
    )

    if DUMP_SURFACE:
        with open('surface_parameters.dump', 'wb') as surface_file:
            pickle.dump(surface_parameters, surface_file)

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
        crack = crack_generator(crack_parameters_generator(surface_parameters), surface_parameters, file_name + '.obj')
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
