import scipy
import numpy as np



class ValidAverageDownsampling:
    """
    Creates a spatially (meaning in x,y axes) coarser copy of the provided
    array by averaging the valid values.

    :param scale: The area of the spatial aggregation in number of elements (pixels.)
    :param scale: int
    """
    def __init__(self, scale: int) -> None:
        self.scale = int(scale)

    def __call__(self, array: np.ndarray) -> np.ndarray:
        shape = array.shape
        array = array.reshape(shape[0], shape[1],
                              shape[2] // self.scale,
                              self.scale,
                              shape[3] // self.scale,
                              self.scale).swapaxes(2, 1)
        _sum = array.sum((-1, -2))
        _nzero = (array > 0).sum((-1, -2))
        return _sum / (_nzero + 1e-10)
    

class NearestNeighbourUpsampling:
    def __init__(self, scale: int) -> None:
        pass

    def __call__(self, array: np.ndarray) -> np.ndarray:
        pass