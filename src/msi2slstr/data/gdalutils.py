from osgeo.gdal import BuildVRT, BuildVRTOptions
from osgeo.gdal import Translate, TranslateOptions
from osgeo.gdal import Warp, WarpOptions
from osgeo.gdal import Dataset, GCPsToGeoTransform, GCP
from osgeo.gdal import GDT_Float32

from numpy import ndarray



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


def geodetics_to_geotransform(*geodetics: Dataset) -> tuple[int]:
    """
    Return a geotransformation according to a collection of GCPs.

    Use case expects X, Y, Z to be provided in separate dataset objects
    that contain the geoinformation in arrays.
    """
    # Will fail if number of elements differs.
    X, Y, Z = geodetics
    Xsize = X.RasterXSize
    Ysize = Y.RasterYSize
    X: ndarray = X.ReadAsArray().flatten()
    Y: ndarray = Y.ReadAsArray().flatten()
    Z: ndarray = Z.ReadAsArray().flatten()
    GCPs = []
    
    # for i, (x, y, z) in enumerate(zip(X, Y, Z)):
    for i in range(0, X.size, 2):
        z = float(min(9000, max(Z[i], 0)))
        x = X[i] * 1e-6
        y = Y[i] * 1e-6
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

