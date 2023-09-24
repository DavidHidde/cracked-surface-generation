import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from generators.crack_model_generator import CrackModelGenerator
from models import CrackParameters

from util import PlaygroundInterface, ObjFileExporter


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
    model = (CrackModelGenerator())(parameters)
    coords = model.points
    for face in model.faces:
        face = np.append(face, face[0])  # Here we cycle back to the first coordinate
        ax.plot(coords[face, 0], coords[face, 1], coords[face, 2], color='red')
    set_ax_bounds(ax, coords[:, 0], coords[:, 1], coords[:, 2])

    exporter = ObjFileExporter()
    exporter(model, 'crack.obj')


# Initial parameters
DEPTH = 0.3
VARIANCE = 0.1
PERMUTATION_CHANCE = 0.1
LENGTH = 50
WIDTH_VARIATION = 0.0
INITIAL_ANGLE = 0.0
INITIAL_WIDTH = 5.0
START_STEPS = 0
END_STEPS = 0
DEPTH_RESOLUTION = 4

# Initial plot
parameters = CrackParameters(
    DEPTH,
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
generator = CrackModelGenerator()
model = generator(parameters)

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

coords = model.points
for face in model.faces:
    face = np.append(face, face[0])  # Here we cycle back to the first coordinate
    ax.plot(coords[face, 0], coords[face, 1], coords[face, 2], color='red')
for face in model.side_faces:
    face = np.append(face, face[0])  # Here we cycle back to the first coordinate
    ax.plot(coords[face, 0], coords[face, 1], coords[face, 2], color='red')

set_ax_bounds(ax, coords[:, 0], coords[:, 1], coords[:, 2])
exporter = ObjFileExporter()
exporter(model, 'crack.obj')

ui = PlaygroundInterface(
    'Crack 3D model playground',
    update_plot,
    fig,
    ax
)
ui.start(parameters)
