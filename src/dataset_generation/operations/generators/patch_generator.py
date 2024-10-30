import os

import cv2
import numpy as np

from dataset_generation.models.parameters import LabelGenerationParameters


class PatchGenerator:
    """
    Class aimed at splitting the output file into multiple patches containing labels
    """

    def __call__(
            self,
            file_name: str,
            images_directory: str,
            labels_directory: str,
            parameters: LabelGenerationParameters
    ) -> int:
        """
        Load the image and labels, divide into patches and save the patches with pixels in it.
        Returns how many patches were generated.
        """
        idx = int(file_name[6:])
        count = 0
        image = cv2.imread(os.path.join(images_directory, file_name + '.png'))
        label = cv2.imread(os.path.join(labels_directory, file_name + '.png'))

        step_size = image.shape[0] // parameters.num_patches
        for row_idx in range(parameters.num_patches):
            start_y, end_y = row_idx * step_size, (row_idx + 1) * step_size
            for col_idx in range(parameters.num_patches):
                start_x, end_x = col_idx * step_size, (col_idx + 1) * step_size
                label_patch = label[start_y:end_y, start_x:end_x]
    
                if np.sum(label_patch) > parameters.min_active_pixels:
                    img_patch = image[start_y:end_y, start_x:end_x]
                    cv2.imwrite(os.path.join(images_directory, f'crack-{idx + count}.png'), img_patch)
                    cv2.imwrite(os.path.join(labels_directory, f'crack-{idx + count}.png'), label_patch)
                    count += 1
        return count
