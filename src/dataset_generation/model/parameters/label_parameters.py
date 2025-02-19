from dataclasses import dataclass


@dataclass
class LabelParameters:
    """Parameters used for setting the compositor and selecting patches."""

    num_patches: int
    resolution: tuple[int, int] # width x height
    min_active_pixels: int

    base_output_directory: str
    image_output_directory: str
    label_output_directory: str
