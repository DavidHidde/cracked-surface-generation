import cv2
import numpy as np

from dataset_generation.empty_label_error import EmptyLabelError
from dataset_generation.models.parameters import LabelGenerationParameters


class LabelGenerator:
    """
    Class aimed at generating label masks.
    """

    def __call__(self, img_file_path: str, label_file_path: str, parameters: LabelGenerationParameters) -> None:
        """
        Load the image and label and generate the label by thresholding the diff.

        This is achieved by iteratively thresholding the diff until the number of
        connected components changes or we reach the max threshold.
        """
        image = cv2.imread(img_file_path)
        label = cv2.imread(label_file_path)
        diff = cv2.cvtColor(cv2.subtract(label, image), cv2.COLOR_RGB2GRAY)

        # Empty diff means definitely a no go
        if np.sum(diff) < parameters.min_active_pixels:
            raise EmptyLabelError

        # Iteratively searching the best threshold
        threshold = parameters.min_threshold
        _, thresholded = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
        base_num_components, _ = cv2.connectedComponentsWithAlgorithm(
            thresholded,
            8,
            cv2.CV_32S,
            -1  # Default algorithm
        )
        num_components = base_num_components
        while num_components == base_num_components and threshold <= parameters.max_threshold:
            threshold += parameters.threshold_increments
            _, thresholded = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
            num_components, _ = cv2.connectedComponentsWithAlgorithm(
                thresholded,
                8,
                cv2.CV_32S,
                -1  # Default algorithm
            )

        # Threshold found, now we just save
        threshold = threshold if num_components == base_num_components else threshold - parameters.threshold_increments
        _, thresholded_label = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
        cv2.imwrite(label_file_path, thresholded_label)

        # If the label is almost empty we don't want it
        if np.sum(thresholded_label) < parameters.min_active_pixels:
            raise EmptyLabelError
