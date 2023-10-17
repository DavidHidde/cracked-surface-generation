import math
import pickle

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from crack_generation import CrackModelGenerator
from crack_generation.models import CrackParameters

from crack_generation.ui import PlaygroundInterface


def set_ax_bounds(ax, x, y, z):
    min_x = math.floor(np.min(x) - 5)
    max_x = math.ceil(np.max(x) + 5)
    ax.set_xticks(np.linspace(min_x, max_x, 7, dtype=int))
    ax.set_xlim(min_x, max_x)

    min_y = math.floor(np.min(y) - 5)
    max_y = math.ceil(np.max(y) + 5)
    ax.set_yticks(np.linspace(min_y, max_y, 7, dtype=int))
    ax.set_ylim(min_y, max_y)

    min_z = math.floor(np.min(z) - 5)
    max_z = math.ceil(np.max(z) + 5)
    ax.set_zticks(np.linspace(min_z, max_z, 7, dtype=int))
    ax.set_zlim(min_z, max_z)


def update_plot(parameters: CrackParameters, ax: Axes) -> None:
    ax.clear()
    model = (CrackModelGenerator())(parameters, surface_map)
    coords = model.points
    for face in model.faces:
        face = np.append(face, face[0])  # Here we cycle back to the first coordinate
        ax.plot(coords[face, 0], coords[face, 1], coords[face, 2], color='red')
    for face in model.side_faces:
        face = np.append(face, face[0])  # Here we cycle back to the first coordinate
        ax.plot(coords[face, 0], coords[face, 1], coords[face, 2], color='blue')

    set_ax_bounds(ax, coords[:, 0], coords[:, 1], coords[:, 2])


# Load surface file
with open('resources/surface.dump', 'rb') as surface_dump:
    surface_map = pickle.load(surface_dump)

# Initial parameters
DEPTH = 5
VARIANCE = 0.1
LENGTH = 100
INITIAL_WIDTH = 5
START_STEPS = 0
END_STEPS = 0
DEPTH_RESOLUTION = 4
ALLOWED_OVERLAP = 1.
ANGLE_PERMUTATION_CHANCE = 0.1
WIDTH_PERMUTATION_CHANCE = 0.1
BREAKTHROUGH_CHANCE = 0.1

# Initial plot
parameters = CrackParameters(
    DEPTH,
    INITIAL_WIDTH,
    LENGTH,
    VARIANCE,
    START_STEPS,
    END_STEPS,
    DEPTH_RESOLUTION,
    ALLOWED_OVERLAP,
    ANGLE_PERMUTATION_CHANCE,
    WIDTH_PERMUTATION_CHANCE,
    BREAKTHROUGH_CHANCE
)
generator = CrackModelGenerator()
model = generator(parameters, surface_map)

fig, ax = plt.subplots(figsize=(16, 5), dpi=100, subplot_kw={"projection": "3d"})

coords = model.points
for face in model.faces:
    face = np.append(face, face[0])  # Here we cycle back to the first coordinate
    ax.plot(coords[face, 0], coords[face, 1], coords[face, 2], color='red')
for face in model.side_faces:
    face = np.append(face, face[0])  # Here we cycle back to the first coordinate
    ax.plot(coords[face, 0], coords[face, 1], coords[face, 2], color='blue')

set_ax_bounds(ax, coords[:, 0], coords[:, 1], coords[:, 2])

ui = PlaygroundInterface(
    'Crack 3D model playground',
    update_plot,
    fig,
    ax
)
ui.start(parameters)
