import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.stats import norm

from crack_generation.model import Point, Surface
from crack_generation.model.parameters import CrackDimensionParameters
from crack_generation.path_functions import point_to_coords


def smooth_path_moving_average(path: list[Point], smoothing: int) -> list[Point]:
    """Smooth a crack path using a moving average filter."""
    coords = np.array([point.center for point in path], dtype=np.int32)
    padded = np.concatenate(
        [
            np.repeat([coords[0, :]], smoothing - 1, 0),
            coords,
            np.repeat([coords[-1, :]], smoothing - 1, 0)
        ], 0
    )

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


def shrink_path_end(path: list[Point], min_width: float, max_width_grow: float) -> list[Point]:
    """Adjust the width at the end of the path such that it ends in the min width with increments of max_width_grow."""
    new_path = path
    idx = len(new_path) - 1
    new_path[idx].width = min_width if new_path[idx].width > min_width else new_path[idx].width

    while idx > 0:
        diff = abs(new_path[idx - 1].width - new_path[idx].width)
        if diff <= max_width_grow:
            break

        new_path[idx - 1].width = new_path[idx].width + np.random.uniform(0.5, 1.) * max_width_grow
        idx -= 1

    return new_path


def remove_non_increasing_points(path: list[Point], threshold: float) -> list[Point]:
    """Remove non-increasing points compared to the starting point based on the derivative."""
    # Ignore very small paths
    if len(path) < 5:
        return path

    coords = np.array([point.center for point in path], dtype=np.int32)
    distances = np.linalg.norm(coords[:, :] - coords[0, :], axis=1)
    gradient_distances = np.gradient(distances)

    filter_mask = gradient_distances > threshold
    return list([point for idx, point in enumerate(path) if filter_mask[idx]])


def create_height_map_from_path(path: list[Point], surface: Surface, parameters: CrackDimensionParameters) -> np.array:
    """Create a height map representing the given path. This map can be used in combination with the surface."""
    height_map = np.zeros_like(surface.height_map, dtype=np.uint8)
    coords = np.array([point_to_coords(point) for point in path], dtype=np.int32)
    flattened = np.concatenate([coords[:, 0, :], np.flip(coords[:, 1, :], axis=0)], axis=0)

    inverse_crack = cv2.fillPoly(height_map, [flattened], color=255)
    distance_transform = cv2.distanceTransform(inverse_crack, cv2.DIST_L2, cv2.DIST_MASK_5).astype(np.float64)
    mask = distance_transform > 0

    # Use the distance transform to transform distances to normalized Gaussian depth values
    distance_transform[mask] -= np.max(distance_transform) # Center values
    distance_transform[mask] *= parameters.sigma * parameters.width_stds_offset  # Set 1 to the desired sigma value

    distance_transform[mask] = norm.pdf(distance_transform[mask], scale=parameters.sigma ** 2)
    distance_transform[mask] = distance_transform[mask] / np.max(distance_transform[mask])  # Normalize
    distance_transform[mask] = np.clip(distance_transform[mask], 1. / 255., 1.) # Bump min to at least a visible value

    return distance_transform
