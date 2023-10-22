import numpy as np
from skimage import draw

from dataset_generation.models import SurfaceMap


class CollisionChecker:
    """
    Class for checking collision within the wall map
    """

    __surface_map: SurfaceMap
    __overlap_map: np.array

    def __init__(self, surface_map: SurfaceMap):
        """
        Initialize and set the surface map
        """
        self.__surface_map = surface_map
        self.__overlap_map = np.zeros(surface_map.mask.shape, dtype=bool)

    def within_bounds(self, position: np.array) -> bool:
        """
        Check if a position iw within the borders of the surface
        """
        return 0 < position[0] < self.__surface_map.surface.shape[1] - 1 and \
            0 < position[1] < self.__surface_map.surface.shape[0] - 1

    def in_object(self, position: np.array) -> bool:
        """
        Check if the poisition is in an object outside of the mortar.
        """
        return self.__surface_map.mask[position[1], position[0]]

    def check_and_mark_overlap(self, top_point: np.array, bot_point: np.array, allowed_overlap: float) -> bool:
        """
        Check if the overlap in area is within an allowed tolerance and marks it on the map if it is.
        Returns true if within the tolerance, else false.
        """
        # Early return in case overlap is fully allowed
        if allowed_overlap == 1:
            return True
        
        rows, columns = draw.line(top_point[1], top_point[0], bot_point[1], bot_point[0])
        if np.mean(self.__overlap_map[rows, columns].astype(float)) <= allowed_overlap:
            self.__overlap_map[rows, columns] = True
            return True

        return False
