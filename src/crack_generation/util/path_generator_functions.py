"""
A set of helper functions for the Crack path generator.
"""
from math import ceil

import numpy as np
import random

from skimage import draw

from crack_generation.models import CrackPath, CrackParameters
from dataset_generation.models import SurfaceMap


def increment_by_chance(variable: float, increment: float, chance: float) -> float:
    """
    Increment a value based on a chance
    """
    return variable + (increment if random.random() < chance else 0.)


def get_rotation_matrix(angle: float) -> np.array:
    """
    Get the rotation matrix for a certain angle
    """
    cos = np.cos(angle)
    sin = np.sin(angle)
    return np.array([
        [cos, -sin],
        [sin, cos]
    ])


def create_single_line(path: CrackPath) -> tuple[np.array, np.array]:
    """
    Glue top and bot lines together into a single line and split into x and y
    """
    line = np.append(np.concatenate([path.top_line, np.flip(path.bot_line, 0)]), [path.top_line[0, :]], 0)
    return line[:, 0], line[:, 1]


def within_bounds(position: np.array, surface: SurfaceMap) -> bool:
    """
    Check if a position iw within the borders of the surface
    """
    return 0 < position[0] < surface.surface.shape[1] - 1 and \
        0 < position[1] < surface.surface.shape[0] - 1


def in_object(position: np.array, surface: SurfaceMap) -> bool:
    """
    Check if the poisition is in an object outside of the mortar.
    """
    return surface.mask[position[1], position[0]]


def scan_directions(position: np.array, surface: SurfaceMap, max_steps: int) -> np.array:
    """
    Scan around the positions and see how many steps it takes to hit a wall.
    """
    limits = np.array([-1, -1, -1, -1], dtype=int)
    increment_array = np.array([
        [1, 0],  # Right
        [0, 1],  # Up
        [-1, 0],  # Left
        [0, -1],  # Down
    ])

    for idx in range(1, max_steps + 1):
        for limit_idx in range(4):
            new_pos = position + idx * increment_array[limit_idx]
            if limits[limit_idx] == -1 and \
                    (idx == max_steps or not within_bounds(new_pos, surface) or in_object(new_pos, surface)):
                limits[limit_idx] = idx - 1

    return limits


def choose_initial_position(surface: SurfaceMap, parameters: CrackParameters) -> tuple[np.array, float, float]:
    """
    Choose an initial position of the crack (which should be mortar) and then find the width based on the parameters.
    """
    num_rows, num_columns = surface.surface.shape
    position = np.random.randint(
        [num_columns * 0.1, num_rows * 0.1],
        [num_columns * 0.9, num_rows * 0.9],
        size=(2,)
    )

    # Keep randoming until we find a value where we can actually start
    while not within_bounds(position, surface) or in_object(position, surface):
        position = np.random.randint(
            [num_columns * 0.1, num_rows * 0.1],
            [num_columns * 0.9, num_rows * 0.9],
            size=(2,)
        )

    # Scan the relative position of the crack and determine the angle and width
    margins = scan_directions(position, surface, 15)
    angles = [
        0.,  # Right
        np.pi / 2,  # Up
        np.pi,  # Left
        1.5 * np.pi,  # Down
    ]
    angle = angles[np.argmax(margins)]

    # Determine the width
    min_dir_idx = np.argmin(margins)
    dist_to_edge = margins[min_dir_idx]
    max_width = margins[(min_dir_idx + 2) % 4] + dist_to_edge
    width = min(max_width - 1, parameters.width)

    # Adjust for the width not fitting in the current position
    increment_array = np.array([
        [-1, 0],  # Right
        [0, -1],  # Up
        [1, 0],  # Left
        [0, 1],  # Down
    ])
    position += (ceil(width / 2) - dist_to_edge) * increment_array[min_dir_idx]

    return position, width, angle


def check_and_mark_overlap(
        top_point: np.array,
        bot_point: np.array,
        overlap_map: np.array,
        allowed_overlap: float
) -> bool:
    """
    Check if the overlap in area is within an allowed tolerance and marks it on the map if it is.
    Returns true if within the tolerance, else false.
    """
    rows, columns = draw.line(top_point[1], top_point[0], bot_point[1], bot_point[0])
    if np.mean(overlap_map[rows, columns].astype(float)) <= allowed_overlap:
        overlap_map[rows, columns] = True
        return True
    return False
