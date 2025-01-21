import os

import bpy

from crack_generation.model.parameters import CrackGenerationParameters, CrackDimensionParameters, CrackPathParameters, \
    CrackTrajectoryParameters
from dataset_generation.model.parameters import CameraParameters, LabelParameters

IMAGES_OUTPUT_DIR = 'images'
LABELS_OUTPUT_DIR = 'labels'


def load_crack_parameters(crack_parameters_dict: dict) -> CrackGenerationParameters:
    """Load the crack parameters from a dict. These values can be directly injected."""
    return CrackGenerationParameters(
        dimension_parameters=CrackDimensionParameters(**crack_parameters_dict['dimensions']),
        path_parameters=CrackPathParameters(**crack_parameters_dict['path']),
        trajectory_parameters=CrackTrajectoryParameters(**crack_parameters_dict['trajectory'])
    )


def load_camera_parameters(camera_parameters_dict: dict) -> CameraParameters:
    """Load the camera parameters from a dict. These values can be directly injected."""
    rotation = camera_parameters_dict['rotation']
    translation = camera_parameters_dict['translation']

    return CameraParameters(
        bpy.data.objects[camera_parameters_dict['object']],
        (rotation['x']['min'], rotation['y']['min'], rotation['z']['min']),
        (rotation['x']['max'], rotation['y']['max'], rotation['z']['max']),
        (translation['x']['min'], translation['y']['min'], translation['z']['min']),
        (translation['x']['max'], translation['y']['max'], translation['z']['max'])
    )


def load_label_parameters(label_parameters_dict: dict, output_directory: str) -> LabelParameters:
    """Load the label parameters from a dict. These values can be directly injected alongside the output directory."""
    threshold_data = label_parameters_dict['thresholding']
    base_output_directory = output_directory if output_directory.startswith(os.sep) \
        else os.path.join(os.getcwd(), output_directory)

    return LabelParameters(
        label_parameters_dict['patches'],
        threshold_data['min_active_pixels'],
        threshold_data['image_threshold'],
        threshold_data['uv_threshold'],
        threshold_data['ao_threshold'],
        base_output_directory,
        os.path.join(base_output_directory, IMAGES_OUTPUT_DIR),
        os.path.join(base_output_directory, LABELS_OUTPUT_DIR)
    )
