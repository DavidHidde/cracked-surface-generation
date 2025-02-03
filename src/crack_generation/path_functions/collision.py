import numpy as np

from crack_generation.model import Point, Surface


def within_surface(point: Point, surface: Surface) -> bool:
    """Check if a point is within a surface."""
    x, y = point.center
    height, width = surface.height_map.shape
    return 0 <= x < width and 0 <= y < height


def on_edge(point: Point, surface: Surface) -> bool:
    """Check if a point is on an edge of a surface."""
    x, y = point.center
    height, width = surface.height_map.shape
    return x == 0 or x == width - 1 or y == 0 or y == height - 1


def in_object(point: Point, surface: Surface) -> bool:
    """Check if a point is inside an object."""
    x, y = point.center
    return surface.distance_transform[y, x] == 0


def move_to_nearest_mortar(point: Point, surface: Surface) -> Point:
    """Move a point to the nearest point in the mortar."""
    max_step = np.max(surface.distance_transform)
    while within_surface(point, surface) and in_object(point, surface):
        angle = surface.gradient_angles[point.center[1], point.center[0]]
        step_size = max_step - surface.distance_transform[point.center[1], point.center[0]]
        update = np.rint(step_size * np.array([np.cos(angle), np.sin(angle)])).astype(int)
        point.center[0] += update[0]
        point.center[1] += update[1]

    return point
