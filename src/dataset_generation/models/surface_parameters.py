from dataclasses import dataclass

from .surface_map import SurfaceMap


@dataclass
class SurfaceParameters:
    """
    Parameters of a surface, just concerning dimensions and it's map.
    """
    
    brick_width: float
    brick_height: float
    
    mortar_size: float
    
    surface_map: SurfaceMap
    