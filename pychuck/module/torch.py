import numpy as np

import torch
from pychuck.module.base import _ChuckBufferInOutModule


class Rave(_ChuckBufferInOutModule):
    def __init__(self, model_path: str = None):
        super().__init__()
        self.model = None
        if model_path:
            self.load(model_path)

    def load(self, model_path: str):
        self.model = torch.jit.load(model_path).eval()
        self.size = 2048

    def compute(self, input: np.ndarray):
        with torch.no_grad():
            return self.model.forward(
                torch.from_numpy(
                    input.reshape(1, 1, -1)
                )
            ).detach().numpy()[0][0]
