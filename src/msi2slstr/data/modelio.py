from dataclasses import dataclass
from .sentinel2 import Sentinel2L1C
from .sentinel3 import Sentinel3RBT
from .gdalutils import crop_sen3_geometry

from ..align.corregistration import corregister_datasets


@dataclass
class ModelInput:
    sen2l1c: Sentinel2L1C
    sen3rbt: Sentinel3RBT

    def __post_init__(self):
        self.sen2l1c = Sentinel2L1C(self.sen2l1c)
        self.sen3rbt = Sentinel3RBT(self.sen3rbt)
        crop_sen3_geometry(self.sen2l1c, self.sen3rbt)
        corregister_datasets(self.sen2l1c, self.sen3rbt)

