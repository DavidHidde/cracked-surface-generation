from dataclasses import dataclass


@dataclass
class LabelGenerationParameters:
    """
    Parameters used for rendering labels.
    """
    
    num_patches: int
    min_active_pixels: int
    min_threshold: int
    max_threshold: int
    threshold_increments: int
