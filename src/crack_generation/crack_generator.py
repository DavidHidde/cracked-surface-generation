import numpy as np

from crack_generation.model import Surface, Crack, Point
from crack_generation.model.parameters import CrackGenerationParameters
from crack_generation.path_functions import generate_pivot_trajectory, generate_path


class CrackGenerator:
    """Callable generator class for generating cracks in surfaces."""

    parameters: CrackGenerationParameters

    def __init__(self, parameters: CrackGenerationParameters):
        self.parameters = parameters

    def __call__(self, surface: Surface) -> Crack:
        """Generate a crack for the provided surface with the set parameters."""
        start_point, pivot_points = generate_pivot_trajectory(surface, self.parameters)
        all_points = [start_point]

        # Generate a path from pivot point to pivot point
        for pivot_point in pivot_points:
            all_points += generate_path(all_points[-1], pivot_point, surface, self.parameters.path_parameters)

        # Post process the crack
        # TODO

        # Create height map for crack
        # TODO
        height_map = np.zeros_like(surface.height_map)

        return Crack(all_points, pivot_points, height_map)
