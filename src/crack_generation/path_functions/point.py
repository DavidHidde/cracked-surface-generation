import numpy as np
from crack_generation.model import Point


def point_to_coords(point: Point) -> tuple[tuple[int, int], tuple[int, int]]:
    """Transform a point to its top and bottom coordinates."""
    offset = point.width / 2. * np.array([-np.sin(point.angle), np.cos(point.angle)])
    center = np.array(point.center)
    return tuple(np.rint(center + offset).astype(np.int32)), tuple(np.rint(center - offset).astype(np.int32))
