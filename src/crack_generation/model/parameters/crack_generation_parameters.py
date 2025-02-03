from dataclasses import dataclass

from .crack_dimension_parameters import CrackDimensionParameters
from .crack_path_parameters import CrackPathParameters
from .crack_trajectory_parameters import CrackTrajectoryParameters


@dataclass
class CrackGenerationParameters:
    """
    Parameters that are used to generate a crack.
    These parameters basically describe how the entire algorithm should function.
    """

    dimension_parameters: CrackDimensionParameters
    path_parameters: CrackPathParameters
    trajectory_parameters: CrackTrajectoryParameters
