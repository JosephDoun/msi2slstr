
from typing import Any

from datetime import datetime
from xml.etree.ElementTree import ElementTree, Element, parse
from dataclasses import dataclass, field
from osgeo.gdal import Open, Dataset
from os.path import isdir, join, exists, isfile, sep, split
from os import PathLike

from .gdalutils import geodetics_to_geotransform


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
    scale: float = field(init=False, default=1.)
    offset: float = field(init=False, default=.0)
    
    def __post_init__(self):
        # Assert direct invocation of NETCDF driver.
        assert self.path.startswith("NETCDF:"),\
            "NETCDF:\"<path-to-file>\":<subdataset-name> format expected."

        self.dataset = Open(self.path)
        assert self.dataset,\
            "Incorrect path to NETCDF subdataset:\n"\
            "NETCDF:\"<path-to-file>\":<subdataset-name> format expected."
        
        self.name = self.path.split(":")[-1]


@dataclass
class SAFE(Archive):
    """
    Dataclass encapsulating a .SAFE archive.
    """
    __nlength = len("S2B_MSIL1C_20231004T103809_N0509_R008_T31TDG_20231004T141941.SAFE")
    __bnames = {"B01", "B02", "B03", "B04", "B05", "B06", "B07",
                "B08", "B8A", "B09", "B10", "B11", "B12"}

    manifest: File = field(init=False)
    MTD_file: File = field(init=False)
    # datastrip: Dir = field(init=False)
    bands: list[File] = field(init=False, default_factory=list)
    product: str = field(init=False, default="")
    tile: str = field(init=False, default="")
    acquisition_time: datetime = field(init=False, default=datetime(2000, 1, 1))
    
    def __post_init__(self):
        super().__post_init__()
        SAFE_archivename = split(self.path)[-1]
        if not len(SAFE_archivename) == self.__nlength:
            raise InconsistentFileType("File does not follow naming convention.")

        self.manifest = XML(join(self, "manifest.safe"))

        __file_locations = [
            # Index 2 holds the `dataObjectSection` of the manifest.
            File(join(self, p[0][0].get("href"))) for p in self.manifest.root[2]
        ]
        
        self.MTD_file = XML(__file_locations[0])

        product_info = self.MTD_file.root[0][0]
        
        # Not required at the moment.
        # image_files = self.MTD_file.root[0][0][-1][0][0]
        # self.datastrip = Dir(join(self, "DATASTRIP"))
        
        __imgdata = filter(lambda x: "IMG_DATA" in x.path, __file_locations)

        condition = lambda x: any([x.path.endswith(f"{b}.jp2") for b in self.__bnames])

        self.bands = [Image(p) for p in filter(condition, __imgdata)]
        assert len(self.bands) == len(self.__bnames), "Wrong number of bands."


@dataclass
class SEN3(Archive):
    """
    Dataclass encapsulating a `.SEN3` archive.

    `geodetic` files contain georeference information:
        `an` grid is the most detailed addressing optical bands.
        `in` grid is half resolution addressing thermal bands.
        `fn` grid is identical to `in` apart from slight offset.

    `geometry` files contain solar angles information.
    """
    __bnames = {"S1", "S2", "S3", "S4", "S5", "S6",
                "S7", "S8", "S9", "F1", "F2"}
    
    longitude: NETCDFSubDataset = field(init=False)
    latitude: NETCDFSubDataset = field(init=False)
    elevation: NETCDFSubDataset = field(init=False)
    bands: list[Image] = field(init=False)
    geotransform: tuple[int] = field(init=False)

    def __post_init__(self):
        """
        Needs to build a VRT with all bands properly georeferenced.

        We can probably get away with only using the `an` grid to
        build a common geotransformation.

        # TODO : Evaluate case
        """
        super().__post_init__()
        # Build GeoTransform from the AN grid.
        elevation = NETCDFSubDataset(f'NETCDF:"{join(self, "geodetic_an.nc")}":elevation_an')
        longitude = NETCDFSubDataset(f'NETCDF:"{join(self, "geodetic_an.nc")}":longitude_an')
        latitude  = NETCDFSubDataset(f'NETCDF:"{join(self, "geodetic_an.nc")}":latitude_an')

        self.geotransform = geodetics_to_geotransform(longitude.dataset,
                                                      latitude.dataset,
                                                      elevation.dataset)
        # geodetic_in = join(self, "geodetic_in.nc")


