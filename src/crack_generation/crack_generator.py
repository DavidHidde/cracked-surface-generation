from crack_generation.model import Surface, Crack
from crack_generation.model.parameters import CrackGenerationParameters
from crack_generation.path_functions import generate_pivot_trajectory, generate_path, remove_non_increasing_points, \
    smooth_path_gaussian, smooth_path_moving_average, on_edge, shrink_path_end, create_height_map_from_path


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
        all_points = remove_non_increasing_points(
            all_points,
            self.parameters.path_parameters.distance_improvement_threshold
        )

        if self.parameters.path_parameters.smoothing_type == 'gaussian':
            all_points = smooth_path_gaussian(all_points, self.parameters.path_parameters.smoothing)
        if self.parameters.path_parameters.smoothing_type == 'moving_average':
            all_points = smooth_path_moving_average(all_points, self.parameters.path_parameters.smoothing)

        if not on_edge(all_points[-1], surface) and all_points[-1].width > self.parameters.path_parameters.min_width:
            all_points = shrink_path_end(
                all_points,
                self.parameters.path_parameters.min_width,
                self.parameters.path_parameters.max_width_grow
            )

        return Crack(
            all_points,
            pivot_points,
            create_height_map_from_path(all_points, surface, self.parameters.dimension_parameters)
        )
