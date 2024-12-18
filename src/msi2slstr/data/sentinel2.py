"""
Module of Sentinel-2 related dataclasses and validation methods.
"""
from os.path import join, split
from dataclasses import dataclass, field
from datetime import datetime
from osgeo.gdal import Dataset

from .dataclasses import Archive, Image, File, XML
from .dataclasses import InconsistentFileType
from .gdalutils import build_unified_dataset

from ..config import get_sen2name_length


@dataclass
class SAFE(Archive):
    """
    Dataclass encapsulating a .SAFE archive.
    """
    __nlength = len(
        "S2B_MSIL1C_20231004T103809_N0509_R008_T31TDG_20231004T141941.SAFE")
    __bnames = ("B01", "B02", "B03", "B04", "B05", "B06", "B07",
                "B08", "B8A", "B09", "B10", "B11", "B12")

    manifest: File = field(init=False)
    MTD_file: File = field(init=False)
    # datastrip: Dir = field(init=False)
    product: str = field(init=False, default="")
    tile: str = field(init=False, default="")
    acquisition_time: datetime = field(
        init=False, default=datetime(2000, 1, 1))
    dataset: Dataset = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        SAFE_archive_name = split(self.path)[-1]

        if not len(SAFE_archive_name) == self.__nlength:
            raise InconsistentFileType(
                f"{SAFE_archive_name} File does not follow naming convention.")

        self.manifest = XML(join(self, "manifest.safe"))

        __file_locations = [
            # Index 2 holds the `dataObjectSection` of the manifest.
            File(join(self, p[0][0].get("href")))
            for p in self.manifest.root[2]
        ]

        self.MTD_file = XML(__file_locations[0])

        __imgdata = filter(lambda x: "IMG_DATA" in x.path, __file_locations)

        def condition(x): return any(
            [x.path.endswith(f"{b}.jp2") for b in self.__bnames])
        def sorting(x): return [self.__bnames.index(band)
                                for band in self.__bnames if band in x.path][0]
        bands = list(Image(p) for p in filter(condition, __imgdata))
        bands.sort(key=sorting)

        assert len(bands) == len(self.__bnames), "Wrong number of bands."

        self.dataset = build_unified_dataset(*map(lambda x: x.dataset, bands))


@dataclass
class Sentinel2L1C(SAFE):
    def __post_init__(self):
        super().__post_init__()


@dataclass
class Sen2Name:

    file_name: str
    platform: str = field(init=False)
    product: str = field(init=False)
    acquisition_date: str = field(init=False)
    a_orbit: str = field(init=False)
    r_orbit: str = field(init=False)
    tile: str = field(init=False)
    processing_date: str = field(init=False)

    def __post_init__(self):
        self.file_name = split(self.file_name)[-1]
        assert len(self.file_name) == get_sen2name_length(), \
            f"{self.file_name} has unexpected length."

        self.file_name, _ = self.file_name.split(".")
        (
            self.platform,
            self.product,
            self.acquisition_date,
            self.a_orbit,
            self.r_orbit,
            self.tile,
            self.processing_date
        ) = self.file_name.split("_")
