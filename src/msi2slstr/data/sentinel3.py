from dataclasses import dataclass
from .dataclasses import SEN3, NETCDFSubDataset, File, join, split
from .gdalutils import geodetics_to_geotransform



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
        self.bands = tuple(
            NETCDFSubDataset(f'NETCDF:"{p}":{subdatasetname(p)}')
            for p in _band_files
        )
        
