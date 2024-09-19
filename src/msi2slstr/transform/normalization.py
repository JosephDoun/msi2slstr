"""
Data normalization module.
"""

from numpy import ndarray
from numpy import array as _array


class Normalizer:
    """
    Class to normalize given array according to the normalizer state, always in
    a channelwise manner. i.e. Each channel (dim 1) of the array is normalized
    independently.

    .. math:: A_{\\mathrm{normal}} = \\frac{(A - offset)}
        {(scale + \\varepsilon)}

    :param offset: A tuple of floats with the per channel value by which to
        offset the provided array's value range. Has to be broadcastable to
        the array's shape.
    :type offset: tuple[float]
    :param scale: A tuple of floats with the per channel value to scale the
        array's value range. Has to be broadcastable to the array's shape.
    :type scale: tuple[int]
    :param e: A small constant added to the denominator to avoid division by 0,
        defaults to 1e-15.
    :type e: float, optional

    .. automethod:: __call__
    """

    def __init__(self, offset: tuple[float], scale: tuple[float], *,
                 e: float = 1e-15) -> None:
        self.offset = _array(offset).reshape(1, len(offset), 1, 1)
        self.scale = _array(scale).reshape(1, len(scale), 1, 1)
        self.e = e

    def __call__(self, array: ndarray) -> ndarray:
        """
        Execute normalization.

        :param array: Array to rescale according to offset and scale.
        :param type: :class:`ndarray`

        :return: Normalized array with rescaled values.
        :rtype: :class:`ndarray`
        """
        return (array - self.offset) / (self.scale + self.e)

    def reverse(self, array: ndarray) -> ndarray:
        """
        Reverse the value normalization.

        :param array: Scaled array whose values to unscale.
        :param type: :class:`ndarray`

        :return: Array with original values.
        :rtype: :class:`ndarray`
        """
        return array * (self.scale + self.e) + self.offset


class Standardizer:
    """
    Class to standardize given array in a channelwise manner.

    .. math::
        A_{\\mathrm{standard}} =
        \\frac{(A - \\bar{A})}{(\\sigma_A + \\varepsilon)}

    :param dims: A tuple of ints indicating the dimensions to collapse.
    :type dims: tuple[int], optional
    :param e: A small constant added to the denominator to avoid
        division by 0, defauts to 1e-15.
    :type e: float, optional

    .. automethod:: __call__
    """

    def __init__(self, dims: tuple[int] = None, *, e: float = 1e-15) -> None:
        self.dims = dims
        self.e = e

    def __call__(self, array: ndarray) -> ndarray:
        """
        Execute standardization.

        :param array: Array to rescale to have mean 0 and variance 1.
        :param type: :class:`ndarray`

        :return: Standardized array.
        :rtype: :class:`ndarray`
        """
        return (array - array.mean(axis=self.dims, keepdims=True)) /\
            (array.std(axis=self.dims, keepdims=True) + self.e)
