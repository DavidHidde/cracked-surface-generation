from dataclasses import dataclass

import numpy as np

from .bounding_box import BoundingBox


@dataclass
class SurfaceMap:
    """
    Map of a surface, where the the pixel intensities are the height values in the y-dimension.
    """

    surface: np.array
    bounding_box: BoundingBox
    contrast_factor: float
    grid_factor: float
