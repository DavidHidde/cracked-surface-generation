from dataclasses import asdict
from math import ceil
from tkinter import Tk, Button, Scale, HORIZONTAL, Frame
from typing import Callable

import matplotlib.pyplot as plt

from matplotlib.axes import Axes
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from sys import platform as sys_pf

from crack_generation.model.parameters import CrackGenerationParameters, CrackDimensionParameters, \
    CrackPathParameters, CrackTrajectoryParameters
from crack_generation.model import Surface

# Fix for MacOS
if sys_pf == 'darwin':
    import matplotlib

    matplotlib.use("TkAgg")


class PlaygroundInterface:
    """
    Shared playground UI class.
    """

    # TkInter parameters
    window: Tk

    # Plot parameters
    plot_function: Callable[[CrackGenerationParameters, Surface, Axes], None]
    fig: Figure
    ax: Axes

    # State
    parameters: CrackGenerationParameters
    surface: Surface
    sliders: dict[str, dict[str, Scale]] = {}

    def __init__(
            self,
            title: str,
            plot_function: Callable[[CrackGenerationParameters, Surface, Axes], None],
            figure: Figure,
            ax: Axes
    ):
        self.plot_function = plot_function
        self.fig = figure
        self.ax = ax

        self.sliders = {
            'dimension_parameters': {},
            'path_parameters': {},
            'trajectory_parameters': {}
        }

        self.window = Tk()
        self.window.title(title)

        ax.set_title(title)
        plt.title(title)

    def start(self, parameters: CrackGenerationParameters, surface: Surface) -> None:
        """
        Start the UI with a certain set of parameters
        """
        self.parameters = parameters
        self.surface = surface

        # creating the Tkinter canvas containing the Matplotlib figure
        canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        canvas.draw()

        # placing the canvas on the Tkinter window
        canvas.get_tk_widget().pack()

        # creating the Matplotlib toolbar
        toolbar = NavigationToolbar2Tk(canvas, self.window)
        toolbar.update()

        # placing the toolbar on the Tkinter window
        canvas.get_tk_widget().pack()

        self.__add_widgets(parameters)

        self.window.mainloop()

    def redraw(self):
        # Update current parameters
        parameters_dict = asdict(self.parameters)
        for child_dict_key, child_dict in self.sliders.items():
            for key, slider in child_dict.items():
                parameters_dict[child_dict_key][key] = slider.get()
        self.parameters = CrackGenerationParameters(
            CrackDimensionParameters(**parameters_dict['dimension_parameters']),
            CrackPathParameters(**parameters_dict['path_parameters']),
            CrackTrajectoryParameters(**parameters_dict['trajectory_parameters'])
        )

        # Call plot function with updated parameters
        self.plot_function(self.parameters, self.surface, self.ax)

        # Redraw
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def __add_widgets(self, parameters: CrackGenerationParameters) -> None:
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
        scales_per_column = ceil((len(slider_settings['dimension_parameters']) + len(slider_settings['path_parameters']) + len(slider_settings['trajectory_parameters'])) / 2)
        idx = 0
        for child_dict_key, child_dict in slider_settings.items():
            for attr_name, settings in child_dict.items():
                scale = Scale(**settings, master=frame, orient=HORIZONTAL, length=250)
                scale.set(parameters_dict[child_dict_key].get(attr_name, 0))
                scale.grid(
                    row=idx % scales_per_column,
                    column=(0 if idx < scales_per_column else 2)
                )
                self.sliders[child_dict_key][attr_name] = scale
                idx += 1

        # Add redraw button
        redraw_button = Button(
            master=frame,
            command=self.redraw,
            height=2,
            width=10,
            text='Redraw'
        )
        redraw_button.grid(
            row=scales_per_column,
            column=1
        )
