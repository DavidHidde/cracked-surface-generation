import argparse
import dataclasses
import pickle

from tqdm import tqdm

from crack_generation import CrackModelGenerator
from crack_generation.models import CrackParameters
from crack_generation.util import ObjFileExporter

parser = argparse.ArgumentParser(
    prog='Batch Crack model generator',
    description='Generate a batch of cracks in the current workspace'
)
parser.add_argument('--count', dest='count', type=int, required=False, default=1)

with open('resources/surface.dump', 'rb') as surface_dump:
    surface_map = pickle.load(surface_dump)

# Add parameters
for field in dataclasses.fields(CrackParameters):
    parser.add_argument(f'--{field.name}', dest=field.name, type=field.type, required=True)

# Parse args and separate count
args = parser.parse_args()
count = args.count
params = vars(args)
del params['count']

# Start export
generator = CrackModelGenerator()
exporter = ObjFileExporter()
crack_params = CrackParameters(**params)
for idx in tqdm(range(count)):
    exporter(generator(crack_params, surface_map), f'crack-{idx}.obj')
print('\nAll done exporting')
