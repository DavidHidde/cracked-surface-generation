import numpy as np

from .collision_checker import CollisionChecker
from dataset_generation.models import SurfaceMap


class PointDecollider:
    """
    Class with an unnecessary complicated sounding name to move points to the mortar.
    """

    def __call__(self, position: np.array, surface_map: SurfaceMap):
        """
        Move the position to a position within mortar using gradient ascend.
        """
        collision_checker = CollisionChecker(surface_map)

        while collision_checker.within_bounds(position) and collision_checker.in_object(position):
            angle = surface_map.inverse_gradient_angles[position[1], position[0]]
            position += np.rint(2 * np.array([np.cos(angle), np.sin(angle)])).astype(int)

        return position
