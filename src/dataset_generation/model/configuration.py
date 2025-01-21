from dataclasses import dataclass

from crack_generation.model.parameters import CrackGenerationParameters
from .asset_collection import AssetCollection
from .parameters.camera_parameters import CameraParameters
from .parameters.label_parameters import LabelParameters


@dataclass
class Configuration:
    """The complete configuration of the framework, consisting of the shufflable assets and parameters."""

    asset_collection: AssetCollection
    crack_parameters: CrackGenerationParameters
    camera_parameters: CameraParameters
    label_parameters: LabelParameters
