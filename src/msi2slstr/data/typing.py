from osgeo.gdal import Dataset
from typing import Protocol


class NETCDFSubDataset(Protocol):
    dataset: Dataset
    scale: float
    offset: float

