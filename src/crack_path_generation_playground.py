import pickle

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from crack_generation.models import CrackParameters
from crack_generation import CrackPathGenerator
from crack_generation.ui import PlaygroundInterface
from crack_generation.operations import create_single_line


# Update plot
def plot_path(parameters: CrackParameters, ax: Axes):
    crack_generator = CrackPathGenerator()
    path = crack_generator(parameters, surface_parameters)
    x, y = create_single_line(path)
    line = ax.get_lines()[0]
    line.set_xdata(x)
    line.set_ydata(y)


# Load surface file
with open('resources/surface_parameters.dump', 'rb') as surface_dump:
    surface_parameters = pickle.load(surface_dump)

# Initial parameters
VARIANCE = 0.1
INITIAL_WIDTH = 5
START_STEPS = 0
END_STEPS = 0
ALLOWED_OVERLAP = 1.
ANGLE_PERMUTATION_CHANCE = 0.1
WIDTH_PERMUTATION_CHANCE = 0.1
BREAKTHROUGH_CHANCE = 0.1

# Setup plot
fig, ax = plt.subplots(figsize=(16, 5), dpi=100)

# Initial plot
crack_generator = CrackPathGenerator()
parameters = CrackParameters(
    0,
    INITIAL_WIDTH,
    VARIANCE,
    START_STEPS,
    END_STEPS,
    0,
    ALLOWED_OVERLAP,
    ANGLE_PERMUTATION_CHANCE,
    WIDTH_PERMUTATION_CHANCE,
    BREAKTHROUGH_CHANCE
)
path = crack_generator(parameters, surface_parameters)
x, y = create_single_line(path)
line, = ax.plot(x, y, color='red')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.imshow(surface_parameters.surface_map.mask, cmap='gray')

ui = PlaygroundInterface(
    'Crack parameter playground',
    plot_path,
    fig,
    ax
)
ui.start(parameters)
