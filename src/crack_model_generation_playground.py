from argparse import ArgumentParser

import math
import pickle

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from crack_generation import CrackGenerator
from crack_generation.models.crack.parameters import CrackGenerationParameters
from crack_generation.models.surface import Surface
from util import PlaygroundInterface, DEFAULT_PARAMETERS


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


def update_plot(parameters: CrackGenerationParameters, surface: Surface, ax: Axes) -> None:
    ax.clear()
    crack = (CrackGenerator())(parameters, surface)
    coords = crack.mesh.vertices
    for face in crack.mesh.faces:
        face = np.append(face, face[0])  # Here we cycle back to the first coordinate
        ax.plot(coords[face, 0], coords[face, 1], coords[face, 2], color='red')
    for face in crack.mesh.side_faces:
        face = np.append(face, face[0])  # Here we cycle back to the first coordinate
        ax.plot(coords[face, 0], coords[face, 1], coords[face, 2], color='red')

    set_ax_bounds(ax, coords[:, 0], coords[:, 1], coords[:, 2])


def main():
    # Load surface file
    parameters = DEFAULT_PARAMETERS

    parser = ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the .surface file to test on.')
    filename = parser.parse_args().file
    with open(filename, 'rb') as surface_dump:
        surface: Surface = pickle.load(surface_dump)

    # Initial plot
    fig, ax = plt.subplots(figsize=(16, 5), dpi=100, subplot_kw={"projection": "3d"})
    update_plot(parameters, surface, ax)

    ui = PlaygroundInterface(
        'Crack 3D model playground',
        update_plot,
        fig,
        ax
    )
    ui.start(parameters, surface)


if __name__ == "__main__":
    main()
