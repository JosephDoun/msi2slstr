"""
Definining preprocessor classes that encapsulate complete data preparation
workflows.
"""

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

    def __call__(self, sen2tuple: tuple[ndarray],
                 sen3tuple: tuple[ndarray]) -> tuple[ndarray, ndarray]:
        """
        Executes workflow that finalizes input data for model consumption.

        1. Constructs the batch dimension of data.
        2. Enforces minimum value as 0.
        3. Performs value normalization according to 
        `normalization.yaml` values.
        4. Casts input to `np.float32`

        :param sen2tuple: A tuple of Sentinel-2 3D patches with length 
        equal to `batch_size`
        :type sen2tuple: tuple[ndarray]
        :param sen3tuple: A tuple of Sentinel-3 3D patches with length 
        equal to `batch_size`
        :type sen3tuple: tuple[ndarray]

        :return: The 4D input arrays prepared for model consuption
        :rtype: tuple[ndarray]
        """

        # Build batch dimension.
        sen2 = stack(sen2tuple, 0)
        sen3 = stack(sen3tuple, 0)
        # Verify 0 min.
        sen2.clip(0, None, sen2)
        sen3.clip(0, None, sen3)
        # Normalize.
        sen2 = self.sen2norm(sen2)
        sen3 = self.sen3norm(sen3)
        # Cast to float32 and return.
        return sen2.astype(float32, copy=False), sen3.astype(float32, copy=False)

    def reset_value_range(self, Y_hat: ndarray):
        return self.sen3norm.reverse(Y_hat)
