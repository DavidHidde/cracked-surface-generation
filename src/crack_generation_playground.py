from argparse import ArgumentParser

import cv2

from crack_generation import CrackGenerator, create_surface_from_image
from util import PlaygroundInterface, DEFAULT_PARAMETERS


def main():
    # Load surface file
    parameters = DEFAULT_PARAMETERS
    parser = ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the surface height map to test on.')
    filename = parser.parse_args().file
    height_map = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    surface = create_surface_from_image(height_map, 650, 150)

    ui = PlaygroundInterface(surface, parameters)
    ui.start()


if __name__ == "__main__":
    main()
