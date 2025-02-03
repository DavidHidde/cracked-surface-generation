import os
import traceback
from pathlib import Path

import bpy
import time

from crack_generation import CrackGenerator
from dataset_generation import generate_render_iteration, prepare_scene, render_crack
from dataset_generation.load_functions import load_config_from_yaml
from dataset_generation.node_injection_functions import create_compositor_flow


def run(dataset_size: int, max_retries: int, config_file_path: str, output_dir: str):
    """
    Main entrypoint. Starts the dataset generation using a specific config, dataset size and maximum number of retries.
    """

    start_time = time.time()

    print('-- Preloading Blender data... --')
    # Load config and create output directories
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
        - Generate a new render iteration
        - Generate a new crack on the surface of the iteration.
        - Apply iteration settings.
        - Render and divide into patches if needed.
    """
    print('-- Starting rendering pipeline... --')
    idx = 0
    retry_count = 0
    crack_generator = CrackGenerator(config.crack_parameters)
    while idx < dataset_size and retry_count <= max_retries:
        try:
            render_iteration = generate_render_iteration(config, crack_generator, idx)
            prepare_scene(config, render_iteration)

            num_rendered = render_crack(config.label_parameters, render_iteration.index)
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
