from dataclasses import dataclass

import numpy as np


@dataclass
class CrackPath:
    """
    Data class describing a crack path consisting of an uncentered top and bottom line
    """
    top_line: np.array
    bot_line: np.array
