import cv2

MIN_RGB_COLOR = (120, 120, 120)
MAX_RGB_COLOR = (255, 255, 255)


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
        cv2.imwrite(label_file_path, thresholded_image)
