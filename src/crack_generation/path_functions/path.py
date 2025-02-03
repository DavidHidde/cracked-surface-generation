import numpy as np

from crack_generation.model import Point, Surface
from crack_generation.model.parameters import CrackPathParameters
from .collision import within_surface, in_object


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
    surface_height, surface_width = surface.height_map.shape
    breaking_gradient = True  # Start at true to help progression

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
        if not breaking_gradient and np.random.random_sample() < parameters.breakthrough_chance:
            breaking_gradient = True
        factor = parameters.gradient_influence if not breaking_gradient else 0.

        direction_vector = factor * gradient_vector + (1 - factor) * end_point_vector
        direction_vector /= np.linalg.norm(direction_vector)

        # Calculate the new point and next values. If we go outside the surface, clip to the edge and then stop
        center = (np.array(current_point.center, dtype=np.int32) + parameters.step_size * direction_vector).astype(np.int32)
        if 0 > center[0] or center[0] >= surface_width or 0 > center[1] or center[1] >= surface_height:
            center = (
                np.clip(center[0], 0, surface_width - 1, dtype=np.int32),
                np.clip(center[1], 0, surface_height - 1, dtype=np.int32)
            )
            end_position = center

        angle = np.arctan2(direction_vector[1], direction_vector[0])
        width_increment = np.random.uniform(-1., 1) * parameters.max_width_grow if current_point.width < surface.distance_transform[center[1], center[0]] or breaking_gradient else -np.random.rand()
        width = current_point.width + width_increment if np.random.rand() < parameters.width_update_chance else current_point.width
        breaking_gradient = in_object(current_point, surface)

        new_point = Point(angle, width, center)
        current_point = new_point
        path_points.append(new_point)

    return path_points
