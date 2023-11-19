import cv2
import numpy as np

from dataset_generation.empty_label_error import EmptyLabelError
from dataset_generation.models.parameters import LabelGenerationParameters


class LabelThresholder:
    """
    Class aimed at thresholding label images.
    """

    def __call__(self, label_file_path: str, parameters: LabelGenerationParameters) -> None:
        """
        Load and threshold the image.
        """
        image = cv2.imread(label_file_path)
        thresholded_image = cv2.inRange(
            image,
            parameters.min_rgb_value,
            parameters.max_rgb_value
        )

        if np.sum(thresholded_image) < parameters.min_active_pixels:
            raise EmptyLabelError

        cv2.imwrite(label_file_path, thresholded_image)
