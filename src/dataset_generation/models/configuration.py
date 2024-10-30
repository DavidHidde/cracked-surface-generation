from dataclasses import dataclass

from crack_generation.models.crack.parameters import CrackGenerationParameters
from .asset_collection import AssetCollection
from .parameters.camera_parameters import CameraParameters
from .parameters.label_generation_parameters import LabelGenerationParameters


@dataclass
class Configuration:
    """
    The complete configuration of the framework, including crack generation parameters
    and scene generation parameters.
    """

    crack_parameters: CrackGenerationParameters
    asset_collection: AssetCollection
    camera_parameters: CameraParameters
    label_parameters: LabelGenerationParameters

    output_directory: str
    output_images_directory: str
    output_labels_directory: str
