import pickle

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from crack_generation import CrackPathGenerator
from crack_generation.models.crack import CrackPath
from crack_generation.models.crack.parameters import CrackGenerationParameters
from crack_generation.models.surface import Surface
from util import PlaygroundInterface, DEFAULT_PARAMETERS


def create_single_line(path: CrackPath) -> tuple[np.array, np.array]:
    """
    Glue top and bot lines together into a single line and split into x and y
    """
    line = np.append(np.concatenate([path.top_line, np.flip(path.bot_line, 0)]), [path.top_line[0, :]], 0)
    return line[:, 0], line[:, 1]


# Update plot
def update_plot(parameters: CrackGenerationParameters, surface: Surface, ax: Axes) -> None:
    crack_generator = CrackPathGenerator()
    path = crack_generator(parameters, surface)
    x, y = create_single_line(path)
    line = ax.get_lines()[0]
    line.set_xdata(x)
    line.set_ydata(y)


def main():
    # Load surface file
    parameters = DEFAULT_PARAMETERS
    with open('resources/surface_parameters.dump', 'rb') as surface_dump:
        surface = pickle.load(surface_dump)

    # Setup plot
    fig, ax = plt.subplots(figsize=(16, 5), dpi=100)
    crack_generator = CrackPathGenerator()

    path = crack_generator(parameters, surface)
    x, y = create_single_line(path)
    line, = ax.plot(x, y, color='red')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.imshow(surface.map.mask, cmap='gray')
    ax.invert_yaxis()  # Align with 3D model

    ui = PlaygroundInterface(
        'Crack parameter playground',
        update_plot,
        fig,
        ax
    )
    ui.start(parameters, surface)


if __name__ == "__main__":
    main()
