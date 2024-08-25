
from typing import Any

from datetime import datetime
from xml.etree.ElementTree import ElementTree, Element
from dataclasses import dataclass, field
from osgeo.gdal import Open, Dataset
from os.path import isdir, join, exists, isfile, sep, split
from os import PathLike

from .gdalutils import load_unscaled_S3_data


class InconsistentFileType(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


@dataclass
class Pathlike(PathLike):
    def __str__(self) -> str:
        return self.path
    
    def __post_init__(self):
        self.path = str(self.path)
        assert isinstance(self.path, str)
        assert exists(self.path), f"{self} does not exist."

    def __fspath__(self) -> Any:
        return self.path


@dataclass
class File(Pathlike):
    path: str
    
    def __post_init__(self):
        super().__post_init__()
        assert isfile(self.path), f"{self.path} is not a file."

@dataclass
class Dir(Pathlike):
    path: str

    def __post_init__(self):
        if self.path.endswith(sep): self.path = self.path[:-1]
        assert isdir(self.path), f"{self} is not a directory."


@dataclass
class XML(File, ElementTree):
    root: Element = field(init=False)
    def __post_init__(self):
        super().__post_init__()
        self.parse(self.path)
        self.root = self.getroot()

    def __getitem__(self, index: int):
        return self.root[index]


@dataclass
class Image(File):
    dataset: Dataset = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.dataset = Open(self.path)


@dataclass
class Archive(Pathlike):
    path: Dir


@dataclass
class NETCDFSubDataset:

    """
    Class encapsulating NETCDF subdatasets that are normally
    scaled and offset for efficiency.
    """

    path: str = field(init=True)
    dataset: Dataset = field(init=False)
    name: str = field(init=False)
    scale: float = field(init=False, default=1., repr=False)
    offset: float = field(init=False, default=.0, repr=False)
    metadata: dict = field(init=False, repr=False)
    

    def __post_init__(self):
        # Assert direct invocation of NETCDF driver.
        assert self.path.startswith("NETCDF:"),\
            "NETCDF:\"<path-to-file>\":<subdataset-name> format expected."

        self.dataset = Open(self.path)
        assert self.dataset,\
            "Incorrect path to NETCDF subdataset:\n"\
            "NETCDF:\"<path-to-file>\":<subdataset-name> format expected."
        
        self.name = self.path.split(":")[-1]
        self.metadata = self.dataset.GetMetadata()
        self.scale = float(self.metadata.get(f"{self.name}#scale_factor"))
        self.offset = float(self.metadata.get(f"{self.name}#add_offset"))
        
        

