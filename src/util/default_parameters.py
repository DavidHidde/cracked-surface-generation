from crack_generation.model.parameters import CrackGenerationParameters, CrackDimensionParameters, \
    CrackPathParameters, CrackTrajectoryParameters

DEFAULT_PARAMETERS = CrackGenerationParameters(
    CrackDimensionParameters(
        width=15.,
        depth=5.,
        sigma=5.,
        width_stds_offset=1.5
    ),
    CrackPathParameters(
        step_size=15.,
        gradient_influence=0.5,
        width_update_chance=0.02,
        breakthrough_chance=0.1,
        min_distance=10.,
        min_width=2.,
        max_width_grow=2,
        smoothing_type='gaussian',
        smoothing=1,
        distance_improvement_threshold=0.1
    ),
    CrackTrajectoryParameters(
        along_bottom_chance=2 / 12,
        along_diagonal_chance=9 / 12,
        along_side_chance=1 / 12,
        max_pivot_brick_widths=5,
        max_pivot_brick_heights=7,
        max_pivot_points=6,
        row_search_space_percent=0.2,
        column_search_space_percent=0.2
    )
)
