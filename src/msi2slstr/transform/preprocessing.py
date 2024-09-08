from typing import Any
from .normalization import Normalizer, ndarray

from ..config import SEN2_MINMAX
from ..config import SEN3_MINMAX

from numpy import float32, stack


class DataPreprocessor:
    """
    Class that encapsulates the algebraic manipulations of the data prior to
    their introduction to the model's feature space.

    e.g. Nodata values handling, readjusting value ranges, etc. 
    """
    def __init__(self) -> None:
        self.sen2norm = Normalizer(*zip(*SEN2_MINMAX.values()))
        self.sen3norm = Normalizer(*zip(*SEN3_MINMAX.values()))

    def __call__(self, sen2list: list[ndarray], sen3list: list[ndarray]) -> tuple[ndarray, ndarray]:
        sen2 = stack([sen2list], 0)
        sen3 = stack([sen3list], 0)
        assert sen2.ndim == 4
        sen2.clip(0, None, sen2)
        sen3.clip(0, None, sen3)
        sen2 = self.sen2norm(sen2)
        sen3 = self.sen3norm(sen3)
        return sen2.astype(float32, copy=False), sen3.astype(float32, copy=False)
    
    def reset_value_range(self, Y_hat: ndarray):
        return self.sen3norm.reverse(Y_hat)
    