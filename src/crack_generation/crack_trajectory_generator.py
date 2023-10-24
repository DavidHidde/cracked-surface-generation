import numpy as np

from crack_generation.models import CrackParameters
from crack_generation.operations import CollisionChecker, PointDecollider, PivotPointGenerator
from dataset_generation.models import SurfaceParameters, SurfaceMap

DIRECTION_LEFT_TO_RIGHT = 1
DIRECTION_RIGHT_TO_LEFT = -1

MAX_PIVOT_POINTS = 6

ROW_SEARCH_SPACE_PERCENTILE = 0.2
COLUMN_SEARCH_SPACE_PERCENTILE = 0.2


def determine_width(
        angle: float,
        surface_parameters: SurfaceParameters,
        crack_parameters: CrackParameters
) -> float:
    """
    Determine the width at a position based on the requested width and the 
    """
    max_width = surface_parameters.mortar_height * surface_parameters.surface_map.grid_factor
    # Change to mortar width is the crack starts horizontal
    if 0.25 * np.pi < angle < 0.75 * np.pi or -0.75 * np.pi < angle < -0.25 * np.pi:
        max_width = surface_parameters.mortar_width * surface_parameters.surface_map.grid_factor

    return min(max_width, crack_parameters.width) - 1


def determine_start_point(
        surface_map: SurfaceMap,
        collision_checker: CollisionChecker,
        decollider: PointDecollider,
        direction: int
) -> np.array:
    """
    Determine the starting point on the grid. This should be somewhere along the top.
    """
    num_rows, num_columns = surface_map.surface.shape
    position = np.array([-1, -1], int)

    # Start on either the left or right side depending on the direction
    columns_start = 0 if direction == DIRECTION_LEFT_TO_RIGHT else (1 - COLUMN_SEARCH_SPACE_PERCENTILE) * num_columns
    columns_end = COLUMN_SEARCH_SPACE_PERCENTILE * num_rows if direction == DIRECTION_LEFT_TO_RIGHT else num_columns

    # Keep randoming until we find a value where we can actually start
    while not collision_checker.within_bounds(position) or collision_checker.in_object(position):
        position = np.random.randint(
            [columns_start, 0],
            [columns_end, num_rows * ROW_SEARCH_SPACE_PERCENTILE],
            size=(2,)
        )
        position = decollider(position, surface_map)

    return position


class CrackTrajectoryGenerator:
    """
    Class aimed at choosing the points of the trajectory of the crack as well as the initial width and angle.
    """

    __decollider: PointDecollider = PointDecollider()
    __pivot_point_generator = PivotPointGenerator()

    def __call__(
            self,
            crack_parameters: CrackParameters,
            surface_parameters: SurfaceParameters
    ) -> tuple[np.array, float, float]:
        """
        Choose an initial position, determine the pivot points and determine the width and angle.
        """
        direction = DIRECTION_LEFT_TO_RIGHT if np.random.rand() < 0.5 else DIRECTION_RIGHT_TO_LEFT
        collision_checker = CollisionChecker(surface_parameters.surface_map)
        start_position = determine_start_point(
            surface_parameters.surface_map,
            collision_checker,
            self.__decollider,
            direction
        )
        num_pivot_points = np.random.randint(1, MAX_PIVOT_POINTS)

        idx = 0
        pivot_points = np.empty((num_pivot_points + 1, 2), int)
        pivot_points[0, :] = start_position
        while idx < num_pivot_points:
            new_pivot_point = self.__pivot_point_generator(
                pivot_points[idx, :],
                surface_parameters.brick_width,
                surface_parameters.brick_height,
                direction,
                surface_parameters.surface_map
            )

            if not collision_checker.within_bounds(new_pivot_point):
                break

            idx += 1
            pivot_points[idx, :] = new_pivot_point

        # Determine angle and width at the start position
        grad_angle = surface_parameters.surface_map.gradient_angles[pivot_points[0, 1], pivot_points[0, 0]]
        path_angle = np.arctan2(pivot_points[1, 1] - pivot_points[0, 1], pivot_points[1, 0] - pivot_points[0, 0])
        angle = (grad_angle + path_angle) / 2.

        width = determine_width(angle, surface_parameters, crack_parameters)

        # Adjust for the width not fitting in the current position
        if width > surface_parameters.surface_map.distance_transform[start_position[1], start_position[0]]:
            start_position += np.rint(width * np.array([np.cos(angle), np.sin(angle)])).astype(int)

        return pivot_points[:idx + 1, :], width, angle
