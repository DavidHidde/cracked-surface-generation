import bpy

from dataset_generation.models.parameters import CameraParameters


class CameraParametersLoader:
    """
    Loader class for the camera parameters
    """

    def __call__(self, camera_parameters_data: dict) -> CameraParameters:
        rotation = camera_parameters_data['rotation']
        translation = camera_parameters_data['translation']
        return CameraParameters(
            bpy.data.objects[camera_parameters_data['object']],
            (rotation['x']['min'], rotation['y']['min'], rotation['z']['min']),
            (rotation['x']['max'], rotation['y']['max'], rotation['z']['max']),
            (translation['x']['min'], translation['y']['min'], translation['z']['min']),
            (translation['x']['max'], translation['y']['max'], translation['z']['max'])
        )
