"""
A set of helper functions for the Crack path generator.
"""
import numpy as np
import random
from crack_generation.models import CrackPath


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
