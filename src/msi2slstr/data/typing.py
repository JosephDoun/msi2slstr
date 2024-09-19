"""
Helper module for avoiding circular imports during annotations.
"""

from osgeo.gdal import Dataset
from typing import Protocol


class NETCDFSubDataset(Protocol):
    """
    Abstract class for NETCDFSubDataset static type checking.
    """
    dataset: Dataset
    name: str
    scale: float
    offset: float


class Sentinel2L1C(Protocol):
    """
    Abstract class for Sentinel2L1C static type checking.
    """
    dataset: Dataset


class Sentinel3RBT(Protocol):
    """
    Abstract class for Sentinel3RBT static type checking.
    """
    dataset: Dataset


class Sentinel3SLSTR(Protocol):
    """
    Abstract class for Sentinel3SLSTR static type checking.
    """
    dataset: Dataset
