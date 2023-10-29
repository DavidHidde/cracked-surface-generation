import numpy as np

from dataset_generation.models import SurfaceMap


class CollisionChecker:
    """
    Class for checking collision within the wall map
    """

    __surface_map: SurfaceMap

    def __init__(self, surface_map: SurfaceMap):
        """
        Initialize and set the surface map
        """
        self.__surface_map = surface_map

    def within_bounds(self, position: np.array) -> bool:
        """
        Check if a position iw within the borders of the surface
        """
        return 0 < position[0] < self.__surface_map.mask.shape[1] - 1 and \
            0 < position[1] < self.__surface_map.mask.shape[0] - 1

    def in_object(self, position: np.array) -> bool:
        """
        Check if the poisition is in an object outside of the mortar.
        """
        return self.within_bounds(position) and self.__surface_map.mask[position[1], position[0]]
