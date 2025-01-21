import numpy as np

from crack_generation.model import Surface, Point
from crack_generation.model.parameters import CrackTrajectoryParameters
from crack_generation.path_functions import move_to_nearest_mortar

PIVOT_DIRECTION_LEFT = -1
PIVOT_DIRECTION_RIGHT = 1


def generate_pivot_point(
    previous_point: tuple[int, int],
    surface: Surface,
    parameters: CrackTrajectoryParameters,
    pivot_direction: int,
    force_inwards: bool
) -> tuple[int, int]:
    """Determine the next pivot point as seen from the current position."""

    brick_projected_size = np.array(
        [
            surface.brick_width,
            surface.brick_height
        ], dtype=np.int32
    )
    unit_size = np.array(
        [
            np.random.randint(1, parameters.max_pivot_brick_widths),
            np.random.randint(1, parameters.max_pivot_brick_heights)
        ], dtype=np.int32
    ) * brick_projected_size

    # Triangle distribution, describing the chance of where the next pivot point should end up.
    distribution_parameters = [
        (0, 0, unit_size[0]),  # Along bottom
        (0, unit_size[0], unit_size[0] + unit_size[1]),  # Along diagonal
        (unit_size[0], unit_size[0], unit_size[0] + unit_size[1])  # Along side
    ]

    probs = [parameters.along_bottom_chance, parameters.along_diagonal_chance, parameters.along_side_chance]
    if force_inwards:
        is_roof = previous_point[1] == 0  # Set along side or bottom to 0 depending on which side we're on
        probs[0 if is_roof else 1] += probs[2 if is_roof else 0]
        probs[2 if is_roof else 0] = 0

    distribution_parameters_idx = np.random.choice(np.arange(3), p=probs)

    displacement = np.rint(np.random.triangular(*distribution_parameters[distribution_parameters_idx]))
    displacement_vector = [min(displacement, unit_size[0]), unit_size[1] - max(displacement - unit_size[0], 0)]
    displacement_vector = np.rint(displacement_vector / brick_projected_size) * brick_projected_size
    new_position = np.array(previous_point) + np.array([pivot_direction, 1]) * displacement_vector.astype(int)

    return move_to_nearest_mortar(Point(0, 0, new_position), surface).center


def determine_start_point(
    surface: Surface,
    parameters: CrackTrajectoryParameters,
    pivot_direction: int,
    initial_width: float
) -> Point:
    """
    Determine the starting point on the grid. This should be somewhere along the top.
    Note: min and max values are half open interval.
    """
    height, width = surface.height_map.shape
    min_height, max_height = 0, int(np.rint(height * (1 - parameters.row_search_space_percent)))
    if pivot_direction == PIVOT_DIRECTION_LEFT:
        min_width, max_width = int(np.rint(width * (1 - parameters.column_search_space_percent))), width - 1
    if pivot_direction == PIVOT_DIRECTION_RIGHT:
        min_width, max_width = 0, int(np.rint(width * parameters.column_search_space_percent))

    # Pair all edge points and sort them based on height value.
    side_edge_points = zip(
        [min_width if pivot_direction == PIVOT_DIRECTION_RIGHT else max_width] * (max_height - min_height),
        range(min_height, max_height)
    )
    top_edge_points = zip(range(min_width, max_width), [min_height] * (max_width - min_width))
    all_points = list(side_edge_points) + list(top_edge_points)
    all_points.sort(key=lambda point: -surface.distance_transform[point[1], point[0]])

    # Choose one of the 25% lowest points
    center = all_points[np.random.randint(int(len(all_points) * 0.2))]
    angle = (0 if pivot_direction == PIVOT_DIRECTION_RIGHT else np.pi) if center[1] > 0 else np.pi / 2.

    return Point(angle, min(initial_width, surface.distance_transform[center[1], center[0]]), center)
