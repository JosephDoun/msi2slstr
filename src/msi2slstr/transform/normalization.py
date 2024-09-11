from numpy import ndarray
from numpy import array as _array


class Normalizer:
    """
    Class to normalize given array according to the normalizer state, in a
    channelwise manner.

    :math:`Array_normal = (Array - OFFSET) / (SCALE + e)`

    :param offset: A tuple of floats with the per channel value by which to offset
        the provided array's value range. Has to be broadcastable to the array's shape.
    :type offset: tuple[float]
    :param scale: A tuple of floats with the per channel value to scale the array's 
        value range. Has to be broadcastable to the array's shape.
    :type scale: tuple[int]
    """

    def __init__(self, offset: tuple[float], scale: tuple[float]) -> None:
        self.offset = _array(offset).reshape(1, len(offset), 1, 1)
        self.scale = _array(scale).reshape(1, len(scale), 1, 1)
        self.e = 1e-15

    def __call__(self, array: ndarray) -> ndarray:
        return (array - self.offset) / (self.scale - self.offset + self.e)

    def reverse(self, array: ndarray) -> ndarray:
        return array * (self.scale - self.offset + self.e) + self.offset
