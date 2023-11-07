import cv2
import numpy as np

from dataset_generation.empty_label_error import EmptyLabelError

MIN_RGB_COLOR = (75, 75, 75)
MAX_RGB_COLOR = (255, 255, 255)

MIN_ACTIVE_PIXELS = 5


class LabelThresholder:
    """
    Class aimed at thresholding label images.
    """

    def __call__(self, label_file_path: str) -> None:
        """
        Load and threshold the image.
        """
        image = cv2.imread(label_file_path)
        thresholded_image = cv2.inRange(
            image,
            MIN_RGB_COLOR,
            MAX_RGB_COLOR
        )

        if np.sum(thresholded_image) < MIN_ACTIVE_PIXELS:
            raise EmptyLabelError

        cv2.imwrite(label_file_path, thresholded_image)
