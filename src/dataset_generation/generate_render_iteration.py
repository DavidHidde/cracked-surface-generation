import numpy as np

from crack_generation import CrackGenerator
from dataset_generation.model import Configuration
from dataset_generation.model import RenderIteration


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

    scene = np.random.choice(config.asset_collection.scenes)

    crack = crack_generator(scene.surface)
    while np.sum(crack.crack_height_map) < config.label_parameters.min_active_pixels:
        crack = crack_generator(scene.surface)

    return RenderIteration(
        index=iteration,
        scene=scene,
        world_texture=np.random.choice(config.asset_collection.world_textures),
        crack=crack,
        camera_translation=tuple(camera_translation),
        camera_rotation=tuple(camera_rotation)
    )
