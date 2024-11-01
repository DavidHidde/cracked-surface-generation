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
        
        return LabelGenerationParameters(
            label_parameters_data['patches'],
            threshold_data['min_active_pixels'],
            threshold_data['image_threshold'],
            threshold_data['uv_threshold'],
            threshold_data['ao_threshold'],
        )
    