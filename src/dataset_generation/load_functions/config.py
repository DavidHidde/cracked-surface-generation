import yaml

from .asset_collection import load_asset_collection
from .parameters import load_crack_parameters, load_label_parameters, load_camera_parameters
from dataset_generation.model import Configuration


def load_config_from_yaml(yaml_file_path: str, output_directory: str) -> Configuration:
    """Load a configuration from a yaml file. We supply the output dir dynamically to allow for repeated yaml use."""
    with open(yaml_file_path, 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)

    return Configuration(
        asset_collection=load_asset_collection(data['assets']),
        crack_parameters=load_crack_parameters(data['crack_generation']),
        camera_parameters=load_camera_parameters(data['dataset_generation']['camera']),
        label_parameters=load_label_parameters(data['dataset_generation']['label'], output_directory),
    )
