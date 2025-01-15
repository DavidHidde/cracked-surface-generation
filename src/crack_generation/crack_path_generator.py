import random

import numpy as np
from scipy.ndimage import gaussian_filter1d

from crack_generation.crack_trajectory_generator import CrackTrajectoryGenerator
from crack_generation.models.crack import CrackPath
from crack_generation.models.parameters import CrackPathParameters, CrackGenerationParameters
from crack_generation.models.surface import Surface
from crack_generation.operations import CollisionChecker


def increment_by_chance(variable: float, increment: float, chance: float) -> float:
    """
    Increment a value based on a chance
    """
    return variable + (increment if random.random() < chance else 0.)


def determine_width_points(
        center: np.array,
        width: float,
        angle: float
) -> tuple[np.array, np.array]:
    """
    Calculate the top and bot points using the center, width and angle.
    """
    offset = width * np.array([-np.sin(angle), np.cos(angle)]) / 2.
    top_point = np.rint(center + offset).astype(int)
    bot_point = np.rint(center - offset).astype(int)

    return top_point, bot_point


def generate_path(
        initial_position: np.array,
        end_position: np.array,
        angle: float,
        width: float,
        surface: Surface,
        parameters: CrackPathParameters
) -> tuple[np.array, np.array]:
    """
    Generate a path and the corresponding top and bottom line from a set of crack parameters.
    """
    center = initial_position.copy().astype(float)
    center_int = initial_position.copy()
    top_point, bot_point = determine_width_points(center, width, angle)
    top_line, bot_line = np.array([top_point], int), np.array([bot_point], int)

    collision_checker = CollisionChecker(surface)
    breaking_gradient = collision_checker.in_object(center_int)

    width_grow = parameters.max_width_grow

    # Keep going until the crack becomes to small, reaches the boundary or reaches the end point
    while width >= parameters.min_width and \
            collision_checker.within_bounds(center) and \
            np.linalg.norm(end_position - center) > parameters.min_distance:
        gradient_angle = surface.map.gradient_angles[center_int[1], center_int[0]]
        gradient_vector = np.array([np.cos(gradient_angle), np.sin(gradient_angle)])

        end_point_angle = np.arctan2(end_position[1] - center[1], end_position[0] - center[0])
        end_point_vector = np.array([np.cos(end_point_angle), np.sin(end_point_angle)])

        # Blend the gradient and direction factor. We have a small chance to ignore the gradient.
        if not breaking_gradient and np.random.random_sample() < parameters.breakthrough_chance:
            breaking_gradient = True
        factor = parameters.gradient_influence if not breaking_gradient else 0.

        direction_vector = factor * gradient_vector + (1 - factor) * end_point_vector
        direction_vector /= np.linalg.norm(direction_vector)

        # Update parameters for the current step unless the step reaches outside of bounds
        center += parameters.step_size * direction_vector
        center_int = np.rint(center).astype(int)

        if not collision_checker.within_bounds(center):
            break

        angle = np.arctan2(direction_vector[1], direction_vector[0])
        top_point, bot_point = determine_width_points(center, width, angle)
        top_line, bot_line = np.append(top_line, [top_point], axis=0), np.append(bot_line, [bot_point], axis=0)
        breaking_gradient = collision_checker.in_object(center_int)

        width = increment_by_chance(
            width,
            width_grow if width / 2 < surface.map.distance_transform[center_int[1], center_int[0]] else -width_grow,
            parameters.width_update_chance
        )

    return top_line, bot_line


