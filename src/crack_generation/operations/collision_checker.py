import numpy as np

from crack_generation.models.surface import Surface


class CollisionChecker:
    """
    Class for checking collisions with a surface
    """

    __surface_mask: np.array

    def __init__(self, surface: Surface):
        """
        Initialize and set the surface map
        """
        self.__surface_mask = surface.map.mask

    def within_bounds(self, position: np.array) -> bool:
        """
        Check if a position iw within the borders of the surface
        """
        return 0 < position[0] < self.__surface_mask.shape[1] - 1 and \
            0 < position[1] < self.__surface_mask.shape[0] - 1

    def in_object(self, position: np.array) -> bool:
        """
        Check if the poisition is in an object outside of the mortar.
        """
        return self.within_bounds(position) and self.__surface_mask[position[1], position[0]]
