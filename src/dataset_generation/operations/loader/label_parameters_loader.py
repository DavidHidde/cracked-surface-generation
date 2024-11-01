import os

from dataset_generation.models.parameters import LabelGenerationParameters


class LabelParametersLoader:
    """
    Class for loading the label parameters.
    """
    
    def __call__(self, label_parameters_data: dict, output_directory:str) -> LabelGenerationParameters:
        """
        Load the label parameters from a dict
        """
        threshold_data = label_parameters_data['thresholding']
        base_output_directory = output_directory if output_directory.startswith('/')\
            else os.path.join(os.getcwd(), output_directory)
        
        return LabelGenerationParameters(
            label_parameters_data['patches'],
            threshold_data['min_active_pixels'],
            threshold_data['image_threshold'],
            threshold_data['uv_threshold'],
            threshold_data['ao_threshold'],
            base_output_directory,
            os.path.join(base_output_directory, 'images'),
            os.path.join(base_output_directory, 'labels')
        )
    