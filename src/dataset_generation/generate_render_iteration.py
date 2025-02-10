import functools
import signal
import random

import numpy as np

from crack_generation import CrackGenerator
from crack_generation.model import Surface, Crack
from dataset_generation.model import Configuration
from dataset_generation.model import RenderIteration

TIMEOUT_TIME = 10


# Source: https://imzye.com/Python/python-func-timeout/
def timeout(seconds):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(f'Function {func.__name__} timed out')

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator


@timeout(TIMEOUT_TIME)
def generate_crack(crack_generator: CrackGenerator, surface: Surface, min_pixels: int) -> Crack:
    """Generate a crack for the surface given a minimum amount of active pixels."""
    crack = crack_generator(surface)
    while np.sum(crack.crack_height_map) < min_pixels:
        crack = crack_generator(surface)
    return crack


def generate_render_iteration(
    config: Configuration,
    crack_generator: CrackGenerator,
    iteration: int
) -> RenderIteration:
    """Generate a new random RenderIteration."""
    random_state = np.random.random_sample(6)

    camera_parameters = config.camera_parameters
    x_distance_diff = camera_parameters.translation_max[0] - camera_parameters.translation_min[0]
    y_distance_diff = camera_parameters.translation_max[1] - camera_parameters.translation_min[1]
    z_distance_diff = camera_parameters.translation_max[2] - camera_parameters.translation_min[2]

    x_angle_diff = camera_parameters.rotation_max[0] - camera_parameters.rotation_min[0]
    y_angle_diff = camera_parameters.rotation_max[1] - camera_parameters.rotation_min[1]
    z_angle_diff = camera_parameters.rotation_max[2] - camera_parameters.rotation_min[2]

    camera_translation = [
        camera_parameters.translation_min[0] + random_state[0] * x_distance_diff,
        camera_parameters.translation_min[1] + random_state[1] * y_distance_diff,
        camera_parameters.translation_min[2] + random_state[2] * z_distance_diff
    ]
    camera_rotation = [
        camera_parameters.rotation_min[0] + random_state[3] * x_angle_diff,
        camera_parameters.rotation_min[1] + random_state[4] * y_angle_diff,
        camera_parameters.rotation_min[2] + random_state[5] * z_angle_diff
    ]

    # Make sure the camera points towards the crack
    if camera_rotation[0] < 0 and camera_translation[2] < 0:
        camera_rotation[0] *= -1
    if camera_rotation[2] < 0 and camera_translation[0] < 0:
        camera_rotation[2] *= -1

    scene = random.choice(config.asset_collection.scenes)
    face, uv_map, surface = random.choice(scene.surfaces)

    return RenderIteration(
        index=iteration,
        scene=scene,
        surface=surface,
        face=face,
        uv_map=uv_map,
        world_texture=random.choice(config.asset_collection.world_textures),
        crack=generate_crack(crack_generator, surface, config.label_parameters.min_active_pixels),
        camera_translation=tuple(camera_translation),
        camera_rotation=tuple(camera_rotation)
    )
