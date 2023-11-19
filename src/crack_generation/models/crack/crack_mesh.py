from dataclasses import dataclass

import numpy as np


@dataclass
class CrackMesh:
    """
    Data class for the polygonal mesh of a crack
    """

    vertices: np.array
    vertex_means: np.array

    faces: np.array  # Quads
    side_faces: np.array  # Triangles
