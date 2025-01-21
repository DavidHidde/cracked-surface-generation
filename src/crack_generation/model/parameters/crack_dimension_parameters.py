from dataclasses import dataclass


@dataclass
class CrackDimensionParameters:
    """
    Parameters that determine the dimensions of a crack.
    """

    width: float
    depth: float

    sigma: float  # standard deviation of the normal distribution
    width_stds_offset: float  # number of standard deviations away from the mean the width points are placed at
