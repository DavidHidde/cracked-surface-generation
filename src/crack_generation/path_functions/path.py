import numpy as np

from crack_generation.model import Point, Surface
from crack_generation.model.parameters import CrackPathParameters
from .collision import within_surface, on_edge


def generate_path(
    initial_point: Point,
    end_position: tuple[int, int],
    surface: Surface,
    parameters: CrackPathParameters
) -> list[Point]:
    """
    Generate a path given a starting point and end position based on a surface and parameters.
    The final path does not include the initial point.
    """

    path_points = []
    current_point = initial_point
    end_x, end_y = end_position
    surface_width, surface_height = surface.height_map.shape

    # Keep going until the crack becomes to small, reaches the boundary or reaches the end point
    while current_point.width >= parameters.min_width and \
            within_surface(current_point, surface) and \
            np.linalg.norm(np.array(end_position) - np.array(current_point.center)) > parameters.min_distance:

        current_x, current_y = current_point.center
        gradient_angle = surface.gradient_angles[current_y, current_x]
        gradient_vector = np.array([np.cos(gradient_angle), np.sin(gradient_angle)])

        end_point_angle = np.arctan2(end_y - current_y, end_x - current_x)
        end_point_vector = np.array([np.cos(end_point_angle), np.sin(end_point_angle)])

        # Blend the gradient and direction factor. We have a small chance to ignore the gradient.
        factor = parameters.gradient_influence if not np.random.random_sample() < parameters.breakthrough_chance else 0.

        direction_vector = factor * gradient_vector + (1 - factor) * end_point_vector
        direction_vector /= np.linalg.norm(direction_vector)

        # Calculate the new point and next values
        center = (np.array(current_point.center, dtype=np.int32) + parameters.step_size * direction_vector).astype(np.int32)
        angle = np.arctan2(direction_vector[1], direction_vector[0])
        width_increment = current_point.width * np.random.uniform(-1., 1) * parameters.max_width_grow_factor
        width = current_point.width + width_increment if np.random.rand() < parameters.width_update_chance else current_point.width
        new_point = Point(
            angle,
            width,
            (np.clip(center[0], 0, surface_width - 1, dtype=np.int32), np.clip(center[1], 0, surface_height - 1, dtype=np.int32))
        )

        path_points.append(new_point)
        current_point = new_point

        # If the new point is on the edge of the surface, abort
        if on_edge(new_point, surface):
            break

    return path_points
