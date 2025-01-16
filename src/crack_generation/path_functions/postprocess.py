import numpy as np
from scipy.ndimage import gaussian_filter1d

from crack_generation.model import Point


def smooth_path_moving_average(path: list[Point], smoothing: int) -> list[Point]:
    """Smooth a crack path using a moving average filter."""
    coords = np.array([point.center for point in path], dtype=np.int32)
    padded = np.concatenate([
        np.repeat([coords[0, :]], smoothing - 1, 0),
        coords,
        np.repeat([coords[-1, :]], smoothing - 1, 0)
    ], 0)

    cumsum = np.cumsum(padded, 0)
    coords[1:-1] = np.rint((cumsum[2 * smoothing:, :] - cumsum[:-2 * smoothing, :]) / (2 * smoothing))

    new_path = path
    for idx in range(0, len(new_path)):
        new_path[idx].center = coords[idx, 0], coords[idx, 1]
    return new_path


def smooth_path_gaussian(path: list[Point], smoothing: int) -> list[Point]:
    """Smooth a crack path using a 1D Gaussian filter."""
    coords = np.array([point.center for point in path], dtype=np.int32)
    coords[:, 0] = gaussian_filter1d(coords[:, 0], 1., mode='nearest', radius=smoothing)
    coords[:, 1] = gaussian_filter1d(coords[:, 1], 1., mode='nearest', radius=smoothing)

    new_path = path
    for idx in range(0, len(new_path)):
        new_path[idx].center = coords[idx, 0], coords[idx, 1]
    return new_path

def remove_non_increasing_points(path: list[Point], threshold: float) -> list[Point]:
    """Remove non-increasing points compared to the starting point based on the derivative."""
    coords = np.array([point.center for point in path], dtype=np.int32)
    distances = np.linalg.norm(coords[:, :] - coords[0, :], axis=1)
    gradient_distances = np.gradient(distances)

    filter_mask = gradient_distances > threshold
    return list([point for idx, point in enumerate(path) if filter_mask[idx]])