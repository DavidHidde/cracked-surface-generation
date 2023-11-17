from dataclasses import dataclass

from .crack_mesh import CrackMesh
from .crack_path import CrackPath
from .parameters import CrackGenerationParameters


@dataclass
class Crack:
    """
    A generated crack, consisting of its parameters, its 2D path and its mesh.
    """

    path: CrackPath
    mesh: CrackMesh
    parameters: CrackGenerationParameters
