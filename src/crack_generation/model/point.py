from dataclasses import dataclass


@dataclass
class Point:
    """A point on the crack, characterized by its position, angle and width."""

    angle: float
    width: float
    center: tuple[int, int]
