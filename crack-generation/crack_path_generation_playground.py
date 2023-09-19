import math
import random

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from scipy.stats import norm
from math import cos, sin

# Get the rotation matrix for a certain angle
def get_rotation_matrix(angle):
    return np.array([
        [cos(angle), -sin(angle)],
        [sin(angle), cos(angle)]
    ])

# Create the Brownian motion crack
def get_crack(variance, initial_angle, permutation_chance, length):
    positions = np.zeros((length + 1, 2))
    
    # Initial angle
    angle = initial_angle
    
    sigma_square = variance ** 2
    for idx in range(length):
        increments = norm.rvs(size=2, scale=sigma_square)
        positions[idx + 1, :] = positions[idx, :] + np.dot(get_rotation_matrix(angle), np.array([1., increments[0]]))
        angle += (1. if random.random() < permutation_chance else 0.) * increments[1] * math.pi
        
    return positions[:, 0], positions[:, 1]

# Update plot
def update_plot(value):
    x, y = get_crack(variance_slider.val, angle_slider.val, chance_slider.val, LENGTH)
    line.set_xdata(x)
    line.set_ydata(y)
    
    # Set bounds again
    min_y = np.min(y)
    max_y = np.max(y)
    offset = (max_y - min_y) / 6.
    ax.set_yticks(np.linspace(min_y, max_y, 6))
    ax.set_ylim(min_y - offset, max_y + offset)
    
    # Redraw
    fig.canvas.draw_idle()
    fig.canvas.flush_events()

# Initial parameters
VARIANCE = 0.1
PERMUTATION_CHANCE = 0.1
LENGTH = 50
INITIAL_ANGLE = 0.0

# Setup plot
fig, ax = plt.subplots()
fig.subplots_adjust(left=0.25, bottom=0.25)

# Initial plot
x, y = get_crack(VARIANCE, INITIAL_ANGLE, PERMUTATION_CHANCE, LENGTH)
line, = ax.plot(x, y, color='red')
plt.grid()
plt.title('Brownian Motion example')
ax.set_title('Brownian Motion example')

# Horizontal sliders to control the chance, variance and initial angle.
ax_chance_slider = fig.add_axes([0.25, 0.05, 0.4, 0.03])
chance_slider = Slider(
    ax=ax_chance_slider,
    label='Angle chance',
    valmin=0.0,
    valmax=1.0,
    valinit=PERMUTATION_CHANCE,
)

ax_variance_slider = fig.add_axes([0.25, 0.1, 0.4, 0.03])
variance_slider = Slider(
    ax=ax_variance_slider,
    label='Variance',
    valmin=0.0,
    valmax=1.0,
    valinit=VARIANCE,
)

ax_angle_slider = fig.add_axes([0.25, 0.15, 0.4, 0.03])
angle_slider = Slider(
    ax=ax_angle_slider,
    label='Start angle',
    valmin=0.0,
    valmax=math.pi,
    valinit=INITIAL_ANGLE,
)

# Redraw button
redraw_button_ax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
button = Button(redraw_button_ax, 'Redraw', hovercolor='0.975')
button.on_clicked(update_plot)

plt.show()