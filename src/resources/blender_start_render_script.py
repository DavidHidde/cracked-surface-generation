import bpy
import os
import sys


SCRIPT_NAME = 'generate_dataset.py'

# Add to path
base_dir = os.path.join(os.path.dirname(bpy.data.filepath), '..')
if base_dir not in sys.path:
    sys.path.append(base_dir)

# Reload all submodules
import generate_dataset
import importlib
modules = [key for key in sys.modules.keys() if 'dataset_generation' in key or 'crack_generation' in key]
for key in modules:
    importlib.reload(sys.modules[key])

importlib.reload(generate_dataset)
generate_dataset.main()