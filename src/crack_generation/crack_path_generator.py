import numpy as np
from scipy.stats import norm

from crack_generation.models import CrackParameters, CrackPath
from crack_generation.operations import get_rotation_matrix, increment_by_chance, CrackPointChooser, CollisionChecker
from dataset_generation.models import SurfaceParameters, SurfaceMap

MIN_DISTANCE = 1

MIN_WIDTH = 1.
MAX_WIDTH_GROW_FACTOR = 0.05
DEFAULT_WIDTH_GROW = 0.2
MAX_TURN_STEPS = 10


def determine_new_points(
        center: np.array,
        width: float,
        angle: float,
        sigma_square: float
) -> tuple[np.array, np.array, np.array]:
    """
    Calculate the new center and top/bot points
    """
    # Calculate new center point
    rotation_matrix = get_rotation_matrix(angle)
    new_center = center + np.dot(rotation_matrix, np.array([1., norm.rvs(scale=sigma_square)]))

    # Calculate the distance from the center for the lines and update them
    offset = np.dot(rotation_matrix, np.array([0., width])) / 2.
    top_point = np.rint(new_center + offset).astype(int)
    bot_point = np.rint(new_center - offset).astype(int)

    return new_center, top_point, bot_point


def generate_path(
        initial_position: np.array,
        end_position: np.array,
        surface_map: SurfaceMap,
        angle: float,
        width: float,
        width_grow_increments: float,
        parameters: CrackParameters
) -> tuple[np.array, np.array]:
    """
    Generate a path and the corresponding top and bottom line from a set of crack parameters
    """
    collision_checker = CollisionChecker(surface_map)
    sigma_square = parameters.variance ** 2
    center, top_point, bot_point = determine_new_points(initial_position, width, angle, sigma_square)
    top_line, bot_line = np.array([top_point], int), np.array([bot_point], int)
    moving_through_object = collision_checker.in_object(initial_position)
    idx = 0

    # Perform crack path generation, which ends when the crack becomes too small or reached the end
    while width >= MIN_WIDTH and np.linalg.norm(end_position - center) > MIN_DISTANCE:
        new_center, top_point, bot_point = determine_new_points(center, width, angle, sigma_square)

        # Stop condition: We should be within bounds
        if not collision_checker.within_bounds(top_point) or not collision_checker.within_bounds(bot_point):
            break

        # Check if we're outside the mortar. If we're not, add it to the line
        center_in_object = collision_checker.in_object(np.rint(new_center).astype(int))
        top_in_object = collision_checker.in_object(top_point)
        bot_in_object = collision_checker.in_object(bot_point)

        # While the current position remain invalid, try to fix it
        while not moving_through_object and (center_in_object or top_in_object or bot_in_object):
            if np.random.random_sample() < parameters.breakthrough_chance:
                moving_through_object = True
                break

            center_int = np.rint(center).astype(int)
            angle += 0.2 * surface_map.gradient_angles[center_int[1], center_int[0]]
            width -= 0.2 * max(width - surface_map.distance_transform[center_int[1], center_int[0]], 0)

            center_in_object = collision_checker.in_object(np.rint(new_center).astype(int))
            top_in_object = collision_checker.in_object(top_point)
            bot_in_object = collision_checker.in_object(bot_point)

        if collision_checker.check_and_mark_overlap(top_point, bot_point, parameters.allowed_path_overlap):
            center = new_center
            top_line = np.append(top_line, [top_point], axis=0)
            bot_line = np.append(bot_line, [bot_point], axis=0)
            moving_through_object = center_in_object or top_in_object or bot_in_object
            width += width_grow_increments if idx < parameters.start_pointiness else 0
            angle = np.arctan2(end_position[1] - center[1], end_position[0] - center[0])
            idx += 1

        # Update angle and width based on chance
        # increments = norm.rvs(size=2, scale=sigma_square)
        # angle = increment_by_chance(angle, increments[0], parameters.angle_update_chance)
        # width = increment_by_chance(width, increments[1], parameters.width_update_chance) + width_grow

    return top_line[:idx], bot_line[:idx]


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

        # Shrink width if the width should grow at the start
        width_grow_increments = max(DEFAULT_WIDTH_GROW, MAX_WIDTH_GROW_FACTOR * width)
        width = max(MIN_WIDTH, width - crack_parameters.start_pointiness * width_grow_increments)

        # Launch path generation
        top_line, bot_line = generate_path(
            start_position,
            end_position,
            surface_parameters.surface_map,
            angle,
            width,
            width_grow_increments,
            crack_parameters
        )

        return CrackPath(top_line, bot_line)
