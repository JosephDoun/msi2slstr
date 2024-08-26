from .typing import NETCDFSubDataset


def set_geolocation_domain(*netcdfs: NETCDFSubDataset):
    """
    Create a GEOLOCATION metadata domain in VRT datasets to
    include geolocation arrays for georeferencing.
    """
    for netcdf in netcdfs:
        netcdf.dataset.SetMetadata(
            {"X_DATASET": netcdf.longitude.dataset.GetDescription(),
             "X_BAND": 1,
             "Y_DATASET": netcdf.latitude.dataset.GetDescription(),
             "Y_BAND": 1,
             "Z_DATASET": netcdf.elevation.dataset.GetDescription(),
             "Z_BAND": 1,
             "PIXEL_OFFSET": 0,
             "PIXEL_STEP": 1,
             "LINE_OFFSET": 0,
             "LINE_STEP": 1}, "GEOLOCATION")


