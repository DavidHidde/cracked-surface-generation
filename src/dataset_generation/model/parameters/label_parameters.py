from dataclasses import dataclass


@dataclass
class LabelParameters:
    """Parameters used for setting the compositor and selecting patches."""

    num_patches: int

    min_active_pixels: int
    image_threshold: float
    uv_threshold: float
    ao_threshold: float

    base_output_directory: str
    image_output_directory: str
    label_output_directory: str
