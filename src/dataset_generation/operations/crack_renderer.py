import os

import bpy

from dataset_generation.operations.generators.label_generator import LabelGenerator
from dataset_generation.models.parameters import LabelGenerationParameters, SceneParameters


class CrackRenderer:
    """
    Render operation aimed at rendering a crack and it's label.
    """

    __label_generator: LabelGenerator = LabelGenerator()
    
    def __call__(
            self,
            crack: bpy.types.Object,
            wall: bpy.types.Object,
            label_parameters: LabelGenerationParameters,
            scene_parameters: SceneParameters,
            images_directory: str,
            labels_directory: str,
    ) -> None:
        """
        Render the current scene with and without the crack marker to a specified
        file name. This name should be without the image extension.
        """
        output_dir = os.path.dirname(os.path.join(bpy.data.filepath))
        base_file_path = os.path.join(output_dir, f'{os.path.join(images_directory, scene_parameters.output_file_name)}.png')
        label_file_path = os.path.join(output_dir, f'{os.path.join(labels_directory, scene_parameters.output_file_name)}.png')

        # First pass: Render with marker
        old_aa_filter = bpy.context.scene.cycles.filter_width
        bpy.context.scene.cycles.filter_width = 0.01

        wall.data.materials[1] = scene_parameters.crack_material
        bpy.context.scene.render.filepath = label_file_path
        bpy.ops.render.render(write_still=True)
        
        # Second pass: Render the crack
        bpy.context.scene.cycles.filter_width = old_aa_filter
        wall.data.materials[1] = scene_parameters.wall_material
        bpy.context.scene.render.filepath = base_file_path
        bpy.ops.render.render(write_still=True)
        
        # Generate the label using the diff
        self.__label_generator(base_file_path, label_file_path, label_parameters)
