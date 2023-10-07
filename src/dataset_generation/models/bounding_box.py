from __future__ import annotations
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

    def combine(self, bounding_box: BoundingBox) -> BoundingBox:
        """
        Combine two bounding boxes into one (possibly bigger) bounding box
        """
        new_min = np.array([
            min(self.min_vertex[0], bounding_box.min_vertex[0]),
            min(self.min_vertex[1], bounding_box.min_vertex[1]),
            min(self.min_vertex[2], bounding_box.min_vertex[2]),
        ])
        new_max = np.array([
            min(self.max_vertex[0], bounding_box.max_vertex[0]),
            min(self.max_vertex[1], bounding_box.max_vertex[1]),
            min(self.max_vertex[2], bounding_box.max_vertex[2]),
        ])
        dimensions = new_max - new_min

        return BoundingBox(
            new_min,
            new_max,
            dimensions[0],
            dimensions[2],
            dimensions[1]
        )
