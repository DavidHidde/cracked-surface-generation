import numpy as np
from scipy.spatial import Delaunay

from models import CrackParameters, CrackModel
from .crack_path_generator import CrackPathGenerator


def centered_gaussian(points: np.array, variance: float) -> np.array:
    """
    Calculate the gaussian distribution value for a set of points
    """
    return 1. / (variance * np.sqrt(2 * np.pi)) - np.exp(points ** 2. / (2. * variance ** 2))


def calculate_control_points(parameters: CrackParameters) -> np.array:
    """
    Calculate x y z control net for the crack mesh
    """
    crack_generator = CrackPathGenerator()
    path = crack_generator(parameters)
    top_line, bot_line = path.top_line, path.bot_line

    # Depth points
    length = top_line.shape[0]
    points_per_line = 2 + parameters.depth_resolution
    coords = np.empty((length * points_per_line, 3))
    for idx in range(length):
        top_point, bot_point = top_line[idx, :], bot_line[idx, :]
        x_points = np.linspace(top_point[0], bot_point[0], points_per_line)
        y_points = np.linspace(top_point[1], bot_point[1], points_per_line)

        # Calculate the variance of the distribution. We consider the start and end point at mu - 2 std.
        width = np.sqrt(np.sum((top_point - bot_point) ** 2))
        sigma = 1 / width  # inverse relation between width and depth
        z_points = -parameters.depth * centered_gaussian(np.linspace(-2 * sigma, 2 * sigma, points_per_line), sigma)

        # Copy points over
        coords[points_per_line * idx:points_per_line * idx + points_per_line, 0] = x_points
        coords[points_per_line * idx:points_per_line * idx + points_per_line, 1] = y_points
        coords[points_per_line * idx:points_per_line * idx + points_per_line, 2] = z_points

    return coords[:length * points_per_line, :]


class CrackModelGenerator:
    """
    Generator of 3D crack models
    """

    def __call__(self, parameters: CrackParameters) -> CrackModel:
        """
        Create a quad mesh out of a set of parameters
        """

        # Calculate and center coords
        coords = calculate_control_points(parameters)
        coords[:, 0] -= np.mean(coords[:, 0])
        coords[:, 1] -= np.mean(coords[:, 1])
        coords[:, 2] -= np.mean(coords[:, 2])

        # Calculate quad faces
        points_per_line = 2 + parameters.depth_resolution
        length = coords[:, 0].shape[0] // points_per_line
        faces = np.empty(((length - 1) * points_per_line, 4), dtype=int)

        # Main body
        for column_idx in range(length - 1):
            for row_idx in range(points_per_line):
                face_idx = column_idx * points_per_line + row_idx
                next_face_idx = face_idx + 1 if row_idx < points_per_line - 1 else column_idx * points_per_line
                faces[face_idx, :] = np.array([
                    face_idx,
                    face_idx + points_per_line,  # Next column, same row
                    next_face_idx + points_per_line,  # Next column, next row
                    next_face_idx  # Same column, next row
                ])

        # Sides - which we keep triangulated
        side_faces = np.concatenate([
            Delaunay(coords[:points_per_line, 1:]).simplices,
            Delaunay(coords[(length - 1) * points_per_line:, 1:]).simplices + (length - 1) * points_per_line
        ], 0)

        return CrackModel(parameters, coords, faces, side_faces)
