from osgeo.gdal import Dataset
from typing import Protocol


class NETCDFSubDataset(Protocol):
    dataset: Dataset
    name: str
    scale: float
    offset: float

