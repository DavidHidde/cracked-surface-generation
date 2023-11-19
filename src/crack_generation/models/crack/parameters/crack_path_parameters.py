from dataclasses import dataclass


@dataclass
class CrackPathParameters:
    """
    Parameters used for generating a crack path. This includes post-processing parameters.
    """

    ##
    # Algorithm parameters - These affect the crack generation process and therefore the path
    ##
    step_size: float  # gradient ascent step size
    gradient_influence: float  # weigth of the gradient step that should be used for gradient ascent

    width_update_chance: float  # chance to update the width
    breakthrough_chance: float  # chance to ignore the gradient direction

    min_distance: float  # minimum distance to the next pivot point before generation is stopped

    min_width: float  # minimum width the crack is allowed to have
    max_width_grow: float  # absolute maximum value that the width of the crack is allowed to grow at a step
    max_width_grow_factor: float  # maximum percentage of the width the crack is allowed to grow at a step

    ##
    # Post processing parameters - These affect how the crack is post processed
    ##
    start_pointiness: int  # number of steps that should decrease in width at the start of the crack
    end_pointiness: int  # number of steps that should decrease in width at the end of the crack
    smoothing: int  # Gaussian kernel size for 1D smoothing
    distance_improvement_threshold: float  # minimum value the distance to the start has to increase per step to not be filtered out
