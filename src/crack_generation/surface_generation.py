import cv2
import numpy as np
from scipy.signal import find_peaks

from crack_generation.model import Surface


def find_brick_dims(thresholded: np.array) -> tuple[int, int]:
    """Approximate brick dims using the thresholded image. We take the last peak of the histogram as the width and height."""
    contours, _ = cv2.findContours(
        thresholded,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    widths = []
    heights = []
    for contour in contours:
        if contour.shape[0] >= 4:
            contour = contour.squeeze()
            x, y, width, height = cv2.boundingRect(contour)
            widths.append(width)
            heights.append(height)

    counts_w, bins_w = np.histogram(widths)
    counts_h, bins_h = np.histogram(heights)
    width_peaks, _ = find_peaks(counts_w, height=0)
    height_peaks, _ = find_peaks(counts_h, height=0)

    return int(bins_w[width_peaks[-1]]), int(bins_h[height_peaks[-1]])


def create_surface_from_image(image: np.array) -> Surface:
    """Create a surface from an image through thresholding."""
    blurred = cv2.medianBlur(image, 15)
    kernel_size = np.min(image.shape) // 20  # Consider a 5% window
    kernel_size += 1 - kernel_size % 2  # Make uneven if necessary
    thresholded = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, kernel_size, 2)

    inverse_thresholded = 255 - thresholded
    distance_transform = cv2.distanceTransform(inverse_thresholded, cv2.DIST_L2, cv2.DIST_MASK_5)

    grad_x = cv2.Sobel(distance_transform, cv2.CV_64F, 1, 0, ksize=5)
    grad_y = cv2.Sobel(distance_transform, cv2.CV_64F, 0, 1, ksize=5)
    angles = np.arctan2(grad_y, grad_x)

    brick_width, brick_height = find_brick_dims(thresholded)
    return Surface(image, distance_transform, angles, brick_width, brick_height)
