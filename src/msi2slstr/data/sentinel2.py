from dataclasses import dataclass
from .dataclasses import SAFE
from osgeo.gdal import Translate, TranslateOptions, BuildVRT, BuildVRTOptions
from osgeo.gdal import Dataset



def build_unified_dataset(datasets: list[Dataset]) -> Dataset:
    options = BuildVRTOptions(resolution="highest",
                              separate=True)
    return BuildVRT("/vsimem/s2_mem_output.tif", datasets, options=options)


@dataclass
class Sentinel2L1C(SAFE):
    def __post_init__(self):
        super().__post_init__()
        self.dataset = build_unified_dataset(map(lambda x: x.ds, self.bands))


