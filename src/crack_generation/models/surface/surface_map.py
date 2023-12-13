from dataclasses import dataclass

import numpy as np

from .bounding_box import BoundingBox


@dataclass
class SurfaceMap:
    """
    Map of a surface, consisting of its surface mask, the distance transforms
    based on it and the bounding box and factor used to generate the mask.
    """

    mask: np.array  # Boolean array marking objects in the surface as False

    distance_transform: np.array    # Distance transform of the inverse mask
    gradient_angles: np.array   # Gradient angles of the above distance transform

    grid_factor: float
    bounding_box: BoundingBox
