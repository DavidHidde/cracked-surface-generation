from dataclasses import dataclass

from .surface_dimensions import SurfaceDimensions
from .surface_map import SurfaceMap


@dataclass
class Surface:
    """
    A surface, represented by its map and the dimensions
    """
    
    map: SurfaceMap
    dimensions: SurfaceDimensions
    