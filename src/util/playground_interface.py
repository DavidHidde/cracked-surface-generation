from dataclasses import asdict
from math import ceil
from tkinter import Tk, Button, Scale, HORIZONTAL, Frame
from typing import Union

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.axes import Axes
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from sys import platform as sys_pf

from crack_generation import CrackGenerator
from crack_generation.model.parameters import CrackGenerationParameters, CrackDimensionParameters, \
    CrackPathParameters, CrackTrajectoryParameters
from crack_generation.model import Surface, Crack, Point
from crack_generation.path_functions import point_to_coords, create_height_map_from_path

# Fix for MacOS
if sys_pf == 'darwin':
    import matplotlib

    matplotlib.use("TkAgg")


def single_line_from_crack_path(path: list[Point]) -> np.array:
    """Transform a list of points into a single looping line."""
    coords = np.array([point_to_coords(point) for point in path], dtype=np.int32)
    return np.concatenate([coords[:, 0, :], np.flip(coords[:, 1, :], axis=0)], axis=0)


class PlaygroundInterface:
    """
    Interactive UI for checking and adjusting crack generation parameters.
    """
    WINDOW_TITLE = 'Crack parameter playground'
    REGENERATE_BUTTON_TEXT = 'Regenerate crack'
    UPDATE_DEPTH_BUTTON_TEXT = 'Update depth plot'

    # TkInter parameters
    window: Tk

    # State
    surface: Surface
    parameters: CrackGenerationParameters

    # UI
    fig: Figure
    path_ax: Axes
    height_ax: Axes

    sliders: dict[str, dict[str, Scale]]
    crack: Union[Crack, None] = None

    def __init__(
        self,
        surface: Surface,
        parameters: CrackGenerationParameters
    ):
        self.surface = surface
        self.parameters = parameters

        self.fig, [self.path_ax, self.height_ax] = plt.subplots(
            1,
            2,
            sharex=True,
            sharey=True,
            figsize=(16, 5),
            dpi=100
        )
        self.fig.suptitle(self.WINDOW_TITLE)
        self.path_ax.set_xlabel('x')
        self.path_ax.set_ylabel('y')

        self.sliders = {
            'dimension_parameters': {},
            'path_parameters': {},
            'trajectory_parameters': {}
        }

        self.window = Tk()
        self.window.title(self.WINDOW_TITLE)

        canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas, self.window)
        toolbar.update()
        canvas.get_tk_widget().pack()

        self.add_widgets(parameters)

    def start(self) -> None:
        """Start the UI."""
        self.generate_and_plot_crack()
        self.window.mainloop()

    def update_parameters_from_sliders(self) -> None:
        """Read sliders into parameters."""
        parameters_dict = asdict(self.parameters)
        for child_dict_key, child_dict in self.sliders.items():
            for key, slider in child_dict.items():
                parameters_dict[child_dict_key][key] = slider.get()
        self.parameters = CrackGenerationParameters(
            CrackDimensionParameters(**parameters_dict['dimension_parameters']),
            CrackPathParameters(**parameters_dict['path_parameters']),
            CrackTrajectoryParameters(**parameters_dict['trajectory_parameters'])
        )

    def generate_and_plot_crack(self, *args) -> None:
        """Generate a crack and plot it. This resets both plots."""
        self.update_parameters_from_sliders()
        self.path_ax.clear()

        crack_generator = CrackGenerator(self.parameters)
        self.crack = crack_generator(self.surface)
        coords = np.array([point_to_coords(point) for point in self.crack.path], dtype=np.int32)
        flattened = np.concatenate([coords[:, 0, :], np.flip(coords[:, 1, :], axis=0)], axis=0)

        self.path_ax.plot(flattened[:, 0], flattened[:, 1], color='red', zorder=1)
        pivot_points = np.array(self.crack.trajectory)
        self.path_ax.scatter(pivot_points[:, 0], pivot_points[:, 1], color='red', edgecolors='black', zorder=10)
        self.path_ax.imshow(self.surface.height_map, cmap='gray')

        self.plot_height_map(redraw=False)

        # Redraw
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def plot_height_map(self, *args, redraw=True) -> None:
        """Plot the height map of the crack and optionally redraw."""
        self.height_ax.clear()

        if redraw:
            height_map = create_height_map_from_path(
                self.crack.path,
                self.surface,
                self.parameters.dimension_parameters
            )
            self.height_ax.imshow(height_map)
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        else:
            self.height_ax.imshow(self.crack.crack_height_map)

    def add_widgets(self, parameters: CrackGenerationParameters) -> None:
        """Add sliders and draw buttons."""
        slider_settings = {
            'dimension_parameters': {
                'depth': {
                    'label': 'Depth',
                    'from_': 1,
                    'to': 15.,
                    'resolution': 1
                },
                'width': {
                    'label': 'Initial width',
                    'from_': 1,
                    'to': 15.,
                    'resolution': 1.
                },
                'depth_resolution': {
                    'label': 'Depth resolution',
                    'from_': 0,
                    'to': 10,
                    'resolution': 1
                },
            },
            'path_parameters': {
                'start_pointiness': {
                    'label': 'Start pointiness',
                    'from_': 0,
                    'to': 100,
                    'resolution': 1
                },
                'end_pointiness': {
                    'label': 'End pointiness',
                    'from_': 0,
                    'to': 100,
                    'resolution': 1
                },
                'step_size': {
                    'label': 'Step size',
                    'from_': 0.1,
                    'to': 5.,
                    'resolution': 1
                },
                'gradient_influence': {
                    'label': 'Gradient influence',
                    'from_': 0.,
                    'to': 1.,
                    'resolution': 0.01
                },
                'width_update_chance': {
                    'label': 'Width update chance',
                    'from_': 0.,
                    'to': 1.,
                    'resolution': 0.01
                },
                'breakthrough_chance': {
                    'label': 'Breakthrough chance',
                    'from_': 0.,
                    'to': 1.,
                    'resolution': 0.01
                },
                'smoothing': {
                    'label': 'Smoothing',
                    'from_': 0,
                    'to': 10,
                    'resolution': 1
                },
            },
            'trajectory_parameters': {}
        }

        # Create subframe
        frame = Frame(self.window)
        frame.pack()

        # Add sliders
        parameters_dict = asdict(self.parameters)
        scales_per_column = ceil(
            (len(slider_settings['dimension_parameters']) + len(slider_settings['path_parameters']) + len(
                slider_settings['trajectory_parameters']
            )) / 2
        )
        idx = 0
        for child_dict_key, child_dict in slider_settings.items():
            for attr_name, settings in child_dict.items():
                scale = Scale(**settings, master=frame, orient=HORIZONTAL, length=250)
                scale.set(parameters_dict[child_dict_key].get(attr_name, 0))
                scale.grid(
                    row=idx % scales_per_column,
                    column=(0 if idx < scales_per_column else 1),
                    padx=20,
                    pady=5
                )
                self.sliders[child_dict_key][attr_name] = scale
                idx += 1

        # Add buttons
        crack_redraw_button = Button(
            master=frame,
            command=self.generate_and_plot_crack,
            height=2,
            width=10,
            text=self.REGENERATE_BUTTON_TEXT
        )
        crack_redraw_button.grid(
            row=scales_per_column,
            column=0,
            pady=40
        )

        height_redraw_button = Button(
            master=frame,
            command=self.plot_height_map,
            height=2,
            width=10,
            text=self.UPDATE_DEPTH_BUTTON_TEXT
        )
        height_redraw_button.grid(
            row=scales_per_column,
            column=1,
            pady=40
        )
