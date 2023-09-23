import math

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from crack_parameters import CrackParameters
from generators import CrackPathGenerator
from util import PlaygroundInterface


# Set the bounds of a plot
def set_ax_bounds(ax, x, y):
    min_x = math.floor(np.min(x) - 5)
    max_x = math.ceil(np.max(x) + 5)
    ax.set_xticks(np.linspace(min_x, max_x, 7, dtype=int))
    ax.set_xlim(min_x, max_x)

    min_y = math.floor(np.min(y) - 5)
    max_y = math.ceil(np.max(y) + 5)
    ax.set_yticks(np.linspace(min_y, max_y, 7, dtype=int))
    ax.set_ylim(min_y, max_y)


# Update plot
def plot_path(parameters: CrackParameters, ax: Axes):
    crack_generator = CrackPathGenerator()
    top, bot = crack_generator(parameters)
    x, y = crack_generator.create_single_line(top, bot)
    line = ax.get_lines()[0]
    line.set_xdata(x)
    line.set_ydata(y)
    set_ax_bounds(ax, x, y)


# Initial parameters
VARIANCE = 0.1
PERMUTATION_CHANCE = 0.1
LENGTH = 500
WIDTH_VARIATION = 0.0
INITIAL_ANGLE = 0.0
INITIAL_WIDTH = 5.0
START_STEPS = 0
END_STEPS = 0

# Setup plot
fig, ax = plt.subplots()

# Initial plot
crack_generator = CrackPathGenerator()
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
    0
)
top, bot = crack_generator(parameters)
x, y = crack_generator.create_single_line(top, bot)
line, = ax.plot(x, y, color='red')
set_ax_bounds(ax, x, y)
plt.grid()

ui = PlaygroundInterface(
    'Crack parameter playground',
    plot_path,
    fig,
    ax
)
ui.start(parameters)
