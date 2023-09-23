import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from scipy.spatial import ConvexHull

from crack_parameters import CrackParameters
from generators import CrackPathGenerator

from util import PlaygroundInterface


def centered_gaussian(points: np.array, variance: float) -> np.array:
    """
    Calculate the gaussian distribution value for a set of points
    """
    return 1. / (variance * np.sqrt(2 * np.pi)) - np.exp(points ** 2. / (2. * variance ** 2))


def calculate_hull(parameters: CrackParameters) -> np.array:
    crack_generator = CrackPathGenerator()
    top_line, bot_line = crack_generator(parameters)

    # Depth points
    points_per_line = 2 + parameters.depth_resolution
    coords = np.empty((parameters.length * points_per_line, 3))
    for idx in range(top_line.shape[0]):
        top_point, bot_point = top_line[idx, :], bot_line[idx, :]
        x_points = np.linspace(top_point[0], bot_point[0], points_per_line)
        y_points = np.linspace(top_point[1], bot_point[1], points_per_line)

        # Calculate the variance of the distribution. We consider the start and end point at mu - 2 std.
        width = np.sqrt((top_point[0] - bot_point[0]) ** 2 + (top_point[1] - bot_point[1]))
        sigma = width / 4.
        z_points = -centered_gaussian(np.linspace(-2 * sigma, 2 * sigma, points_per_line), sigma)

        # Copy points over
        coords[points_per_line * idx:points_per_line * idx + points_per_line, 0] = x_points
        coords[points_per_line * idx:points_per_line * idx + points_per_line, 1] = y_points
        coords[points_per_line * idx:points_per_line * idx + points_per_line, 2] = z_points

    return coords


def update_plot(parameters: CrackParameters, ax: Axes) -> None:
    coords = calculate_hull(parameters)
    hull = ConvexHull(coords)
    ax.clear()
    ax.plot_trisurf(coords[:, 0], coords[:, 1], coords[:, 2], triangles=hull.simplices, linewidth=0.2, antialiased=True)


# Initial parameters
VARIANCE = 0.1
PERMUTATION_CHANCE = 0.1
LENGTH = 20
WIDTH_VARIATION = 0.0
INITIAL_ANGLE = 0.0
INITIAL_WIDTH = 5.0
START_STEPS = 3
END_STEPS = 3

DEPTH_RESOLUTION = 4

# Initial plot
parameters = CrackParameters(
    0,
    INITIAL_WIDTH,
    LENGTH,
    INITIAL_ANGLE,
    VARIANCE,
    WIDTH_VARIATION,
    START_STEPS,
    END_STEPS,
    PERMUTATION_CHANCE,
    DEPTH_RESOLUTION
)
coords = calculate_hull(parameters)
hull = ConvexHull(coords)

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
ax.plot_trisurf(coords[:, 0], coords[:, 1], coords[:, 2], triangles=hull.simplices, linewidth=0.2, antialiased=True)

ui = PlaygroundInterface(
    'Crack 3D model playground',
    update_plot,
    fig,
    ax
)
ui.start(parameters)
