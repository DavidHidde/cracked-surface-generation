import random

from crack_generation.models import CrackParameters
from dataset_generation.models import SurfaceParameters

DEPTH = 30
START_STEPS = 0
END_STEPS = 2
DEPTH_RESOLUTION = 1
STEP_SIZE = 2.
GRADIENT_INFLUENCE = 0.5
WIDTH_PERMUTATION_CHANCE = 0.1
BREAKTHROUGH_CHANCE = 0.1

MIN_WIDTH = 3.


class CrackParametersGenerator:
    """
    Class for generating crack parameters. This is currently only used to vary width.
    """

    def __call__(self, surface_parameters: SurfaceParameters) -> CrackParameters:
        """
        Generate new crack parameters based on constants and the surface.
        """

        max_width = surface_parameters.mortar_size * surface_parameters.surface_map.grid_factor
        return CrackParameters(
            DEPTH,
            max(random.random() * max_width, MIN_WIDTH),
            START_STEPS,
            END_STEPS,
            DEPTH_RESOLUTION,
            STEP_SIZE,
            GRADIENT_INFLUENCE,
            WIDTH_PERMUTATION_CHANCE,
            BREAKTHROUGH_CHANCE
        )
