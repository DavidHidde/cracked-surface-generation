import bpy


class MaterialLoader:
    """
    Simple class loading a set of materials.
    """

    KEYWORD_BRICK = 'brick'
    KEYWORD_MORTAR = 'mortar'
    KEYWORD_CRACK = 'crack'

    BRICK_MATERIALS = [
        'Brick - red',
        'Brick - gray'
    ]
    MORTAR_MATERIALS = ['Mortar - white']
    CRACK_MATERIALS = ['Crack marker']

    def __call__(self) -> dict[str, dict[str, bpy.types.Material]]:
        materials = {
            self.KEYWORD_BRICK: {},
            self.KEYWORD_MORTAR: {},
            self.KEYWORD_CRACK: {}
        }

        for material_name in self.BRICK_MATERIALS:
            if material_name in bpy.data.materials:
                materials[self.KEYWORD_BRICK][material_name] = bpy.data.materials[material_name]
        for material_name in self.MORTAR_MATERIALS:
            if material_name in bpy.data.materials:
                materials[self.KEYWORD_MORTAR][material_name] = bpy.data.materials[material_name]
        for material_name in self.CRACK_MATERIALS:
            if material_name in bpy.data.materials:
                materials[self.KEYWORD_CRACK][material_name] = bpy.data.materials[material_name]

        return materials
