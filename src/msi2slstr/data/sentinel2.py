from dataclasses import dataclass, field
from datetime import datetime
from .dataclasses import Archive, Image, File, XML 
from .dataclasses import InconsistentFileType, join, split
from .gdalutils import build_unified_dataset


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

        bands = tuple(Image(p) for p in filter(condition, __imgdata))
        assert len(bands) == len(self.__bnames), "Wrong number of bands."

        self.dataset = build_unified_dataset(*map(lambda x: x.dataset, bands))


@dataclass
class Sentinel2L1C(SAFE):
    def __post_init__(self):
        super().__post_init__()


