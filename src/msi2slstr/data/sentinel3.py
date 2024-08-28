from dataclasses import dataclass, field
from .dataclasses import NETCDFSubDataset, Archive, File, XML, join, split
from .gdalutils import load_unscaled_S3_data
from .gdalutils import geodetics_to_gcps, execute_geolocation
from .gdalutils import build_unified_dataset
from .gdalutils import Dataset

from .vrt_geolocation import set_geolocation_domain


@dataclass
class SEN3Bands:

    bands: tuple[Dataset]
    
    def __post_init__(self):
        set_geolocation_domain(*self.bands)
        load_unscaled_S3_data(*self.bands)
        execute_geolocation(*self.bands)

    def __iter__(self):
        return (b for b in self.bands)
    
    def __getitem__(self, index: int | slice):
        return self.bands[index]


@dataclass
class SEN3(Archive):
    """
    Dataclass encapsulating a `.SEN3` archive.

    `geodetic` files contain georeference information:    geotransform: tuple[float] = field(default=None)

        `an` grid is the most detailed addressing optical bands.
        `in` grid is half resolution addressing thermal bands.
        `fn` grid is identical to `in` apart from slight offset.

    `geometry` files contain solar angles information.
    """
    
    xfdumanifest: XML = field(init=False)

    def __post_init__(self):
        """
        Needs to build a VRT with all bands properly georeferenced.

        We can probably get away with only using the `an` grid to
        build a common geotransformation.

        # TODO : Evaluate case
        """
        super().__post_init__()
        self.xfdumanifest = XML(join(self, "xfdumanifest.xml"))

        self.data_files = [
            # Index 2 returns the `dataObject` section.
            File(join(self, e[0][0].get("href"))) for e in self.xfdumanifest[2]
            ]


@dataclass
class Sentinel3RBT(SEN3):
    __bnames = ("S1_radiance_an", "S2_radiance_an",
                "S3_radiance_an", "S4_radiance_an",
                "S5_radiance_an", "S6_radiance_an",
                "S7_BT_in", "S8_BT_in", "S9_BT_in",
                "F1_BT_fn", "F2_BT_in")
    
    
    dataset: Dataset = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        # Create array of booleans for filtering band files.
        # e.g. If path contains one of the band names.
        condition = lambda x: any([x.path.endswith(f"{b}.nc") for b in self.__bnames])
        
        # Return the index of the matching band to force tuple-defined order.
        sorting = lambda x: [self.__bnames.index(band) for band in self.__bnames if band in x.path][0]
        
        _band_files = list(filter(condition, self.data_files))
        _band_files.sort(key=sorting)
        
        assert len(_band_files) == len(self.__bnames), "Unexpected number of bands."
                
        subdatasetname = lambda p: split(p)[-1].split(".")[-2]
        
        bands = SEN3Bands(tuple(
            NETCDFSubDataset(f'NETCDF:"{p}":{subdatasetname(p)}')
            for p in _band_files
        ))

        self.dataset = build_unified_dataset(*map(lambda x: x.dataset, bands))
        
        del bands
        

@dataclass
class Sentinel3LST(SEN3):
    ...


@dataclass
class Sentinel3Collection:
    ...
    