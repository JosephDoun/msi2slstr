from arosics.geometry import GeoArray
from numpy import ndarray
from osgeo.gdal import Dataset, Band
from py_tools_ds.geo.projection import isLocal, CRS


def build_geoarray_from_dataset(dataset: Dataset) -> "GeoArray":
    return GeoArray(dataset)


class GeoArray(GeoArray):
    """
    Extented GeoArray that accepts `gdal.Dataset` objects.

    DEPRECATED

    NOTE not worth it. Reading the Sentinel-2 image with `.ReadAsArray()`
    is blocking and doubles memory usage during corregistration.
    """
    def __init__(self, path_or_array: str | ndarray | GeoArray | Dataset,
                 geotransform: tuple = None, projection: str = None,
                 bandnames: list = None, nodata: float = None,
                 basename: str = '', progress: bool = True,
                 q: bool = False) -> None:
        
        if isinstance(path_or_array, Dataset):
            geotransform = path_or_array.GetGeoTransform()
            projection = path_or_array.GetProjection()
            nodata = path_or_array.GetRasterBand(1).GetNoDataValue()
            # For some reason expects channels last.
            path_or_array = path_or_array.ReadAsArray().swapaxes(0, -1)

        super().__init__(path_or_array, geotransform, projection,
                         bandnames, nodata, basename, progress, q)
        