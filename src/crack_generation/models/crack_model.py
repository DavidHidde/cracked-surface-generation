from dataclasses import dataclass

import numpy as np

from .crack_parameters import CrackParameters


@dataclass
class CrackModel:
    """
    Data class for a Quad mesh of a Crack
    """

    parameters: CrackParameters
    points: np.array
    point_means: np.array
    faces: np.array
    side_faces: np.array
