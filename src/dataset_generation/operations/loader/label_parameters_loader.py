from dataset_generation.models.parameters import LabelGenerationParameters


class LabelParametersLoader:
    """
    Class for loading the label parameters.
    """
    
    def __call__(self, label_parameters_data: dict) -> LabelGenerationParameters:
        """
        Load the label parameters from a dict
        """
        threshold_data = label_parameters_data['thresholding']
        min_color = threshold_data['min_rgb_color']
        max_color = threshold_data['max_rgb_color']
        
        return LabelGenerationParameters(
            label_parameters_data['patches'],
            threshold_data['min_active_pixels'],
            (min_color['r'], min_color['g'], min_color['b']),
            (max_color['r'], max_color['g'], max_color['b'])
        )
    