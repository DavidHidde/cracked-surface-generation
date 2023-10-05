import os
import bpy
import argparse

parser = argparse.ArgumentParser(
    prog='Batch Crack model generator',
    description='Generate a batch of cracks in the current workspace'
)


def main():
    """
    Main entrypoint
    """
    parser = argparse.ArgumentParser(
        prog='Data set generator',
        description='Generate a data set consisting of images and labels using models and Blender.'
    )
    parser.add_argument('--models', dest='models_path', type=str, required=True)
    parser.parse_args()

    model_files = [file for file in os.listdir(parser.models_path) if file.endswith('.obj')]
    print(list(model_files))
    


if __name__ == '__main__':
    main()
