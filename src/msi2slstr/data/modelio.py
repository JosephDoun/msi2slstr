from dataclasses import dataclass, field
from .sentinel2 import Sentinel2L1C
from .sentinel3 import Sentinel3SLSTR, Sentinel3RBT, Sentinel3LST
from .gdalutils import crop_sen3_geometry
from .gdalutils import trim_sen3_geometry
from .gdalutils import trim_sen2_geometry

from ..align.corregistration import corregister_datasets


@dataclass
class ModelInput:
    sen2: Sentinel2L1C = field()
    sen3: Sentinel3SLSTR = field(init=False)
    sen3rbt: Sentinel3RBT = field(repr=False)
    sen3lst: Sentinel3LST = field(repr=False)

    def __post_init__(self):
        self.sen2 = Sentinel2L1C(self.sen2)
        self.sen3 = Sentinel3SLSTR(self.sen3rbt, self.sen3lst)
        crop_sen3_geometry(self.sen2, self.sen3)
        corregister_datasets(self.sen2, self.sen3)
        trim_sen3_geometry(self.sen3)
        trim_sen2_geometry(self.sen2, self.sen3)
        
        del self.sen3rbt, self.sen3lst
