import argparse

import bpy
import os
import sys

# Parse arguments -- from the background_job.py template
argv = sys.argv
if "--" not in argv:
    argv = []  # as if no args are passed
else:
    argv = argv[argv.index("--") + 1:]  # get all args after "--"

# When --help or no args are given, print this help
usage_text = (
    "Run blender in background mode with this script:"
    "  blender -b -P " + __file__ + " -- --cycles-device <device> [options]"
)
parser = argparse.ArgumentParser(description=usage_text)

parser.add_argument(
    "-s", "--size", dest="size", type=int, required=False, default=1,
    help="The dataset size.",
)
parser.add_argument(
    "-r", "--retries", dest="max_retries", type=int, required=False, default=5,
    help="The maximum number of retries before the rendering should stop.",
)
parser.add_argument(
    "-c", "--config", dest="config", type=str, required=False, default='configuration.yaml',
    help="The path to the configuration file.",
)
parser.add_argument(
    "--cycles-device", dest="cycles_device", type=str, required=False, default='CPU',
    help="The rendering device for Cycles to use.",
)
args = parser.parse_args(argv)  # In this example we won't use the args

# Add to path
base_dir = os.path.join(os.path.dirname(bpy.data.filepath), '..')
if base_dir not in sys.path:
    sys.path.append(base_dir)

# Reload all submodules - useful when running script from Blender itself
import generate_dataset
import importlib
modules = [key for key in sys.modules.keys() if 'dataset_generation' in key or 'crack_generation' in key]
for key in modules:
    importlib.reload(sys.modules[key])

importlib.reload(generate_dataset)
generate_dataset.run(args.size, args.max_retries, args.config)
