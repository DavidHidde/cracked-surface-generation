import numpy as np
from numpy import random
from scipy.stats import norm

from crack_generation.models import CrackParameters, CrackPath


def __increment_by_chance(variable: float, increment: float, chance: float) -> float:
    """
    Increment a value based on a chance
    """
    return variable + (increment if random.random() < chance else 0.)


def __get_rotation_matrix(angle: float) -> np.array:
    """
    Get the rotation matrix for a certain angle
    """
    cos = np.cos(angle)
    sin = np.sin(angle)
    return np.array([
        [cos, -sin],
        [sin, cos]
    ])


def generate_path(
        initial_position: np.array,
        steps: int,
        variance: float,
        angle: float,
        width: float,
        width_variation: float,
        randomness: float,
        width_growth: float = 0.
) -> tuple[tuple[np.array, np.array], np.array, float, float]:
    """
    Generate a path and the corresponding top and bottom line from a set of crack parameters
    """
    top_line, bot_line = np.empty((steps, 2)), np.empty((steps, 2))
    center = np.copy(initial_position)
    sigma_square = variance ** 2

    idx = 0
    for idx in range(steps):
        increments = norm.rvs(size=3, scale=sigma_square)

        # Calculate new center point
        rotation_matrix = __get_rotation_matrix(angle)
        center += np.dot(rotation_matrix, np.array([1., increments[0]]))

        # Calculate the distance from the center for the lines and update them
        offset = np.dot(rotation_matrix, np.array([0., width]))
        variation = random.random()
        width_ratio = 0.5 + (
            variation * width_variation / 2. if variation > 0.5 else - variation * width_variation / 2.)

        top_line[idx, :] = center + width_ratio * offset
        bot_line[idx, :] = center - (1. - width_ratio) * offset

        # Stop condition: Minimum crack width is 0.1. We don't take this into account when growing the width.
        if width_growth <= 0 and width < 0.1:
            break

        # Update angle and width based on chance
        angle = __increment_by_chance(angle, increments[1], randomness)
        width = __increment_by_chance(width, increments[2] * width, randomness) + width_growth

    return (top_line[:idx + 1], bot_line[:idx + 1]), center, angle, width


class CrackPathGenerator:
    """
    Generator class for creating 2D cracks based on CrackParameters.
    """

    def __call__(self, parameters: CrackParameters) -> CrackPath:
        """
        Create a top and bottom line of the crack
        """
        angle = parameters.angle
        width = parameters.width

        total_steps = parameters.length
        start_steps = parameters.start_pointiness
        end_steps = parameters.end_pointiness

        # Account for start and end steps going out of bounds
        if start_steps + end_steps > total_steps:
            boundary_steps = start_steps + end_steps
            start_steps = round(total_steps * start_steps / boundary_steps)
            end_steps = round(total_steps * end_steps / boundary_steps)

        # Initial positions
        current_position = np.array([0., 0.])
        top_line = np.empty((0, 2))
        bot_line = np.empty((0, 2))

        # Perform start steps if necessary
        if start_steps > 0:
            width_grow_increments = max(0.2, 0.05 * parameters.width)
            width = max(0.1, parameters.width - start_steps * width_grow_increments)
            (top, bot), current_position, angle, width = generate_path(
                current_position,
                start_steps,
                parameters.variance,
                angle,
                width,
                parameters.width_variation,
                parameters.randomness,
                width_grow_increments
            )
            top_line = np.concatenate([top_line, top], 0)
            bot_line = np.concatenate([bot_line, bot], 0)

        (top, bot), current_position, angle, width = generate_path(
            current_position,
            total_steps - start_steps - end_steps,
            parameters.variance,
            angle,
            width,
            parameters.width_variation,
            parameters.randomness
        )
        top_line = np.concatenate([top_line, top], 0)
        bot_line = np.concatenate([bot_line, bot], 0)

        # Perform end steps if necessary
        if end_steps > 0:
            width_grow_increments = max(0.2, 0.05 * parameters.width)
            width -= width_grow_increments
            (top, bot), current_position, angle, width = generate_path(
                current_position,
                end_steps,
                parameters.variance,
                angle,
                width,
                parameters.width_variation,
                parameters.randomness,
                -width_grow_increments
            )
            top_line = np.concatenate([top_line, top], 0)
            bot_line = np.concatenate([bot_line, bot], 0)

        return CrackPath(top_line, bot_line)

    def create_single_line(self, path: CrackPath) -> tuple[np.array, np.array]:
        """
        Glue top and bot lines together into a single line and split into x and y
        """
        line = np.append(np.concatenate([path.top_line, np.flip(path.bot_line, 0)]), [path.top_line[0, :]], 0)
        return line[:, 0], line[:, 1]
