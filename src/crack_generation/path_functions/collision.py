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
