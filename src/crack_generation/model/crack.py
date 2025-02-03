import numpy as np

from dataclasses import dataclass
from .point import Point


@dataclass
class Crack:
    """
    A generated crack, consisting of its 2D path and its path applied to the surface.
    """

    path: list[Point]
    trajectory: list[tuple[int, int]]
    crack_height_map: np.array

