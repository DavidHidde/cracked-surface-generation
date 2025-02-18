import os

import bpy
import cv2
import numpy as np

from dataset_generation.model.parameters import LabelParameters

MIN_IMG_PIXEL_VALUE = 1  # Set to 1 rather than 0 to deal with noise


def generate_patches(
    parameters: LabelParameters,
    iteration_index: int,
    image: np.array,
    label: np.array
) -> int:
    """Split the provided image and labels into patches based on the parameters. Returns the number of patches created."""
    idx = iteration_index
    count = 0

    step_size = image.shape[0] // parameters.num_patches
    for row_idx in range(parameters.num_patches):
        start_y, end_y = row_idx * step_size, (row_idx + 1) * step_size
        for col_idx in range(parameters.num_patches):
            start_x, end_x = col_idx * step_size, (col_idx + 1) * step_size
            label_patch = label[start_y:end_y, start_x:end_x]

            if np.sum(label_patch > MIN_IMG_PIXEL_VALUE) > parameters.min_active_pixels:
                img_patch = image[start_y:end_y, start_x:end_x]
                cv2.imwrite(os.path.join(parameters.image_output_directory, f'crack-{idx + count}.png'), img_patch)
                cv2.imwrite(os.path.join(parameters.label_output_directory, f'crack-{idx + count}.png'), label_patch)
                count += 1
    return count


def post_process_label(label: np.array) -> np.array:
    """Process the label using the image to get a binary result."""
    new_label = np.zeros_like(label, dtype=np.float32)
    mask = label > MIN_IMG_PIXEL_VALUE
    min, max = np.min(label[mask]), np.max(label[mask])
    new_label[mask] = (label[mask] - min) / (max - min)  # Normalize
    new_label = (new_label * 255).astype(np.uint8)

    new_label = cv2.adaptiveThreshold(
        new_label,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        9,
        2
    )
    new_label[~mask] = 0  # Set background back to 0
    return new_label


def render_crack(parameters: LabelParameters, iteration_index: int) -> int:
    """Given the prepared scene, render and process the crack image and label. Returns the number of output images."""
    bpy.ops.render.render(write_still=False, animation=False)
    rendered_image_path = os.path.join(parameters.base_output_directory, f'image-{bpy.context.scene.frame_current}.png')
    rendered_label_path = os.path.join(parameters.base_output_directory, f'label-{bpy.context.scene.frame_current}.png')

    # Check if the label is 'empty'
    img = cv2.imread(rendered_image_path)
    label = cv2.imread(rendered_label_path, cv2.IMREAD_GRAYSCALE)
    if np.sum(label > MIN_IMG_PIXEL_VALUE) < parameters.min_active_pixels:
        return 0

    # All is okay, we split into patches or move and rename the files
    label = post_process_label(label)
    if parameters.num_patches > 1:
        return generate_patches(parameters, iteration_index, img, label)

    file_name = f'crack-{iteration_index}.png'
    cv2.imwrite(os.path.join(parameters.image_output_directory, file_name), img)
    cv2.imwrite(os.path.join(parameters.label_output_directory, file_name), label)
    return 1
