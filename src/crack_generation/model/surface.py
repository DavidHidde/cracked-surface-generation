import numpy as np
from dataclasses import dataclass


@dataclass
class Surface:
    """
    A surface, represented by its height map (+derived maps) and its 'physical' dimensions.
    """
    height_map: np.array  # Grayscale image detailing the relative height of the surface at each point.
    distance_transform: np.array  # Distance transform of the inverse height map
    gradient_angles: np.array  # Gradient angles of the above distance transform

    # Average 'physical' dimensions in pixels. Useful for navigating the height map.
    brick_width: int
    brick_height: int
    mortar_size: int
