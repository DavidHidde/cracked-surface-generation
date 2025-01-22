import os
import traceback
from pathlib import Path

import bpy
import time

from dataset_generation.load_functions import load_config_from_yaml
from dataset_generation.node_injection_functions.compositor import create_compositor_flow
from dataset_generation.operations import SceneClearer, CrackRenderer, CompositorInitializer
from dataset_generation.operations.generators import SceneParameterGenerator, CrackModelGenerator
from dataset_generation.scene_generator import SceneGenerator

def run(dataset_size: int, max_retries: int, config_file_path: str, output_dir: str):
    """
    Main entrypoint. Starts the dataset generation using a specific config, dataset size and maximum number of retries.
    """

    start_time = time.time()

    print('-- Preloading Blender data... --')
    # Setup of constant operators
    scene_clearer = SceneClearer()
    crack_renderer = CrackRenderer()
    crack_generator = CrackModelGenerator()
    scene_generator = SceneGenerator()
    scene_parameters_generator = SceneParameterGenerator()

    # Create output directories
    config = load_config_from_yaml(config_file_path, output_dir)
    Path(os.path.join(config.label_parameters.image_output_directory)).mkdir(exist_ok=True, parents=True)
    Path(os.path.join(config.label_parameters.label_output_directory)).mkdir(exist_ok=True, parents=True)

    # Set render settings
    resolution_width, resolution_height = config.label_parameters.resolution
    bpy.context.scene.render.resolution_x = max(config.label_parameters.num_patches, 1) * resolution_width
    bpy.context.scene.render.resolution_y = max(config.label_parameters.num_patches, 1) * resolution_height
    create_compositor_flow(config.label_parameters)

    """
    Main generation loop:
        - Clear the scene.
        - Generate a new crack.
        - Generate new scene parameters.
        - Generate a new scene.
        - Render and divide into patches if needed.
    """
    print('-- Starting rendering pipeline... --')
    idx = 0
    retry_count = 0
    crack_obj_path = os.path.join(config.label_parameters.base_output_directory, 'crack.obj')
    while idx < dataset_size and retry_count <= max_retries:
        try:
            file_name = f'crack-{idx}'

            scene_clearer(config)
            scene_parameters = scene_parameters_generator(config)
            crack = crack_generator(
                config.crack_parameters,
                scene_parameters.wall_set.surface,
                crack_obj_path
            )
            scene_generator(crack, config.camera_parameters.camera_obj, scene_parameters)

            num_rendered = crack_renderer(config.label_parameters, file_name)
            if num_rendered == 0:
                print('- Warning: Label was empty, retrying...  -')
                retry_count += 1
            else:
                idx += num_rendered
                retry_count = 0
        except Exception as e:
            print(f'- Error: {e} -')
            print(traceback.format_exc())
            print('- Warning: Something went wrong, retrying... -')
            retry_count += 1

    if retry_count > max_retries:
        print('- Rendering aborted, out of retries -')

    print(f'-- Rendering done after {round((time.time() - start_time) / 60, 2)} minutes --')