class CrackPathGenerator:
    """
    Generator class for creating 2D cracks based on CrackParameters.
    """

    __trajectory_generator: CrackTrajectoryGenerator = CrackTrajectoryGenerator()

    def __call__(self, crack_parameters: CrackGenerationParameters, surface: Surface) -> CrackPath:
        """
        Create a top and bottom line of the crack based on the surface.
        """
        # Initial positions
        pivot_points, width, angle = self.__trajectory_generator(crack_parameters, surface)

        # Launch path generation
        idx = 0
        top_line, bot_line = np.empty((0, 2)), np.empty((0, 2))
        while idx < pivot_points.shape[0] - 1:
            new_top_line, new_bot_line = generate_path(
                pivot_points[idx, :],
                pivot_points[idx + 1, :],
                angle,
                width,
                surface,
                crack_parameters.path_parameters
            )
            top_line = np.concatenate([top_line, new_top_line], axis=0)
            bot_line = np.concatenate([bot_line, new_bot_line], axis=0)
            idx += 1

        # Reduce step widths based on start and end pointiness
        path_parameters = crack_parameters.path_parameters
        width_grow_increments = max(
            path_parameters.max_width_grow,
            path_parameters.max_width_grow_factor * width
        )
        idx = 0
        start_steps = path_parameters.start_pointiness
        while idx < start_steps:
            vector_diff = top_line[idx, :] - bot_line[idx, :]
            center = (top_line[idx, :] + bot_line[idx, :]) / 2
            width = max(
                np.linalg.norm(vector_diff) - (start_steps - idx) * width_grow_increments,
                path_parameters.min_width
            )
            angle = np.arctan2(vector_diff[1], vector_diff[0])
            top_line[idx, :], bot_line[idx, :] = determine_width_points(center, width, angle)
            idx += 1

        total_steps = top_line.shape[0]
        idx = total_steps - path_parameters.end_pointiness
        while idx < total_steps:
            vector_diff = top_line[idx, :] - bot_line[idx, :]
            center = (top_line[idx, :] + bot_line[idx, :]) / 2
            width = max(np.linalg.norm(vector_diff) - idx * width_grow_increments, path_parameters.min_width)
            angle = np.arctan2(vector_diff[1], vector_diff[0])
            top_line[idx, :], bot_line[idx, :] = determine_width_points(center, width, angle)
            idx += 1

        # Filter out non-increasing points
        center_line = (top_line + bot_line) / 2
        distances = np.linalg.norm(center_line[:, :] - center_line[0, :], axis=1)
        gradient_distance = np.gradient(distances)

        filtered_points = gradient_distance > path_parameters.distance_improvement_threshold
        top_line = top_line[filtered_points, :]
        bot_line = bot_line[filtered_points, :]

        # Smooth path through 1D gaussian filter convolution or moving average
        smoothing = path_parameters.smoothing
        if smoothing > 0:
            if path_parameters.smoothing_type == 'gaussian':
                top_line[:, 0] = gaussian_filter1d(top_line[:, 0], 1., mode='nearest', radius=smoothing)
                top_line[:, 1] = gaussian_filter1d(top_line[:, 1], 1., mode='nearest', radius=smoothing)

                bot_line[:, 0] = gaussian_filter1d(bot_line[:, 0], 1., mode='nearest', radius=smoothing)
                bot_line[:, 1] = gaussian_filter1d(bot_line[:, 1], 1., mode='nearest', radius=smoothing)

            if path_parameters.smoothing_type == 'moving_average':
                padded_top_line = np.concatenate([
                    np.repeat([top_line[0, :]], smoothing - 1, 0),
                    top_line,
                    np.repeat([top_line[-1, :]], smoothing - 1, 0)
                ], 0)
                padded_bot_line = np.concatenate([
                    np.repeat([bot_line[0, :]], smoothing - 1, 0),
                    bot_line,
                    np.repeat([bot_line[-1, :]], smoothing - 1, 0)
                ], 0)
                top_cumsum, bot_cumsum = np.cumsum(padded_top_line, 0), np.cumsum(padded_bot_line, 0)

                top_line[1:-1] = (top_cumsum[2 * smoothing:, :] - top_cumsum[:-2 * smoothing, :]) / (2 * smoothing)
                bot_line[1:-1] = (bot_cumsum[2 * smoothing:, :] - bot_cumsum[:-2 * smoothing, :]) / (2 * smoothing)

        return CrackPath(top_line, bot_line)
