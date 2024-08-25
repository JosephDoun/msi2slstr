from osgeo.gdal import BuildVRT, BuildVRTOptions
from osgeo.gdal import Translate, TranslateOptions
from osgeo.gdal import Warp, WarpOptions
from osgeo.gdal import Dataset, GCPsToGeoTransform, GCP
from osgeo.gdal import GDT_Float32

from numpy import ndarray
from .typing import NETCDFSubDataset


def build_unified_dataset(*datasets: Dataset) -> Dataset:
    options = BuildVRTOptions(resolution="highest",
                              separate=True)
    return BuildVRT("/vsimem/mem_output.vrt", list(datasets), options=options)


def load_unscaled_S3_data(*datasets: Dataset | str) -> list[Dataset]:
    """
    Record unscaling as a preprocessing workflow
    and change to proper datatype.
    """
    options = TranslateOptions(unscale=True,
                               format="VRT",
                               outputType=GDT_Float32,
                               noData=-32768)
    virtual_load = []
    for dataset in datasets:
        virtual_load.append(Translate("/vsimem/mem_out.vrt",
                                      dataset,
                                      options=options))
    return virtual_load


def geodetics_to_geotransform(*geodetics: NETCDFSubDataset,
                              grid_dilation: int = 2) -> tuple[int]:
    """
    Return a geotransformation according to a collection of GCPs.

    Use case expects X, Y, Z to be provided in separate dataset objects
    that contain the geoinformation in arrays.
    """
    # Will fail if number of elements differs.
    latitude, longitude, elevation = geodetics
    
    # Scale of data.
    scaleX = latitude.scale
    scaleY = longitude.scale
    scaleZ = elevation.scale

    # Offset of data.
    offsetX = latitude.offset
    offsetY = longitude.offset
    offsetZ = elevation.offset

    # Dimensions of array. Assumes all 3 have equal dimensions.
    Xsize = latitude.dataset.RasterXSize
    Ysize = latitude.dataset.RasterYSize

    X: ndarray = latitude.dataset.ReadAsArray().flatten()
    Y: ndarray = longitude.dataset.ReadAsArray().flatten()
    Z: ndarray = elevation.dataset.ReadAsArray().flatten()

    GCPs = []
    
    for i in range(0, X.size, grid_dilation):
        z = float(min(9000, max(Z[i] * scaleZ, 0)))
        x = X[i] * scaleX
        y = Y[i] * scaleY
        # GCP constructor positional arguments:
        #         x, y, z,     pixel,       line
        gcp = GCP(x, y, z, i % Xsize, i // Ysize)
        GCPs.append(gcp)

    return GCPsToGeoTransform(GCPs)


def get_bounds(dataset: Dataset) -> tuple[int]:
    transform = dataset.GetGeoTransform()
    xlen = dataset.RasterXSize
    ylen = dataset.RasterYSize

    return (transform[0],
            transform[3],
            transform[0] + xlen * transform[1] + ylen * transform[2],
            transform[3] + xlen * transform[4] + ylen * transform[5])


def crop_sen3_geometry(sen2: Dataset, sen3: Dataset) -> Dataset:
    # crop_b_to_a = Translate("/vsimem/mem_output.tif")
    outputbounds = get_bounds(sen2)
    options = WarpOptions(# creationOptions=["TILED=YES",
                          #                  "BLOCKXSIZE=16",
                          #                  "BLOCKYSIZE=16"],
                          targetAlignedPixels=True,
                          xRes=500,
                          yRes=500,
                          outputBounds=outputbounds,
                          outputBoundsSRS=sen2.GetSpatialRef(),
                          srcSRS=sen3.GetSpatialRef(),
                          dstSRS=sen2.GetSpatialRef(),
                          overviewLevel=3,
                          overwrite=True)
    mem = "/vsimem/"
    sen3_cropped = Warp("sen3_cropped_output.tif", sen3, options=options)
    return sen3_cropped

