from dataclasses import dataclass, field
from .dataclasses import NETCDFSubDataset, Archive, File, XML, join, split
from .gdalutils import load_unscaled_S3_data
from .gdalutils import geodetics_to_geotransform
from .gdalutils import build_unified_dataset
from .gdalutils import Dataset



@dataclass
class SEN3Bands:
    bands: tuple[Dataset] = field()

    def __post_init__(self):
        self.bands = load_unscaled_S3_data(*(x.dataset for x in self.bands))

    def __iter__(self):
        return (b for b in self.bands)
    
    def __getitem__(self, index: int | slice):
        return self.bands[index]


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
    
    bands: SEN3Bands = field(init=False)
    geotransform: tuple[int] = field(init=False)
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
    __bnames = {"S1_radiance_an", "S2_radiance_an",
                "S3_radiance_an", "S4_radiance_an",
                "S5_radiance_an", "S6_radiance_an",
                "S7_BT_in", "S8_BT_in", "S9_BT_in",
                "F1_BT_fn", "F2_BT_in"}
    
    def __post_init__(self):
        super().__post_init__()
        
        # Build GeoTransform from the AN grid.
        elevation = NETCDFSubDataset(f'NETCDF:"{join(self, "geodetic_an.nc")}":elevation_an')
        longitude = NETCDFSubDataset(f'NETCDF:"{join(self, "geodetic_an.nc")}":longitude_an')
        latitude  = NETCDFSubDataset(f'NETCDF:"{join(self, "geodetic_an.nc")}":latitude_an')

        self.geotransform = geodetics_to_geotransform(longitude,
                                                      latitude,
                                                      elevation,
                                                      grid_dilation=5)
        
        condition = lambda x: any([x.path.endswith(f"{b}.nc") for b in self.__bnames])
        _band_files = tuple(filter(condition, self.data_files))

        assert len(_band_files) == len(self.__bnames), "Unexpected number of bands."
                
        subdatasetname = lambda p: split(p)[-1].split(".")[-2]
        
        self.bands = SEN3Bands(tuple(
            NETCDFSubDataset(f'NETCDF:"{p}":{subdatasetname(p)}')
            for p in _band_files
        ))

        self.dataset = build_unified_dataset(*self.bands)
        
