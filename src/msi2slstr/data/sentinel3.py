from dataclasses import dataclass
from .dataclasses import SEN3, NETCDFSubDataset, join
from .gdalutils import geodetics_to_geotransform



@dataclass
class Sentinel3RBT(SEN3):
    def __post_init__(self):
        super().__post_init__()
        
        # Build GeoTransform from the AN grid.
        elevation = NETCDFSubDataset(f'NETCDF:"{join(self, "geodetic_an.nc")}":elevation_an')
        longitude = NETCDFSubDataset(f'NETCDF:"{join(self, "geodetic_an.nc")}":longitude_an')
        latitude  = NETCDFSubDataset(f'NETCDF:"{join(self, "geodetic_an.nc")}":latitude_an')

        self.geotransform = geodetics_to_geotransform(longitude,
                                                      latitude,
                                                      elevation)