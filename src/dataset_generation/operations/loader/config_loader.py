import yaml

from crack_generation.models.crack.parameters import CrackGenerationParameters, CrackDimensionParameters, \
    CrackPathParameters, CrackTrajectoryParameters
from dataset_generation.models import Configuration
from .camera_parameters_loader import CameraParametersLoader
from .label_parameters_loader import LabelParametersLoader
from .asset_collection_loader import AssetCollectionLoader


class ConfigLoader:
    """
    Loader class for loading a config from a yaml file
    """

    __asset_collection_loader: AssetCollectionLoader = AssetCollectionLoader()
    __camera_parameters_loader: CameraParametersLoader = CameraParametersLoader()
    __label_parameters_loader: LabelParametersLoader = LabelParametersLoader()

    def __call__(self, yaml_file_path: str) -> Configuration:
        """
        Load a configuration given a file path.
        """

        with open(yaml_file_path, 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)

        crack_parameters = CrackGenerationParameters(
            CrackDimensionParameters(**data['crack_generation_parameters']['crack_dimension_parameters']),
            CrackPathParameters(**data['crack_generation_parameters']['crack_path_parameters']),
            CrackTrajectoryParameters(**data['crack_generation_parameters']['crack_trajectory_parameters'])
        )

        return Configuration(
            crack_parameters,
            self.__asset_collection_loader(data['scene_generation_parameters']['assets']),
            self.__camera_parameters_loader(data['scene_generation_parameters']['camera_parameters']),
            self.__label_parameters_loader(data['scene_generation_parameters']['label_generation'])
        )
