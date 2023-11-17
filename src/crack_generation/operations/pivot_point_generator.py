import numpy as np

from .point_decollider import PointDecollider
from crack_generation.models.crack.parameters import CrackTrajectoryParameters
from crack_generation.models.surface import Surface


class PivotPointGenerator:
    """
    Generator for pivot points of a crack.
    """

    __point_decollider: PointDecollider = PointDecollider()

    def __call__(
            self,
            position: np.array,
            direction: int,
            parameters: CrackTrajectoryParameters,
            surface: Surface
    ) -> np.array:
        """
        Determine the next pivot point as seen from the current position.
        """
        brick_projected_size = np.array([
            surface.dimensions.brick_width,
            surface.dimensions.brick_height
        ]) * surface.map.grid_factor
        unit_width = np.random.randint(1, parameters.max_pivot_brick_widths) * brick_projected_size[0]
        unit_height = np.random.randint(1, parameters.max_pivot_brick_heights) * brick_projected_size[1]

        distribution_parameters = [
            (0, 0, unit_width),  # Along bottom
            (0, unit_width, unit_width + unit_height),  # Along diagonal
            (unit_width, unit_width, unit_width + unit_height)  # Along side
        ]

        distribution_parameters_idx = np.random.choice(
            np.arange(3),
            p=[parameters.along_bottom_chance, parameters.along_diagonal_chance, parameters.along_side_chance]
        )

        displacement = np.random.triangular(*distribution_parameters[distribution_parameters_idx])
        displacement_vector = [min(displacement, unit_width), unit_height - max(displacement - unit_width, 0)]
        displacement_vector = np.rint(displacement_vector / brick_projected_size) * brick_projected_size
        new_position = position + np.array([direction, -1]) * displacement_vector.astype(int)

        return self.__point_decollider(new_position, surface)
