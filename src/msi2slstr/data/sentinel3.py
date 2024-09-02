from dataclasses import dataclass, field
from .dataclasses import NETCDFSubDataset, Archive, File, XML
from .dataclasses import join, split
from .gdalutils import load_unscaled_S3_data
from .gdalutils import execute_geolocation
from .gdalutils import build_unified_dataset
from .gdalutils import Dataset
from .gdalutils import set_vrt_subdataset_geolocation_domain


@dataclass
class SEN3Bands:

    bands: tuple[Dataset]
    
    def __post_init__(self):
        set_vrt_subdataset_geolocation_domain(*self.bands)
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

    `geodetic` files contain georeference information:

        `an` grid is the most detailed addressing optical bands.
        `in` grid is half resolution addressing thermal bands.
        `fn` grid is identical to `in` apart from slight offset.

    `geometry` files contain solar angles information.
    """
    
    xfdumanifest: XML = field(init=False)
    dataset: Dataset = field(init=False)

    def __post_init__(self):
        """
        Instantiates metadata XML and collects data files.
        """
        super().__post_init__()
        self.xfdumanifest = XML(join(self, "xfdumanifest.xml"))

        self.data_files = [
            # Index 2 returns the `dataObject` section where filepaths
            # are kept.
            File(join(self, e[0][0].get("href"))) for e in self.xfdumanifest[2]
            ]

        # Create array of booleans for filtering out band files.
        # e.g. If path contains one of the band names.
        condition = lambda x: any([x.path.endswith(f"{b}.nc") for b
                                   in self._bnames])
        
        # Return the index of the matching band to force tuple-defined order.
        # i.e. The order defined in class attribute `__bnames` will define
        # the order of band files and therefore the order of raster channels.
        sorting = lambda x: [self._bnames.index(band) for band
                             in self._bnames if band in x.path][0]
        
        _band_files = list(filter(condition, self.data_files))
        _band_files.sort(key=sorting)
        
        assert len(_band_files) == len(self._bnames),\
            "Unexpected number of bands."
                
        # subdatasetname = lambda p: split(p)[-1].split(".")[-2]
        
        self.bands = SEN3Bands(tuple(
            NETCDFSubDataset(f'NETCDF:"{p}":{self.subdatasetname(p)}')
            for p in _band_files
        ))
        
    def subdatasetname(self, path: File):
        raise NotImplementedError()


@dataclass
class Sentinel3RBT(SEN3):
    _bnames = ("S1_radiance_an", "S2_radiance_an",
                "S3_radiance_an", "S4_radiance_an",
                "S5_radiance_an", "S6_radiance_an",
                "S7_BT_in", "S8_BT_in", "S9_BT_in",
                "F1_BT_fn", "F2_BT_in")
    
    dataset: Dataset = field(init=False)
    
    def subdatasetname(self, path: File):
        return split(path)[-1].split(".")[-2]
        

@dataclass
class Sentinel3LST(SEN3):
    _bnames = ("LST_in",)

    def subdatasetname(self, path: File):
        return "LST"
    
    @property
    def __grid__(self):
        return "in"



@dataclass
class Sentinel3SLSTR:

    sen3rbt_path: SEN3
    sen3lst_path: SEN3
    dataset: Dataset = field(init=False)

    def __post_init__(self):
        
        RBT = Sentinel3RBT(self.sen3rbt_path)
        LST = Sentinel3LST(self.sen3lst_path)

        # Collect bands for passing to uni-dataset builder.
        bands = [*RBT.bands, *LST.bands]
        del RBT.bands, LST.bands

        self.dataset = build_unified_dataset(*map(lambda x: x.dataset, bands))
        del bands
