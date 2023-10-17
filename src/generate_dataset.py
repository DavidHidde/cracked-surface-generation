import pickle

import bpy

from crack_generation.models import CrackParameters
from dataset_generation.crack_generator import CrackGenerator
from dataset_generation.operations import SceneClearer, MaterialLoader
from dataset_generation.scene_generator import SceneGenerator
from dataset_generation.surface_map_generator import SurfaceMapGenerator


def main():
    """
    Main entrypoint
    """
    # Reset the scene
    scene_clearer = SceneClearer()
    scene_clearer()

    parameters = CrackParameters(
        20.,
        5.,
        300,
        0.1,
        0,
        5,
        5,
        1.,
        0.2,
        0.1,
        0.1
    )
    materials = (MaterialLoader())()

    # Identify base wall
    if 'Wall' in bpy.data.objects:
        wall = bpy.data.objects['Wall']
        wall = wall.evaluated_get(bpy.context.evaluated_depsgraph_get())
        surface_generator = SurfaceMapGenerator()
        surface = surface_generator([wall])
        crack_generator = CrackGenerator()
        crack = crack_generator(parameters, surface, 'crack.obj')
        scene_generator = SceneGenerator()
        scene_generator(wall, bpy.data.objects['Camera'], crack, materials)

        with open('surface.dump', 'wb') as surface_file:
            pickle.dump(surface, surface_file)


# Main entrypoint
if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Something caused the script to crash')
        print(error)
