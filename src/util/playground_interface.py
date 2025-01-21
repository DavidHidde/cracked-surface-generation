from dataclasses import asdict
from tkinter import Tk, Button, Scale, HORIZONTAL, Frame, Canvas
from tkinter.constants import VERTICAL, RIGHT, FALSE, Y, LEFT, BOTH, TRUE, NW
from tkinter.ttk import Label, Scrollbar
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


class VerticalScrolledFrame(Frame):
    """Vertical scollframe class from https://coderslegacy.com/python/make-scrollable-frame-in-tkinter/ß"""

    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(
            self, bd=0, highlightthickness=0,
            width=200, height=300,
            yscrollcommand=vscrollbar.set
        )
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=self.canvas.yview)

        # Reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = Frame(self.canvas)
        self.interior.bind('<Configure>', self._configure_interior)
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=NW)

    def _configure_interior(self, event):
        # Update the scrollbars to match the size of the inner frame.
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion=(0, 0, size[0], size[1]))
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the canvas's width to fit the inner frame.
            self.canvas.config(width=self.interior.winfo_reqwidth())

    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the inner frame's width to fill the canvas.
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())


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

        self.add_widgets()

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
            self.update_parameters_from_sliders()
            height_map = create_height_map_from_path(
                self.crack.path,
                self.surface,
                self.parameters.dimension_parameters
            )
            self.crack.crack_height_map = height_map
            self.height_ax.imshow(height_map)
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        else:
            self.height_ax.imshow(self.crack.crack_height_map)

    def add_widgets(self) -> None:
        """Add sliders and draw buttons."""
        labels = {
            'dimension_parameters': 'Dimension parameters',
            'path_parameters': 'Path parameters',
            'trajectory_parameters': 'Trajectory parameters'
        }
        slider_settings = {
            'dimension_parameters': {
                'width': {
                    'label': 'Initial width',
                    'from_': 1,
                    'to': 50.,
                    'resolution': 1.
                },
                'sigma': {
                    'label': 'Depth Gaussian sigma',
                    'from_': 0.,
                    'to': 10.,
                    'resolution': 0.1
                },
                'width_stds_offset': {
                    'label': 'Depth Gaussian width sigma offset',
                    'from_': 0.1,
                    'to': 5.,
                    'resolution': 0.1
                },
            },
            'path_parameters': {
                'step_size': {
                    'label': 'Step size',
                    'from_': 1.,
                    'to': 50.,
                    'resolution': 0.5
                },
                'gradient_influence': {
                    'label': 'Gradient influence',
                    'from_': 0.,
                    'to': 1.,
                    'resolution': 0.01
                },
                'min_distance': {
                    'label': 'Min L2 stopping distance',
                    'from_': 0.,
                    'to': 100.,
                    'resolution': 1
                },
                'min_width': {
                    'label': 'Min crack width before stopping',
                    'from_': 0.,
                    'to': 100.,
                    'resolution': 1
                },
                'max_width_grow': {
                    'label': 'Max width fluctuation per update',
                    'from_': 0.,
                    'to': 20.,
                    'resolution': 0.1
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
                    'to': 20,
                    'resolution': 1
                },
                'distance_improvement_threshold': {
                    'label': 'Min distance improvement for keeping points',
                    'from_': 0.,
                    'to': 1.,
                    'resolution': 0.05
                },
            },
            'trajectory_parameters': {
                'max_pivot_brick_widths': {
                    'label': 'Max number of bricks in width pivot window',
                    'from_': 1.,
                    'to': 15.,
                    'resolution': 1
                },
                'max_pivot_brick_heights': {
                    'label': 'Max number of bricks in height pivot window',
                    'from_': 1.,
                    'to': 15.,
                    'resolution': 1
                },
                'max_pivot_points': {
                    'label': 'Max number of pivot points',
                    'from_': 1.,
                    'to': 15.,
                    'resolution': 1
                },
                'row_search_space_percent': {
                    'label': 'Percentage of height considered for starting point',
                    'from_': 0.1,
                    'to': 1.,
                    'resolution': 0.1
                },
                'column_search_space_percent': {
                    'label': 'Percentage of width considered for starting point',
                    'from_': 0.1,
                    'to': 1.,
                    'resolution': 0.1
                },
            }
        }

        # Create subframe
        frame = VerticalScrolledFrame(self.window)
        frame.pack()

        # Add sliders
        parameters_dict = asdict(self.parameters)
        for column_idx, (child_dict_key, child_dict) in enumerate(slider_settings.items()):
            label = Label(frame.interior, text=labels[child_dict_key])
            label.grid(row=0, column=column_idx)
            for row_idx, (attr_name, settings) in enumerate(child_dict.items()):
                scale = Scale(**settings, master=frame.interior, orient=HORIZONTAL, length=250)
                scale.set(parameters_dict[child_dict_key].get(attr_name, 0))
                scale.grid(
                    row=row_idx + 1,
                    column=column_idx,
                    padx=20,
                    pady=5
                )
                self.sliders[child_dict_key][attr_name] = scale

        # Add buttons
        crack_redraw_button = Button(
            master=frame.interior,
            command=self.generate_and_plot_crack,
            height=2,
            width=10,
            text=self.REGENERATE_BUTTON_TEXT
        )
        crack_redraw_button.grid(
            row=1,
            column=3,
            padx=40,
            pady=10
        )

        height_redraw_button = Button(
            master=frame.interior,
            command=self.plot_height_map,
            height=2,
            width=10,
            text=self.UPDATE_DEPTH_BUTTON_TEXT
        )
        height_redraw_button.grid(
            row=2,
            column=3,
            padx=40,
            pady=10
        )
