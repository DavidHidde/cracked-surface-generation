import pickle
import traceback

import bpy
import time

from dataset_generation.empty_label_error import EmptyLabelError
from dataset_generation.operations import SceneClearer
from dataset_generation.operations.generators import SceneParameterGenerator, CrackModelGenerator, PatchGenerator
from dataset_generation.operations.loader import ConfigLoader
from dataset_generation.scene_generator import SceneGenerator

DUMP_SURFACE = False
MAX_RETRIES = 5


def main(dataset_size: int = 1, config_file_path: str = 'configuration.yaml'):
    """
    Main entrypoint
    """

    print('-- Starting rendering pipeline... --')
    start_time = time.time()

    # Setup of constants
    scene_clearer = SceneClearer()
    patch_generator = PatchGenerator()
    crack_generator = CrackModelGenerator()
    scene_generator = SceneGenerator()
    scene_parameters_generator = SceneParameterGenerator()
    config_loader = ConfigLoader()

    config = config_loader(config_file_path)

    if DUMP_SURFACE:
        with open('surface.dump', 'wb') as surface_file:
            pickle.dump(config.asset_collection.scenes[1].surface, surface_file)

    bpy.context.scene.render.resolution_x = max(config.label_parameters.num_patches, 1) * 224
    bpy.context.scene.render.resolution_y = max(config.label_parameters.num_patches, 1) * 224

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
            scene_clearer(config)
            scene_parameters = scene_parameters_generator(file_name, config)
            crack = crack_generator(
                config.crack_parameters,
                scene_parameters.wall_set.surface,
                file_name + '.obj'
            )
            scene_generator(crack, config, scene_parameters)

            if config.label_parameters.num_patches > 1:
                idx += patch_generator(file_name, config.label_parameters)
            else:
                idx += 1

            retry_count = 0
        except EmptyLabelError:
            print('- Warning: Label was empty, retrying...  -')
            retry_count += 1
        except Exception as e:
            print(f'- Error: {e} -')
            print(traceback.format_exc())
            print('- Warning: Something went wrong, retrying... -')
            retry_count += 1

    if retry_count >= MAX_RETRIES + 1:
        print('- Rendering aborted, out of retries -')

    print(f'-- Rendering done after {round((time.time() - start_time) / 60, 2)} minutes --')


# Main entrypoint
if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Something caused the script to crash')
        print(error)
