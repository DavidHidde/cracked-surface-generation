from dataclasses import asdict
from math import floor
from tkinter import Tk, Button, Scale, HORIZONTAL, Frame
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.axes import Axes
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from models import CrackParameters

from sys import platform as sys_pf

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
    plot_function: Callable[[CrackParameters, Axes], None]
    fig: Figure
    ax: Axes

    # State
    parameters: CrackParameters
    sliders: dict[str, Scale] = {}

    def __init__(
            self,
            title: str,
            plot_function: Callable[[CrackParameters, Axes], None],
            figure: Figure,
            ax: Axes
    ):
        self.plot_function = plot_function
        self.fig = figure
        self.ax = ax

        self.window = Tk()
        self.window.title(title)

        ax.set_title(title)
        plt.title(title)

    def start(self, parameters: CrackParameters) -> None:
        """
        Start the UI with a certain set of parameters
        """
        self.parameters = parameters

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
        for key, slider in self.sliders.items():
            parameters_dict[key] = slider.get()
        self.parameters = CrackParameters(**parameters_dict)

        # Call plot function with updated parameters
        self.plot_function(self.parameters, self.ax)

        # Redraw
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def __add_widgets(self, parameters: CrackParameters) -> None:
        slider_settings = {
            'depth': {
                'label': 'Depth',
                'from_': 0.1,
                'to': 5.,
                'resolution': 0.1
            },
            'width': {
                'label': 'Width',
                'from_': 0.,
                'to': 10.,
                'resolution': 0.1
            },
            'length': {
                'label': 'Length',
                'from_': 0,
                'to': 1000,
                'resolution': 1
            },
            'angle': {
                'label': 'Initial angle',
                'from_': 0.,
                'to': 2 * np.pi,
                'resolution': 0.1
            },
            'variance': {
                'label': 'Variance',
                'from_': 0.,
                'to': 5.0,
                'resolution': 0.1
            },
            'width_variation': {
                'label': 'Width variation',
                'from_': 0.,
                'to': 1.,
                'resolution': 0.1
            },
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
            'randomness': {
                'label': 'Randomness',
                'from_': 0.,
                'to': 1.,
                'resolution': 0.1
            },
            'depth_resolution': {
                'label': 'Depth resolution',
                'from_': 0,
                'to': 100,
                'resolution': 1
            }
        }

        # Create subframe
        frame = Frame(self.window)
        frame.pack()

        # Add sliders
        parameters_dict = asdict(parameters)
        scales_per_column = floor(len(slider_settings) / 2.)
        idx = 0
        for attr_name, settings in slider_settings.items():
            scale = Scale(**settings, master=frame, orient=HORIZONTAL, length=250)
            scale.set(parameters_dict.get(attr_name, 0))
            scale.grid(
                row=idx % scales_per_column,
                column=(0 if idx < scales_per_column else 2)
            )
            self.sliders[attr_name] = scale
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
