from dataclasses import dataclass
from .dataclasses import SAFE
from .gdalutils import build_unified_dataset



@dataclass
class Sentinel2L1C(SAFE):
    def __post_init__(self):
        super().__post_init__()
        self.dataset = build_unified_dataset(*map(lambda x: x.dataset, self.bands))


