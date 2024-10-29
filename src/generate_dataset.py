import os
import traceback
from pathlib import Path

import bpy
import time

from dataset_generation.empty_label_error import EmptyLabelError
from dataset_generation.operations import SceneClearer
from dataset_generation.operations.generators import SceneParameterGenerator, CrackModelGenerator, PatchGenerator
from dataset_generation.operations.loader import ConfigLoader
from dataset_generation.scene_generator import SceneGenerator

def run(dataset_size: int, max_retries: int, config_file_path: str, output_dir: str):
    """
    Main entrypoint. Starts the dataset generation using a specific config, dataset size and maximum number of retries.
    """

    start_time = time.time()

    print('-- Preloading Blender data... --')
    # Setup of constant operators
    scene_clearer = SceneClearer()
    patch_generator = PatchGenerator()
    crack_generator = CrackModelGenerator()
    scene_generator = SceneGenerator()
    scene_parameters_generator = SceneParameterGenerator()
    config_loader = ConfigLoader()

    # Create output directories
    config = config_loader(config_file_path, output_dir)
    Path(os.path.join(config.output_directory, 'images')).mkdir(exist_ok=True, parents=True)
    Path(os.path.join(config.output_directory, 'labels')).mkdir(exist_ok=True, parents=True)

    # Set render settings
    bpy.context.scene.render.resolution_x = max(config.label_parameters.num_patches, 1) * 224
    bpy.context.scene.render.resolution_y = max(config.label_parameters.num_patches, 1) * 224
    bpy.context.scene.render.image_settings.file_format = 'PNG'

    """
    Main generation loop:
        - Clear the scene.
        - Generate a new crack.
        - Generate new scene parameters.
        - Generate a new scene and render.
        - Divide into patches if needed.
    """
    print('-- Starting rendering pipeline... --')
    idx = 0
    retry_count = 0
    crack_obj_path = os.path.join(config.output_directory, 'crack.obj')
    while idx < dataset_size and retry_count <= max_retries:
        try:
            file_name = f'crack-{idx}'
            scene_clearer(config)
            scene_parameters = scene_parameters_generator(file_name, config)
            crack = crack_generator(
                config.crack_parameters,
                scene_parameters.wall_set.surface,
                crack_obj_path
            )
            scene_generator(crack, config, scene_parameters)

            if config.label_parameters.num_patches > 1:
                idx += patch_generator(file_name, config.output_images_directory, config.output_labels_directory, config.label_parameters)
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

    if retry_count > max_retries:
        print('- Rendering aborted, out of retries -')

    print(f'-- Rendering done after {round((time.time() - start_time) / 60, 2)} minutes --')
