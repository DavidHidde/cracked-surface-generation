import os
import shutil

import bpy
import cv2
import numpy as np

from dataset_generation.empty_label_error import EmptyLabelError


class CrackRenderer:
    """
    Render operation aimed at rendering a crack and its label.
    """

    def __call__(
            self,
            crack: bpy.types.Object,
            wall: bpy.types.Object,
            min_active_pixels: int,
            base_output_directory: str,
            image_path: str,
            label_path: str,
    ) -> None:
        """
        Render the current scene and check the label for the number of pixels.
        Assume everything is set up correctly beforehand.
        """
        bpy.ops.render.render(write_still=False, animation=False)

        rendered_image_path = os.path.join(base_output_directory, f'image-{bpy.context.scene.frame_current}.png')
        rendered_label_path = os.path.join(base_output_directory, f'label-{bpy.context.scene.frame_current}.png')
        print('label path:', rendered_label_path)

        img = cv2.imread(rendered_label_path)
        if np.sum(img) < min_active_pixels:
            raise EmptyLabelError

        # All is okay, we move and rename the files
        shutil.move(rendered_image_path, image_path)
        shutil.move(rendered_label_path, label_path)
