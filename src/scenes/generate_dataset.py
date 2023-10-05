import os

import bpy
import argparse


def clear_scene() -> None:
    """
    Remove all objects from the scenes
    """
    for bpy_data_iter in (
            bpy.data.collections,
            bpy.data.objects,
            bpy.data.meshes,
            bpy.data.lights,
            bpy.data.cameras,
    ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data, do_unlink=True)


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

    model_files = [file for file in os.listdir(args.models_path) if file.endswith('.obj')]

    clear_scene()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Something caused the script to crash')
        print(error)
