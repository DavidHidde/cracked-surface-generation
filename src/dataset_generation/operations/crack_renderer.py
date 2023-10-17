import bpy

from . import MaterialLoader
from .label_thresholder import LabelThresholder


class CrackRenderer:
    """
    Render operation aimed at rendering a crack and it's label.
    """
    
    __label_thresholder: LabelThresholder = LabelThresholder()
    
    def __call__(
            self,
            crack_marker: bpy.types.Object,
            output_name: str
    ) -> None:
        """
        Render the current scene with and without the crack marker to a specified
        file name. This name should be without the image extension.
        """
        # First pass: Render without marker
        crack_marker.hide_render = True
        bpy.context.scene.render.filepath = f'{output_name}.png'
        bpy.ops.render.render(write_still=True)
        
        # Second pass: Render with marker
        crack_marker.hide_render = False
        bpy.context.scene.render.filepath = f'{output_name}-label.png'
        
        # Turn off HDRI
        mix_node = bpy.data.worlds['World'].node_tree.nodes['Mix']
        mix_node.inputs[0].default_value = 1.
        
        bpy.ops.render.render(write_still=True)
        
        # Turn HDRI back on
        mix_node.inputs[0].default_value = 0.
        
        # Threshold the image
        self.__label_thresholder(f'{output_name}-label.png')
