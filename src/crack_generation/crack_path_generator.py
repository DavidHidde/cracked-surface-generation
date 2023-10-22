import numpy as np

from crack_generation.models import CrackParameters, CrackPath
from crack_generation.operations import get_rotation_matrix, increment_by_chance, CrackPointChooser, CollisionChecker
from dataset_generation.models import SurfaceParameters, SurfaceMap

MIN_DISTANCE = 5

MIN_WIDTH = 1.
MAX_WIDTH_GROW_FACTOR = 0.05
MAX_WIDTH_GROW = 0.2


def determine_width_points(
        center: np.array,
        width: float,
        angle: float
) -> tuple[np.array, np.array]:
    """
    Calculate the top and bot points using the center, width and angle.
    """
    rotation_matrix = get_rotation_matrix(angle)
    offset = np.dot(rotation_matrix, np.array([0., width])) / 2.
    top_point = np.rint(center + offset).astype(int)
    bot_point = np.rint(center - offset).astype(int)

    return top_point, bot_point


def generate_path(
        initial_position: np.array,
        end_position: np.array,
        surface_map: SurfaceMap,
        angle: float,
        width: float,
        parameters: CrackParameters
) -> tuple[np.array, np.array]:
    """
    Generate a path and the corresponding top and bottom line from a set of crack parameters.
    """
    center = initial_position.copy().astype(float)
    center_int = initial_position.copy()
    top_point, bot_point = determine_width_points(center, width, angle)
    top_line, bot_line = np.array([top_point], int), np.array([bot_point], int)

    collision_checker = CollisionChecker(surface_map)
    breaking_gradient = collision_checker.in_object(center_int)

    # Keep going until the crack becomes to small, reaches the boundary or reaches the end point
    while width >= MIN_WIDTH and \
            collision_checker.within_bounds(center) and \
            np.linalg.norm(end_position - center) > MIN_DISTANCE:
        gradient_angle = surface_map.gradient_angles[center_int[1], center_int[0]]
        gradient_vector = np.array([np.cos(gradient_angle), np.sin(gradient_angle)])

        end_point_angle = np.arctan2(end_position[1] - center[1], end_position[0] - center[0])
        end_point_vector = np.array([np.cos(end_point_angle), np.sin(end_point_angle)])

        # Blend the gradient and direction factor. We have a small chance to ignore the gradient.
        if not breaking_gradient and np.random.random_sample() < parameters.breakthrough_chance:
            breaking_gradient = True
        factor = parameters.gradient_influence if not breaking_gradient else 0.

        direction_vector = factor * gradient_vector + (1 - factor) * end_point_vector
        direction_vector /= np.linalg.norm(direction_vector)

        # Update parameters for the current step
        center += parameters.step_size * direction_vector
        center_int = np.rint(center).astype(int)
        angle = np.arctan2(direction_vector[1], direction_vector[0])
        top_point, bot_point = determine_width_points(center, width, angle)
        top_line, bot_line = np.append(top_line, [top_point], axis=0), np.append(bot_line, [bot_point], axis=0)
        breaking_gradient = collision_checker.in_object(center_int)

        width_increment = MAX_WIDTH_GROW if width / 2 < surface_map.distance_transform[center_int[1], center_int[0]] \
            else -MAX_WIDTH_GROW
        width = increment_by_chance(width, width_increment, parameters.width_update_chance)

    return top_line, bot_line


class CrackPathGenerator:
    """
    Generator class for creating 2D cracks based on CrackParameters.
    """

    __point_chooser: CrackPointChooser = CrackPointChooser()

    def __call__(self, crack_parameters: CrackParameters, surface_parameters: SurfaceParameters) -> CrackPath:
        """
        Create a top and bottom line of the crack based on the surface.
        """
        # Initial positions
        start_position, end_position, width, angle = self.__point_chooser(crack_parameters, surface_parameters)

        # Launch path generation
        top_line, bot_line = generate_path(
            start_position,
            end_position,
            surface_parameters.surface_map,
            angle,
            width,
            crack_parameters
        )

        # Reduce step widths based on start and end pointiness
        width_grow_increments = max(MAX_WIDTH_GROW, MAX_WIDTH_GROW_FACTOR * width)
        idx = 0
        start_steps = crack_parameters.start_pointiness
        while idx < start_steps:
            vector_diff = top_line[idx, :] - bot_line[idx, :]
            center = (top_line[idx, :] + bot_line[idx, :]) / 2
            width = max(np.linalg.norm(vector_diff) - (start_steps - idx) * width_grow_increments, MIN_WIDTH)
            angle = np.arctan2(vector_diff[1], vector_diff[0])
            top_line[idx, :], bot_line[idx, :] = determine_width_points(center, width, angle)
            idx += 1

        total_steps = top_line.shape[0]
        idx = total_steps - crack_parameters.end_pointiness
        while idx < total_steps:
            vector_diff = top_line[idx, :] - bot_line[idx, :]
            center = (top_line[idx, :] + bot_line[idx, :]) / 2
            width = max(np.linalg.norm(vector_diff) - idx * width_grow_increments, MIN_WIDTH)
            angle = np.arctan2(vector_diff[1], vector_diff[0])
            top_line[idx, :], bot_line[idx, :] = determine_width_points(center, width, angle)
            idx += 1

        return CrackPath(top_line, bot_line)
