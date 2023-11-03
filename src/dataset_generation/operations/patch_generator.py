import cv2
import numpy as np

MIN_ACTIVE_PIXELS = 0


class PatchGenerator:
    """
    Class aimed at splitting the output file into multiple patches containing labels
    """

    def __call__(self, file_name: str, patches_per_dimension: int) -> int:
        """
        Load the image and labels, divide into patches and save the patches with pixels in it.
        Returns how many patches were generated.
        """
        idx = int(file_name[6:])
        count = 0
        image = cv2.imread(file_name + '.png')
        label = cv2.imread(file_name + '-label.png')

        step_size = image.shape[0] // patches_per_dimension
        for row_idx in range(patches_per_dimension):
            start_y, end_y = row_idx * step_size, (row_idx + 1) * step_size
            for col_idx in range(patches_per_dimension):
                start_x, end_x = col_idx * step_size, (col_idx + 1) * step_size
                label_patch = label[start_y:end_y, start_x:end_x]
    
                if np.sum(label_patch) > MIN_ACTIVE_PIXELS:
                    img_patch = image[start_y:end_y, start_x:end_x]
                    cv2.imwrite(f'crack-{idx + count}.png', img_patch)
                    cv2.imwrite(f'crack-{idx + count}-label.png', label_patch)
                    count += 1
        return count
