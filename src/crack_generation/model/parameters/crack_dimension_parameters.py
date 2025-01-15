from dataclasses import dataclass


@dataclass
class CrackDimensionParameters:
    """
    Parameters that determine the dimensions of a crack.
    """

    width: float
    depth: float

    depth_resolution: int  # number of points to sample in the depth
    sigma: float  # standard deviation of the normal distribution
    width_stds_offset: float  # umber of standar deviations away from the mean the width points are placed at
