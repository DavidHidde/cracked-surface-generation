from crack_generation.models.crack.parameters import CrackGenerationParameters, CrackDimensionParameters, \
    CrackPathParameters, CrackTrajectoryParameters

DEFAULT_PARAMETERS = CrackGenerationParameters(
    CrackDimensionParameters(
        width=5.,
        depth=5.,
        depth_resolution=5,
        sigma=1.,
        width_stds_offset=2.
    ),
    CrackPathParameters(
        step_size=2.,
        gradient_influence=0.5,
        width_update_chance=0.1,
        breakthrough_chance=0.1,
        min_distance=5.,
        min_width=2.,
        max_width_grow=0.2,
        max_width_grow_factor=0.2,
        start_pointiness=0,
        end_pointiness=0,
        smoothing=1,
        distance_improvement_threshold=0.1
    ),
    CrackTrajectoryParameters(
        along_bottom_chance=2/12,
        along_diagonal_chance=9/12,
        along_side_chance=1/12,
        max_pivot_brick_widths=5,
        max_pivot_brick_heights=7,
        max_pivot_points=6,
        row_search_space_percent=0.2,
        column_search_space_percent=0.2
    )
)