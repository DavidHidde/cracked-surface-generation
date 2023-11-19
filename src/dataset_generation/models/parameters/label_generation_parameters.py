from dataclasses import dataclass


@dataclass
class LabelGenerationParameters:
    """
    Parameters used for rendering labels.
    """
    
    num_patches: int
    min_active_pixels: int
    min_rgb_value: tuple[int, int, int]
    max_rgb_value: tuple[int, int, int]
    