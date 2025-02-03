import subprocess
import sys

subprocess.check_call([
    sys.executable,
    '-m',
    'pip',
    'install',
    '--no-deps',
    '-r',
    'blender_requirements.txt',
])
print(f'-- Installed dependencies in {sys.executable} --')
