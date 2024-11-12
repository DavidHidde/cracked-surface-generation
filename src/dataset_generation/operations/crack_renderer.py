import os
import shutil

import bpy
import cv2
import numpy as np

from dataset_generation.models.parameters import LabelGenerationParameters


def generate_patches(
        parameters: LabelGenerationParameters,
        image: np.array,
        label: np.array,
        file_name: str,
) -> int:
    """
    Split the provided image and labels into patches based on the parameters.
    Returns the number of patches created.
    """
    idx = int(file_name[6:])
    count = 0

    step_size = image.shape[0] // parameters.num_patches
    for row_idx in range(parameters.num_patches):
        start_y, end_y = row_idx * step_size, (row_idx + 1) * step_size
        for col_idx in range(parameters.num_patches):
            start_x, end_x = col_idx * step_size, (col_idx + 1) * step_size
            label_patch = label[start_y:end_y, start_x:end_x]

            if np.sum(label_patch) > parameters.min_active_pixels:
                img_patch = image[start_y:end_y, start_x:end_x]
                cv2.imwrite(os.path.join(parameters.image_output_directory, f'crack-{idx + count}.png'), img_patch)
                cv2.imwrite(os.path.join(parameters.label_output_directory, f'crack-{idx + count}.png'), label_patch)
                count += 1
    return count

class CrackRenderer:
    """
    Render operation aimed at rendering a crack and its label.
    """

    def __call__(
            self,
            parameters: LabelGenerationParameters,
            file_name: str
    ) -> int:
        """
        Render the current scene and check the label for the number of pixels.
        Assume everything is set up correctly beforehand.
        Returns how many new images were generated.
        """
        bpy.ops.render.render(write_still=False, animation=False)

        rendered_image_path = os.path.join(parameters.base_output_directory, f'image-{bpy.context.scene.frame_current}.png')
        rendered_label_path = os.path.join(parameters.base_output_directory, f'label-{bpy.context.scene.frame_current}.png')

        # Check if the label is 'empty'
        label = cv2.imread(rendered_label_path)
        if np.sum(label) < parameters.min_active_pixels:
            return 0

        # All is okay, we split into patches or move and rename the files
        if parameters.num_patches > 1:
            img = cv2.imread(rendered_image_path)
            return generate_patches(parameters, img, label, file_name)

        shutil.move(rendered_image_path, os.path.join(parameters.image_output_directory, file_name + '.png'))
        shutil.move(rendered_label_path, os.path.join(parameters.label_output_directory, file_name + '.png'))
        return 1
