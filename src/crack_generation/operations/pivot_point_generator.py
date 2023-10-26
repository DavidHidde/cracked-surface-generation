import numpy as np

from .point_decollider import PointDecollider
from dataset_generation.models import SurfaceMap

ALONG_BOTTOM_CHANCE = 2 / 12
ALONG_DIAGONAL_CHANCE = 9 / 12
ALONG_SIDE_CHANCE = 1 / 12

MAX_PIVOT_BRICK_WIDTHS = 5
MAX_PIVOT_BRICK_HEIGTHS = 7


class PivotPointGenerator:
    """
    Generator for pivot points of a crack.
    """

    __point_decollider: PointDecollider = PointDecollider()

    def __call__(
            self,
            position: np.array,
            brick_width: float,
            brick_height: float,
            direction: int,
            surface_map: SurfaceMap
    ) -> np.array:
        """
        Determine the next pivot point as seen from the current position.
        """
        brick_projected_size = np.array([brick_width, brick_height]) * surface_map.grid_factor
        unit_width = np.random.randint(1, MAX_PIVOT_BRICK_WIDTHS) * brick_projected_size[0]
        unit_height = np.random.randint(1, MAX_PIVOT_BRICK_HEIGTHS) * brick_projected_size[1]

        parameters = [
            (0, 0, unit_width),  # Along bottom
            (0, unit_width, unit_width + unit_height),  # Along diagonal
            (unit_width, unit_width, unit_width + unit_height)  # Along side
        ]

        parameters_idx = np.random.choice(
            np.arange(3),
            p=[ALONG_BOTTOM_CHANCE, ALONG_DIAGONAL_CHANCE, ALONG_SIDE_CHANCE]
        )

        displacement = np.random.triangular(*parameters[parameters_idx])
        displacement_vector = [min(displacement, unit_width), unit_height - max(displacement - unit_width, 0)]
        displacement_vector = np.rint(displacement_vector / brick_projected_size) * brick_projected_size
        new_position = position + np.array([direction, -1]) * displacement_vector.astype(int)

        return self.__point_decollider(new_position, surface_map)
