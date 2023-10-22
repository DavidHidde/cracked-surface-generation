import numpy as np

from crack_generation.models import CrackParameters
from .path_generator_functions import get_rotation_matrix
from .collision_checker import CollisionChecker
from dataset_generation.models import SurfaceParameters, SurfaceMap


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


def move_to_mortar(position: np.array, surface_map: SurfaceMap) -> np.array:
    """
    Move a point inside of an object to the mortar.
    """
    collision_checker = CollisionChecker(surface_map)
    new_position = position.copy()

    while collision_checker.within_bounds(new_position) and collision_checker.in_object(new_position):
        rotation_matrix = get_rotation_matrix(surface_map.inverse_gradient_angles[new_position[1], new_position[0]])
        new_position += np.dot(rotation_matrix, [1., 0.]).astype(int)

    return new_position


def determine_start_point(grid_width: float, grid_height: float, surface_map: SurfaceMap) -> np.array:
    """
    Determine the starting point on the grid
    """
    collision_checker = CollisionChecker(surface_map)

    # Determine the initial point
    num_rows, num_columns = surface_map.surface.shape
    position = np.array([-1, -1], int)

    # Keep randoming until we find a value where we can actually start
    while not collision_checker.within_bounds(position) or collision_checker.in_object(position):
        position = np.random.randint(
            [grid_width, grid_height],
            [num_columns - grid_width, num_rows - grid_height],
            size=(2,)
        )
        position = move_to_mortar(position, surface_map)

    return position


class CrackPointChooser:
    """
    Class aimed at choosing the initial parameters by choosing the start and end points of a crack.
    """

    def __call__(
            self,
            crack_parameters: CrackParameters,
            surface_parameters: SurfaceParameters
    ) -> tuple[np.array, np.array, float, float]:
        """
        Choose an initial position, find the end position and determine the width/height.
        """

        # Determine the grid dimensions
        unit_width = surface_parameters.brick_width * surface_parameters.surface_map.grid_factor
        unit_heigth = surface_parameters.brick_height * surface_parameters.surface_map.grid_factor

        grid_width = np.random.normal(3 * unit_width, 2 * unit_width / 3)
        grid_height = np.random.normal(3 * unit_heigth, 2 * unit_heigth / 3)

        # Determine the start and end positions
        start_position = determine_start_point(grid_width, grid_height, surface_parameters.surface_map)
        end_position = np.rint(start_position + np.array([grid_width, grid_height])).astype(int)
        end_position = move_to_mortar(end_position, surface_parameters.surface_map)

        # Determine angle and width at the start position
        grad_angle = surface_parameters.surface_map.gradient_angles[start_position[1], start_position[0]]
        path_angle = np.arctan2(end_position[1] - start_position[1], end_position[0] - start_position[0])
        angle = (grad_angle + path_angle) / 2.

        width = determine_width(angle, surface_parameters, crack_parameters)

        # Adjust for the width not fitting in the current position
        if width > surface_parameters.surface_map.distance_transform[start_position[1], start_position[0]]:
            rotation_matrix = get_rotation_matrix(angle)
            start_position += np.dot(rotation_matrix, [width / 2., 0.]).astype(int)

        return start_position, end_position, width, angle
