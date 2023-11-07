import pickle

import bpy
import time

from dataset_generation.crack_generator import CrackGenerator
from dataset_generation.empty_label_error import EmptyLabelError
from dataset_generation.operations import SceneClearer, MaterialLoader, SceneParameterGenerator, \
    CrackParametersGenerator, WallSetLoader, PatchGenerator
from dataset_generation.scene_generator import SceneGenerator

DUMP_SURFACE = False
PATCHES_PER_DIMENSION = 5
MAX_RETRIES = 5


def main(dataset_size: int = 1):
    """
    Main entrypoint
    """

    print('-- Starting rendering pipeline... --')
    start_time = time.time()

    # Setup of constants
    scene_clearer = SceneClearer()
    patch_generator = PatchGenerator()
    crack_generator = CrackGenerator()
    scene_generator = SceneGenerator()
    crack_parameters_generator = CrackParametersGenerator()
    scene_parameters_generator = SceneParameterGenerator()

    scene_clearer()  # Clear scene before determining surfaces
    materials = (MaterialLoader())()
    wall_sets = (WallSetLoader())()

    if DUMP_SURFACE:
        with open('surface_parameters.dump', 'wb') as surface_file:
            pickle.dump(wall_sets[0].surface_parameters, surface_file)

    camera = bpy.data.objects['Camera']

    bpy.context.scene.render.resolution_x = max(PATCHES_PER_DIMENSION, 1) * 224
    bpy.context.scene.render.resolution_y = max(PATCHES_PER_DIMENSION, 1) * 224

    """
    Main generation loop:
        - Clear the scene.
        - Generate a new crack.
        - Generate new scene parameters.
        - Generate a new scene and render.
        - Divide into patches if needed.
    """
    idx = 0
    retry_count = 0
    while idx < dataset_size and retry_count < MAX_RETRIES + 1:
        try:
            file_name = f'crack-{idx}'
            scene_clearer()
            scene_parameters = scene_parameters_generator(file_name, materials, wall_sets)
            crack = crack_generator(
                crack_parameters_generator(scene_parameters.wall_set.surface_parameters),
                scene_parameters.wall_set.surface_parameters,
                file_name + '.obj'
            )
            scene_generator(camera, crack, scene_parameters)

            if PATCHES_PER_DIMENSION > 1:
                idx += patch_generator(file_name, PATCHES_PER_DIMENSION)
            else:
                idx += 1

            retry_count = 0
        except EmptyLabelError:
            print('- Warning: Label was empty, retrying...  -')
            retry_count += 1
        except Exception as e:
            print(f'- Error: {e} -')
            print('- Warning: Something went wrong, retrying... -')
            retry_count += 1

    if retry_count >= MAX_RETRIES:
        print('- Rendering aborted, out of retries -')

    print(f'-- Rendering done after {round((time.time() - start_time) / 60, 2)} minutes --')


# Main entrypoint
if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Something caused the script to crash')
        print(error)
