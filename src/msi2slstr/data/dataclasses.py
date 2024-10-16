"""
Definition of generic dataclasses and data models.
"""

from typing import Any
# from datetime import datetime
from xml.etree.ElementTree import ElementTree, Element
from dataclasses import dataclass, field
from osgeo.gdal import Open, Dataset
from os.path import isdir, join, exists, isfile, dirname
from os import PathLike as _PathLike

from .gdalutils import load_unscaled_S3_data


class InconsistentFileType(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


@dataclass
class Pathlike(_PathLike):
    def __str__(self) -> str:
        return self.path

    def __post_init__(self):
        self.path = str(self.path).rstrip("/")
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
        super().__post_init__()
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
class NETCDFSubDatasetPath:
    path: str = field()
    file_path: File = field(init=False)
    subdataset_name: str = field(init=False)

    def __post_init__(self):
        try:
            _, file_path, self.subdataset_name = self.path.split(":")
            self.file_path = File(file_path.strip('"'))
        except Exception:
            raise Exception(
                f"'{self.path}' does not point to a valid NETCDF subdataset.")


@dataclass
class NETCDFSubDataset:
    """
    Dataclass encapsulating NETCDF subdatasets that are normally
    scaled and offset for efficiency.
    """

    path: NETCDFSubDatasetPath = field(init=True)
    dataset: Dataset = field(init=False)
    name: str = field(init=False)
    scale: float = field(init=False, default=1., repr=False)
    offset: float = field(init=False, default=.0, repr=False)
    metadata: dict = field(init=False, repr=False)

    def __post_init__(self):
        self.__load_data__()

        # Get SEN3 path.
        p = dirname(self.path.file_path)

        template = 'NETCDF:"{path}":{subdataset}'.format

        # Load corresponding grids.
        self.elevation = NETCDFGeodetic(
            template(path=join(p, f"geodetic_{self.__grid__}.nc"),
                     subdataset=f'elevation_{self.__grid__}')
        )

        self.longitude = NETCDFGeodetic(
            template(path=join(p, f"geodetic_{self.__grid__}.nc"),
                     subdataset=f'longitude_{self.__grid__}')
        )

        self.latitude = NETCDFGeodetic(
            template(path=join(p, f"geodetic_{self.__grid__}.nc"),
                     subdataset=f'latitude_{self.__grid__}')
        )

        load_unscaled_S3_data(self.longitude,
                              self.latitude,
                              self.elevation)

    def __load_data__(self):
        # Assert direct invocation of NETCDF driver
        # to extract variable.
        self.path = NETCDFSubDatasetPath(self.path)
        self.dataset = Open(self.path.path)

        assert self.dataset, \
            f"{self.path} expected to be in:\n"\
            "NETCDF:\"<path-to-file>\":<subdataset-name> format."

        self.name = self.path.subdataset_name
        self.metadata = self.dataset.GetMetadata()
        self.scale = float(self.metadata.get(f"{self.name}#scale_factor"))
        self.offset = float(self.metadata.get(f"{self.name}#add_offset"))

    @property
    def __grid__(self):
        """
        Extract the correct grid name from the main filepath.
        """
        #                               gets `grid.nc`-> gets `grid`
        return self.path.file_path.path.split("_")[-1].split(".")[0]


# Not needed TODO
@dataclass
class NETCDFGeodetic(NETCDFSubDataset):
    def __post_init__(self):
        self.__load_data__()


@dataclass
class DataReader:
    """
    Base class that defines :meth:`__getitem__` for reading image data.
    """

    dataset: Dataset

    def __getitem__(self, coords: tuple[int, int, int, int]):
        return self.dataset.ReadAsArray(*coords)
