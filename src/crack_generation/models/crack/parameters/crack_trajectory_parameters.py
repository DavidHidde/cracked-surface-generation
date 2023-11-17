from dataclasses import dataclass


@dataclass
class CrackTrajectoryParameters:
    """
    Parameters used to generate the pivot points of a crack.
    """
    
    # Distribution chances
    along_bottom_chance: float
    along_diagonal_chance: float
    along_side_chance: float
    
    # Pivot grid bounds
    max_pivot_brick_widths: int
    max_pivot_brick_heights: int
    max_pivot_points: int
    
    # Start point search space bounds
    row_search_space_percent: float 
    column_search_space_percent: float