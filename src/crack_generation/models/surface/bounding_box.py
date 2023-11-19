from dataclasses import dataclass

import numpy as np


@dataclass
class BoundingBox:
    """
    Data class describing a bounding box. Uses a rectangular bounding box.
    Also note the definitions of width, depth and height.
    """

    min_vertex: np.array
    max_vertex: np.array

    width: float  # Length along x
    height: float  # Length along z
    depth: float  # Length along y
