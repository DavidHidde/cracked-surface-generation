from dataclasses import dataclass

import numpy as np

from .bounding_box import BoundingBox


@dataclass
class SurfaceMap:
    """
    Map of a surface, where the the pixel intensities are the height values in the y-dimension.
    """

    mask: np.array  # Boolean array marking objects in the surface as False

    distance_transform: np.array    # Distance transform of the mask
    gradient_angles: np.array   # Gradient angles of the distance transform

    inverse_distance_transform: np.array    # Distance transform of the inverse mask
    inverse_gradient_angles: np.array   # Gradient angles of the inverse distance transform

    bounding_box: BoundingBox
    grid_factor: float
