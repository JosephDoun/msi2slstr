"""Module for the evaluation of a full satellite scene.
"""
from numpy import array, ndarray

from .metrics import ssim
from .metrics import srmse
from .metrics import r


class Evaluate:
    """
    Tracks fusion evaluation stats for entire image.

    .. automethod:: __call__
    """
    def __init__(self) -> None:
        #: Registered metrics to keep track of.
        self.metrics: list[object] = [r, srmse, ssim]

        #: Dictionary of held metrics.
        self.metric_maps: dict[str, list] = {m.__name__: []
                                             for m in self.metrics}

        self._counter = 0

    def __call__(self, x: ndarray, y: ndarray) -> None:
        """
        Executes and records all registered metrics for given batch of tiles.
        """
        for metric in self.metrics:
            # Evaluate all tiles in batch.
            metric_values = metric(x, y)

            for t_metric in metric_values:
                # Record each tile separately for the generation
                # of quality maps.
                self.metric_maps[metric.__name__].append(t_metric)

            self._counter += 1

    def __repr__(self) -> str:
        return "\n".join([f"{key}: {array(value).mean()}"
                          for key, value in self.metric_maps])

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def quality_maps(self):
        """
        Returns a 2D array per metric that maps fusion quality to the scene's
        geometry.
        """
        ...
