from dataclasses import dataclass


@dataclass
class CrackParameters:
    """
    Hyper parameters of a crack which can be used to generate a crack
    """

    # Dimension parameters - These directly affect the size of the crack
    depth: float
    width: float
    length: int

    # Generation parameters - These affect mainly the look of the crack
    variance: float
    start_pointiness: int
    end_pointiness: int
    depth_resolution: int
    allowed_path_overlap: float
    angle_update_chance: float
    width_update_chance: float
    breakthrough_chance: float
