import math

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from crack_parameters import CrackParameters
from crack_path_generator import CrackPathGenerator


# Set the bounds of a plot
def set_ax_bounds(ax, x, y):
    min_x = math.floor(np.min(x) - 5)
    max_x = math.ceil(np.max(x) + 5)
    ax.set_xticks(np.linspace(min_x, max_x, 7, dtype=int))
    ax.set_xlim(min_x, max_x)

    min_y = math.floor(np.min(y) - 5)
    max_y = math.ceil(np.max(y) + 5)
    ax.set_yticks(np.linspace(min_y, max_y, 7, dtype=int))
    ax.set_ylim(min_y, max_y)


# Update plot
def update_plot(value):
    parameters = CrackParameters(
        0,
        INITIAL_WIDTH,
        int(length_slider.val),
        angle_slider.val,
        variance_slider.val,
        width_variation_slider.val,
        int(start_slider.val),
        int(end_slider.val),
        chance_slider.val
    )
    x, y = crack_generator(parameters)
    line.set_xdata(x)
    line.set_ydata(y)
    set_ax_bounds(ax, x, y)

    # Redraw
    fig.canvas.draw_idle()
    fig.canvas.flush_events()


# Initial parameters
VARIANCE = 0.1
PERMUTATION_CHANCE = 0.1
LENGTH = 500
WIDTH_VARIATION = 0.0
INITIAL_ANGLE = 0.0
INITIAL_WIDTH = 5.0
START_STEPS = 0
END_STEPS = 0

# Setup plot
fig, ax = plt.subplots()
fig.subplots_adjust(left=0.25, bottom=0.50)

# Initial plot
crack_generator = CrackPathGenerator()
parameters = CrackParameters(
    0,
    INITIAL_WIDTH,
    LENGTH,
    INITIAL_ANGLE,
    VARIANCE,
    WIDTH_VARIATION,
    START_STEPS,
    END_STEPS,
    PERMUTATION_CHANCE
)
x, y = crack_generator(parameters)
line, = ax.plot(x, y, color='red')
set_ax_bounds(ax, x, y)
plt.grid()
plt.title('Crack parameter playground')
ax.set_title('Crack parameter playground')

# Horizontal sliders to control the chance, variance and initial angle.
ax_chance_slider = fig.add_axes([0.25, 0.35, 0.4, 0.03])
chance_slider = Slider(
    ax=ax_chance_slider,
    label='Chance',
    valmin=0.0,
    valmax=1.0,
    valinit=PERMUTATION_CHANCE,
)

ax_variance_slider = fig.add_axes([0.25, 0.30, 0.4, 0.03])
variance_slider = Slider(
    ax=ax_variance_slider,
    label='Variance',
    valmin=0.0,
    valmax=1.0,
    valinit=VARIANCE,
)

ax_angle_slider = fig.add_axes([0.25, 0.25, 0.4, 0.03])
angle_slider = Slider(
    ax=ax_angle_slider,
    label='Start angle',
    valmin=0.0,
    valmax=2 * math.pi,
    valinit=INITIAL_ANGLE,
)

ax_width_variation_slider = fig.add_axes([0.25, 0.20, 0.4, 0.03])
width_variation_slider = Slider(
    ax=ax_width_variation_slider,
    label='Width variation',
    valmin=0.,
    valmax=1.,
    valinit=WIDTH_VARIATION
)

ax_start_pointiness_slider = fig.add_axes([0.25, 0.15, 0.4, 0.03])
start_slider = Slider(
    ax=ax_start_pointiness_slider,
    label='Start pointiness',
    valmin=0,
    valmax=50,
    valinit=START_STEPS,
    valstep=1
)

ax_end_pointiness_slider = fig.add_axes([0.25, 0.10, 0.4, 0.03])
end_slider = Slider(
    ax=ax_end_pointiness_slider,
    label='End pointiness',
    valmin=0,
    valmax=50,
    valinit=END_STEPS,
    valstep=1
)

ax_length_slider = fig.add_axes([0.25, 0.05, 0.4, 0.03])
length_slider = Slider(
    ax=ax_length_slider,
    label='Length',
    valmin=0,
    valmax=1000,
    valinit=LENGTH,
    valstep=1
)

# Redraw button
redraw_button_ax = fig.add_axes([0.8, 0.20, 0.1, 0.04])
button = Button(redraw_button_ax, 'Redraw', hovercolor='0.975')
button.on_clicked(update_plot)

plt.show()
