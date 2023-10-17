import bpy


class MaterialLoader:
    """
    Simple class loading a set of materials.
    """

    KEYWORD_BRICK = 'brick'
    KEYWORD_MORTAR = 'mortar'
    KEYWORD_FOREGROUND = 'foreground'

    BRICK_MATERIALS = [
        'Brick - red',
        'Brick - gray'
    ]
    MORTAR_MATERIALS = ['Mortar - white']
    FOREGROUND_MATERIAL = 'Marker - foreground'

    def __call__(self) -> dict[str, dict[str, bpy.types.Material]]:
        """
        Load all materials.
        """
        materials = {
            self.KEYWORD_BRICK: {},
            self.KEYWORD_MORTAR: {},
            self.KEYWORD_FOREGROUND: bpy.data.materials[self.FOREGROUND_MATERIAL]
        }

        for material_name in self.BRICK_MATERIALS:
            if material_name in bpy.data.materials:
                materials[self.KEYWORD_BRICK][material_name] = bpy.data.materials[material_name]
        for material_name in self.MORTAR_MATERIALS:
            if material_name in bpy.data.materials:
                materials[self.KEYWORD_MORTAR][material_name] = bpy.data.materials[material_name]

        return materials
