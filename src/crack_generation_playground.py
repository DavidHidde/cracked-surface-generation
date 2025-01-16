from argparse import ArgumentParser

import cv2
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from crack_generation import CrackGenerator, create_surface_from_image
from crack_generation.model import Surface, Point
from crack_generation.model.parameters import CrackGenerationParameters
from crack_generation.path_functions import point_to_coords
from util import PlaygroundInterface, DEFAULT_PARAMETERS


def create_single_line(path: list[Point]) -> tuple[np.array, np.array]:
    """
    Glue top and bot lines together into a single line and split into x and y.
    """
    parsed_path = np.array([point_to_coords(point) for point in path])
    line = np.append(
        np.concatenate(
            [
                parsed_path[:, 0, :],
                np.flip(parsed_path[:, 1, :], 0)
            ]
        ),
        [parsed_path[0, 0, :]],
        0
    )
    return line[:, 0], line[:, 1]


# Update plot
def update_plot(parameters: CrackGenerationParameters, surface: Surface, ax: Axes) -> None:
    ax.clear()
    crack_generator = CrackGenerator(parameters)
    crack = crack_generator(surface)
    x, y = create_single_line(crack.path)
    ax.plot(x, y, color='red', zorder=1)
    pivot_points = np.array(crack.trajectory)
    ax.scatter(pivot_points[:, 0], pivot_points[:, 1], color='red', edgecolors='black', zorder=10)
    ax.imshow(surface.height_map, cmap='gray')


def main():
    # Load surface file
    parameters = DEFAULT_PARAMETERS
    parser = ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the surface height map to test on.')
    filename = parser.parse_args().file
    height_map = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    surface = create_surface_from_image(height_map, 650, 150)

    # Setup plot
    fig, ax = plt.subplots(figsize=(16, 5), dpi=100)
    crack_generator = CrackGenerator(parameters)

    crack = crack_generator(surface)
    x, y = create_single_line(crack.path)
    ax.plot(x, y, color='red', zorder=1)
    pivot_points = np.array(crack.trajectory)
    ax.scatter(pivot_points[:, 0], pivot_points[:, 1], color='red', edgecolors='black', zorder=10)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.imshow(surface.height_map, cmap='gray')

    ui = PlaygroundInterface(
        'Crack parameter playground',
        update_plot,
        fig,
        ax
    )
    ui.start(parameters, surface)


if __name__ == "__main__":
    main()
