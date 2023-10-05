import argparse
import os

import cv2

parser = argparse.ArgumentParser(
    prog='Crack path generator',
    description='Generate labels from crack images.'
)
parser.add_argument('--path', dest='path', type=str, required=False, default=None)
args = parser.parse_args()

path = args.path if args.path is not None else ''
path = os.path.join('.', path)
files = [file for file in os.listdir(path) if file.endswith('.png')]

for file in files:
    image = cv2.imread(os.path.join(path, file))
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    thresholded_image = cv2.inRange(hsv, (55, 70, 75), (80, 255, 255))

    cv2.imwrite(os.path.join(path, file[:-4] + '-label.png'), thresholded_image)
