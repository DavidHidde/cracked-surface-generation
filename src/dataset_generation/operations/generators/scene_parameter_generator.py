import numpy as np

from dataset_generation.models import Configuration
from dataset_generation.models.parameters.scene_parameters import SceneParameters


class SceneParameterGenerator:
    """
    Generator class for (mostly randomized) scene parameters.
    """

    def __call__(self, config: Configuration) -> SceneParameters:
        """
        Generate a new set of parameters.
        """
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

        return SceneParameters(
            np.random.choice(config.asset_collection.scenes),
            np.random.choice(config.asset_collection.wall_materials),
            np.random.choice(config.asset_collection.world_textures),
            tuple(camera_translation),
            tuple(camera_rotation),
        )
