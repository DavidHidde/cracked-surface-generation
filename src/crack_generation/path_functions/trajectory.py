import numpy as np

from crack_generation.model import Surface, Point
from crack_generation.model.parameters import CrackGenerationParameters
from .collision import within_surface
from .pivot_point import PIVOT_DIRECTION_LEFT, PIVOT_DIRECTION_RIGHT, determine_start_point, generate_pivot_point


def generate_pivot_trajectory(surface: Surface, parameters: CrackGenerationParameters) -> tuple[Point, list[tuple[int, int]]]:
    """Generate a list of pivot points and a starting point, detailing the crack trajectory."""
    pivot_direction = np.random.choice([PIVOT_DIRECTION_LEFT, PIVOT_DIRECTION_RIGHT])
    start_point = determine_start_point(
        surface,
        parameters.trajectory_parameters,
        pivot_direction,
        parameters.dimension_parameters.width
    )
    num_pivot_points = np.random.randint(1, parameters.trajectory_parameters.max_pivot_points)

    pivot_points = [start_point.center]
    for idx in range(1, num_pivot_points + 1):
        next_pivot_point = generate_pivot_point(
            pivot_points[idx - 1],
            surface,
            parameters.trajectory_parameters,
            pivot_direction
        )
        pivot_points.append(next_pivot_point)

        # Stop when a point falls outside the surface
        if not within_surface(Point(0, 0, next_pivot_point), surface):
            break

    return start_point, pivot_points[1:]
