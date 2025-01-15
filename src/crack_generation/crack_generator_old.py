import numpy as np
from scipy.spatial import Delaunay

from .crack_path_generator import CrackPathGenerator
from .models.crack import Crack, CrackPath, CrackMesh
from crack_generation.models.parameters import CrackGenerationParameters
from .models.surface import Surface


def centered_gaussian(points: np.array, variance: float) -> np.array:
    """
    Calculate the gaussian distribution value for a set of points
    """
    return 1. / (variance * np.sqrt(2 * np.pi)) * np.exp(- points ** 2. / (2. * variance ** 2))


def calculate_control_points(path: CrackPath, parameters: CrackGenerationParameters) -> np.array:
    """
    Calculate x y z control net for the crack mesh
    """

    top_line, bot_line = path.top_line, path.bot_line
    length = top_line.shape[0]

    # Calculate z points, which we keep constant
    dimension_parameters = parameters.dimension_parameters
    points_per_line = 2 + dimension_parameters.depth_resolution
    z_points = -dimension_parameters.depth * centered_gaussian(np.linspace(
        -dimension_parameters.width_stds_offset * dimension_parameters.sigma,
        dimension_parameters.width_stds_offset * dimension_parameters.sigma,
        points_per_line
    ), dimension_parameters.sigma)
    # We want the begin and end to be on the same line, so we move all points down to set the ends to 0
    z_points -= z_points[0]

    # Depth points
    points_per_line = 2 + dimension_parameters.depth_resolution
    coords = np.empty((length * points_per_line, 3))
    for idx in range(length):
        top_point, bot_point = top_line[idx, :], bot_line[idx, :]
        x_points = np.linspace(top_point[0], bot_point[0], points_per_line)
        y_points = np.linspace(top_point[1], bot_point[1], points_per_line)

        # Copy points over
        coords[points_per_line * idx:points_per_line * idx + points_per_line, 0] = x_points
        coords[points_per_line * idx:points_per_line * idx + points_per_line, 1] = y_points
        coords[points_per_line * idx:points_per_line * idx + points_per_line, 2] = z_points

    return coords[:length * points_per_line, :]


class CrackGenerator:
    """
    Generator of 3D crack models
    """

    __path_generator: CrackPathGenerator = CrackPathGenerator()

    def __call__(self, parameters: CrackGenerationParameters, surface: Surface) -> Crack:
        """
        Create a crack out of a surface and parameters
        """
        crack_generator = CrackPathGenerator()
        path = crack_generator(parameters, surface)

        # Calculate and center coords
        coords = calculate_control_points(path, parameters)
        coords_means = np.mean(coords, axis=0)
        coords[:, :] -= coords_means

        # Calculate quad faces
        points_per_line = 2 + parameters.dimension_parameters.depth_resolution
        length = coords[:, 0].shape[0] // points_per_line
        faces = np.empty(((length - 1) * points_per_line, 4), dtype=int)

        # Main body - quads
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
        start_coords = coords[:points_per_line, :]
        end_coords = coords[(length - 1) * points_per_line:, :]
        start_x_is_const = np.all(np.isclose(start_coords[:, 0], start_coords[0, 0]))
        end_x_is_const = np.all(np.isclose(end_coords[:, 0], end_coords[0, 0]))
        side_faces = np.concatenate([
            Delaunay(start_coords[:, [(1 if start_x_is_const else 0), 2]]).simplices,
            Delaunay(end_coords[:, [(1 if end_x_is_const else 0), 2]]).simplices + (length - 1) * points_per_line
        ], 0)

        return Crack(path, CrackMesh(coords, coords_means, faces, side_faces), parameters)
