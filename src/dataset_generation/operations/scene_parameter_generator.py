import numpy as np

from dataset_generation.models import SceneParameters, MaterialsContainer

MIN_ANGLE = -np.pi / 16
MAX_ANGLE = np.pi / 16

MIN_XZ_DISTANCE = -0.2
MAX_XZ_DISTANCE = 0.2

MIN_Y_DISTANCE = -1.0
MAX_Y_DISTANCE = -0.5


class SceneParameterGenerator:
    """
    Generator class for (mostly randomized) scene parameters.
    """

    def __call__(
            self,
            output_file_name: str,
            materials: MaterialsContainer
    ) -> SceneParameters:
        """
        Generate a new set of parameters.
        """
        random_state = np.random.random_sample(6)
        angle_diff = MAX_ANGLE - MIN_ANGLE
        xz_distance_diff = MAX_XZ_DISTANCE - MIN_XZ_DISTANCE
        y_distance_diff = MAX_Y_DISTANCE - MIN_Y_DISTANCE

        camera_rotation = [
            MIN_ANGLE + random_state[0] * angle_diff,
            0.,
            MIN_ANGLE + random_state[2] * angle_diff
        ]
        camera_translation = [
            MIN_XZ_DISTANCE + random_state[3] * xz_distance_diff,
            MIN_Y_DISTANCE + random_state[4] * y_distance_diff,
            MIN_XZ_DISTANCE + random_state[5] * xz_distance_diff
        ]

        # Make sure the camera points towards the crack
        if camera_rotation[0] < 0 and camera_translation[0] < 0:
            camera_translation[0] *= -1
        if camera_rotation[1] < 0 and camera_translation[1] < 0:
            camera_translation[1] *= -1
        if camera_rotation[2] < 0 and camera_translation[2] < 0:
            camera_translation[2] *= -1

        return SceneParameters(
            np.random.choice(materials.brick_materials),
            np.random.choice(materials.mortar_materials),
            np.random.choice(materials.crack_materials),
            np.random.choice(materials.world_textures),
            tuple(camera_translation),
            tuple(camera_rotation),
            output_file_name
        )
