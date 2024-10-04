"""Evaluation metrics definition.
"""
from numpy import ndarray
from numpy import sum, multiply
from numpy import sqrt

from ..transform.normalization import Standardizer


class r(ndarray):
    """
    Pearson product-moment correlation coefficient.

    .. math::
        \\begin{aligned}
            ...
        \\end{aligned}
    """
    _C = 1e-10

    def __new__(cls, x: ndarray, y: ndarray) -> "r":
        xnorm = x - x.mean((-1, -2), keepdims=True)
        ynorm = y - y.mean((-1, -2), keepdims=True)
        numer = sum(xnorm * ynorm, axis=(-1, -2), keepdims=True)
        denom = sqrt(multiply(sum(xnorm * xnorm, axis=(-1, -2),
                                  keepdims=True),
                              sum(ynorm * ynorm, axis=(-1, -2),
                                  keepdims=True)))
        result = numer / (denom + cls._C)
        return result.view(cls).reshape(result.shape[0], -1)


class srmse(ndarray):
    """
    Standardized RMSE.

    .. math::
        \\begin{aligned}
            ...
        \\end{aligned}
    """
    standard: Standardizer = Standardizer((-1, -2))

    def __new__(cls, x: ndarray, y: ndarray,
                dims: tuple[int] = (-1, -2)) -> "srmse":

        x = cls.standard(x)
        y = cls.standard(y)
        result = sqrt((x - y) ** 2).mean(axis=dims)
        return result.view(cls)


class ssim(ndarray):
    """
    Global SSIM. Collapses elements along :attr:`dims` of the provided arrays
    to calculate the metric for the elements that remain. Defaults to a
    per-channel computation.

    :param x: First array to use in the computation of SSIM.
    :type x: `ndarray`
    :param y: Second array to use in the computation of SSIM.
    :type y: `ndarray`
    :param dims: Tuple of dimensions to collapse, defaults to (-1, -2).
    :type dims: tuple[int] or None, optional

    .. math::

        \\begin{aligned}
            l = \\frac{2 \\bar{x} \\bar{y} + \\epsilon}
            {\\bar{x} ^ 2 + \\bar{y} ^ 2 + \\epsilon },\\quad&
            c = \\frac{2 \\sigma_{x} \\sigma_{y} + \\epsilon}
            {\\sigma_{x} ^ 2 + \\sigma_{y} ^ 2 + \\epsilon },\\quad
            s = \\frac{\\overline{(x - \\bar{x}) (y - \\bar{y})} + \\epsilon}
            {\\sigma_{x} \\sigma_{y} + \\epsilon}

            \\newline
            \\newline
            SSIM& = l \\times c \\times s,\\quad SSIM \\in [0, 1]&
        \\end{aligned}

    """
    _C = 1e-10

    def __new__(cls, x: ndarray, y: ndarray,
                dims: tuple[int] = (-1, -2)) -> "ssim":

        mx = x.mean(axis=dims, keepdims=True)
        my = y.mean(axis=dims, keepdims=True)
        sx = x. std(axis=dims, keepdims=True)
        sy = y. std(axis=dims, keepdims=True)
        xnorm = x - mx
        ynorm = y - my
        sxy = (xnorm * ynorm).mean(axis=dims, keepdims=True)
        l = (2 * mx * my + cls._C) / (mx ** 2 + my ** 2 + cls._C)
        c = (2 * sx * sy + cls._C) / (sx ** 2 + sy ** 2 + cls._C)
        s = (sxy + cls._C) / (sx * sy + cls._C)
        return (l.clip(0) *
                c.clip(0) *
                s.clip(0)).prod((-1, -2)).view(cls)
