from .abc import Metadata
from ..evaluation.scene import Evaluate

from numpy import ndarray


class FusionQualityMetadata(Metadata):
    """
    Sets the fusion quality metadata domain.

    .. automethod:: __call__
    """
    def __init__(self) -> None:
        self.__ev = Evaluate()

    @property
    def domain(self):
        return ""

    @property
    def content(self):
        return self.__ev.get_stats()

    def evaluate(self, x: ndarray, y: ndarray):
        self.__ev(x, y)
