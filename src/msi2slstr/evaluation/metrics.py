"""Evaluation metrics definition.
"""
from numpy import ndarray
from numpy import corrcoef
from numpy import sqrt

from typing import Self


class Pearson(ndarray):
    """
    Pearson coefficient numpy implementation.
    """
    def __new__(cls, __x: ndarray, __y: ndarray) -> Self:
        coef = corrcoef(__x.flatten(), __y.flatten())
        result = coef[0, 1]
        return result.view(cls)


class SRMSE(ndarray):
    """
    Standardized RMSE.
    """
    def __new__(cls, __x: ndarray, __y: ndarray,
                dims: tuple[int]=(-1, -2)) -> Self:
        result = sqrt((__x - __y) ** 2).mean(axis=dims)
        return result.view(cls)


class SSIM(ndarray):
    """
    Global SSIM.

    .. math::
        l = ...

        c = ...

        s = ...
    """
    _C = 1e-10
    def __new__(cls, __x: ndarray, __y: ndarray,
                dims: tuple[int]=(-1, -2)) -> Self:
        mx = __x.mean(axis=dims, keepdims=True)
        my = __y.mean(axis=dims, keepdims=True)
        sx = __x. std(axis=dims, keepdims=True)
        sy = __y. std(axis=dims, keepdims=True)
        xnorm = __x - mx
        ynorm = __y - my
        sxy = (xnorm * ynorm).sum(axis=dims, keepdims=True)
        sx2 = (xnorm * xnorm).sum(axis=dims, keepdims=True)
        sy2 = (ynorm * ynorm).sum(axis=dims, keepdims=True)
        l = (2 * mx * my + cls._C) / (mx ** 2 + my ** 2 + cls._C)
        c = (2 * sx * sy + cls._C) / (sx ** 2 + sy ** 2 + cls._C)
        s = (sxy + cls._C) / sqrt(sx2 * sy2 + cls._C)
        return (l.clip(0) *
                c.clip(0) *
                s.clip(0)).prod((-1, -2, -3)).view(cls)
