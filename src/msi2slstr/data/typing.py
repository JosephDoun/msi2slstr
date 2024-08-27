from osgeo.gdal import Dataset
from typing import Protocol


class NETCDFSubDataset(Protocol):
    dataset: Dataset
    name: str
    scale: float
    offset: float


class Sentinel2L1C(Protocol):
    dataset: Dataset


class Sentinel3RBT(Protocol):
    dataset: Dataset
    