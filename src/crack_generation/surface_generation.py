import cv2
import numpy as np

from crack_generation.model import Surface


def create_surface_from_image(image: np.array, brick_width: int, brick_height: int) -> Surface:
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

    return Surface(image, distance_transform, angles, brick_width, brick_height)
