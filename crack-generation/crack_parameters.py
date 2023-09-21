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

    # Generation parameters - These affect the look of the crack
    angle: float
    variance: float
    width_variation: float
    start_pointiness: int
    end_pointiness: int
    randomness: float
