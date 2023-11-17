from dataclasses import dataclass


@dataclass
class SurfaceDimensions:
    """
    Data class for the dimensions of a surface
    """
    
    brick_width: float
    brick_height: float
    mortar_size: float
