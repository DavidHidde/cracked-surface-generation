import os
import pickle

import bpy
import argparse

import numpy as np
from PIL import Image

from dataset_generation.operations import ObjImporter, SceneClearer, SurfaceMapGenerator


def main():
    """
    Main entrypoint
    """
    parser = argparse.ArgumentParser(
        prog='Data set generator',
        description='Generate a data set consisting of images and labels using models and Blender.'
    )
    parser.add_argument('--models', dest='models_path', type=str, required=True)
    args = parser.parse_args()

    # Reset the scene
    scene_clearer = SceneClearer()
    scene_clearer()

    # Identify base wall
    if 'Wall' in bpy.data.objects:
        wall = bpy.data.objects['Wall']
        wall = wall.evaluated_get(bpy.context.evaluated_depsgraph_get())
        surface_generator = SurfaceMapGenerator()
        surface = surface_generator([wall])
        with open('surface.dump', 'wb') as surface_file:
            pickle.dump(surface, surface_file)
        im = Image.fromarray(surface.surface.astype(np.uint8))
        im.convert('L')
        im.save('test.png')
        

    # model_files = [file.split(os.pathsep)[-1] for file in os.listdir(args.models_path) if file.endswith('.obj')]
    # if len(model_files) > 0:
    #     importer = ObjImporter()
    #     importer(args.models_path, model_files)


# Main entrypoint
if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Something caused the script to crash')
        print(error)
