import bpy


def modify_material_for_cracking(material: bpy.types.Material) -> None:
    """
    Modify a material such that we can use the height map of the crack to create a crack in the wall.
    This flow relies on a couple of assumptions:
        1. Displacement is enabled for the material and for rendering.
        2. The material is setup using the standard material setup in Blender (Ctrl + Shift + T in the material editor).

    In summary, this function will try to add the following:
    1. A mix node for the diffuse texture, which mixes the standard texture with a blurred variant in the area of the
        crack to reduce artifacts.
    2. A subtract node for the displacement texture, which subtracts the crack height map from the regular displacement texture.
    """
    pass
