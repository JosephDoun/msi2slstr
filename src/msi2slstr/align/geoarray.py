from arosics.geometry import GeoArray
from osgeo.gdal import Dataset


def build_geoarray_from_dataset(dataset: Dataset) -> GeoArray:
    ...