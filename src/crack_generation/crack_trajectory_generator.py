import numpy as np

from crack_generation.models.crack.parameters import CrackGenerationParameters, CrackTrajectoryParameters
from crack_generation.models.surface import Surface
from crack_generation.operations import CollisionChecker, PointDecollider, PivotPointGenerator

DIRECTION_LEFT_TO_RIGHT = 1
DIRECTION_RIGHT_TO_LEFT = -1


def determine_start_point(
        surface: Surface,
        parameters: CrackTrajectoryParameters,
        collision_checker: CollisionChecker,
        decollider: PointDecollider,
        direction: int
) -> np.array:
    """
    Determine the starting point on the grid. This should be somewhere along the top.
    """
    num_rows, num_columns = surface.map.mask.shape
    position = np.array([-1, -1], int)

    # Start on either the left or right side depending on the direction
    rows_start, rows_end = num_rows * (1 - parameters.row_search_space_percent), num_rows - 1
    if direction == DIRECTION_LEFT_TO_RIGHT:
        columns_start, columns_end = 0, parameters.column_search_space_percent * num_columns
    else:
        columns_start, columns_end = (1 - parameters.column_search_space_percent) * num_columns, num_columns - 1

    # Keep randoming until we find a value where we can actually start
    while not collision_checker.within_bounds(position) or collision_checker.in_object(position):
        position = np.random.randint([columns_start, rows_start], [columns_end, rows_end], size=(2,))
        position = decollider(position, surface)

    return position


class CrackTrajectoryGenerator:
    """
    Class aimed at choosing the points of the trajectory of the crack as well as the initial width and angle.
    """

    __decollider: PointDecollider = PointDecollider()
    __pivot_point_generator = PivotPointGenerator()

    def __call__(
            self,
            crack_parameters: CrackGenerationParameters,
            surface: Surface
    ) -> tuple[np.array, float, float]:
        """
        Choose an initial position, determine the pivot points and determine the width and angle.
        """
        direction = DIRECTION_LEFT_TO_RIGHT if np.random.rand() < 0.5 else DIRECTION_RIGHT_TO_LEFT
        collision_checker = CollisionChecker(surface)
        start_position = determine_start_point(
            surface,
            crack_parameters.trajectory_parameters,
            collision_checker,
            self.__decollider,
            direction
        )
        num_pivot_points = np.random.randint(1, crack_parameters.trajectory_parameters.max_pivot_points)

        idx = 0
        pivot_points = np.empty((num_pivot_points + 1, 2), int)
        pivot_points[0, :] = start_position
        while idx < num_pivot_points:
            new_pivot_point = self.__pivot_point_generator(
                pivot_points[idx, :],
                direction,
                crack_parameters.trajectory_parameters,
                surface
            )

            if not collision_checker.within_bounds(new_pivot_point):
                break

            idx += 1
            pivot_points[idx, :] = new_pivot_point

        # Determine angle and width at the start position
        grad_angle = surface.map.gradient_angles[pivot_points[0, 1], pivot_points[0, 0]]
        path_angle = np.arctan2(pivot_points[1, 1] - pivot_points[0, 1], pivot_points[1, 0] - pivot_points[0, 0])
        angle = (grad_angle + path_angle) / 2.

        # Determine the width and adjust for the width not fitting in the current position
        width = min(
            surface.dimensions.mortar_size * surface.map.grid_factor,
            crack_parameters.dimension_parameters.width
        )
        if width > surface.map.distance_transform[start_position[1], start_position[0]]:
            start_position += np.rint(width * np.array([np.cos(angle), np.sin(angle)])).astype(int)

        return pivot_points[:idx + 1, :], width, angle
