import numpy as np

from .collision_checker import CollisionChecker
from crack_generation.models.surface import Surface


class PointDecollider:
    """
    Class with an unnecessary complicated sounding name to move points to the mortar.
    """

    def __call__(self, position: np.array, surface: Surface):
        """
        Move the position to a position within mortar using gradient ascend.
        """
        collision_checker = CollisionChecker(surface)

        while collision_checker.within_bounds(position) and collision_checker.in_object(position):
            angle = surface.map.gradient_angles[position[1], position[0]]
            position += np.rint(2 * np.array([np.cos(angle), np.sin(angle)])).astype(int)

        return position
