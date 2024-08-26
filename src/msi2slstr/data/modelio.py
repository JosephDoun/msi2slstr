
from dataclasses import dataclass
from .sentinel2 import Sentinel2L1C
from .sentinel3 import Sentinel3RBT
from .gdalutils import crop_sen3_geometry


@dataclass
class ModelInput:
    sen2l1c: Sentinel2L1C
    sen3rbt: Sentinel3RBT

    def __post_init__(self):
        assert isinstance(self.sen2l1c, Sentinel2L1C)
        assert isinstance(self.sen3rbt, Sentinel3RBT)
        self.sen3rbt.dataset = crop_sen3_geometry(self.sen2l1c.dataset,
                                                  self.sen3rbt.dataset)