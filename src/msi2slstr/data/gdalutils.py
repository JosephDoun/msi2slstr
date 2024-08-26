from osgeo.gdal import BuildVRT, BuildVRTOptions
from osgeo.gdal import Translate, TranslateOptions
from osgeo.gdal import Warp, WarpOptions
from osgeo.gdal import Dataset, GCPsToGeoTransform, GCP
from osgeo.gdal import GDT_Float32

from numpy import ndarray
from .typing import NETCDFSubDataset


def build_unified_dataset(*datasets: Dataset) -> Dataset:
    """
    Combine an array of datasets into a Virtual dataset.

    Args
    ----
        :param datasets: A collection of gdal Dataset objects to
            combine in a virtual dataset.

    :returns: A virtual in-memory gdal.Dataset combining the inputs.
    """
    options = BuildVRTOptions(resolution="highest", separate=True)
    for dataset in datasets:
        print(dataset.GetDescription(), dataset.RasterCount, dataset.RasterXSize, dataset.RasterYSize)
        print(dataset.GetGeoTransform())

    return BuildVRT("/vsimem/mem_output.vrt", list(datasets), options=options)


def load_unscaled_S3_data(*netcdfs: NETCDFSubDataset | str) -> list[Dataset]:
    """
    Record unscaling as a preprocessing workflow
    and change to proper datatype.
    """
    
    virtual_load = []
    for netcdf in netcdfs:
        print(netcdf.name)
        options = TranslateOptions(unscale=True,
                                   format="VRT",
                                   outputType=GDT_Float32,
                                   noData=-32768,
                                   outputSRS="EPSG:4326",
                                   GCPs=netcdf.GCPs)
        ds = Translate("/vsimem/mem_out.vrt", netcdf.dataset, options=options)
        
        options = WarpOptions(dstSRS="EPSG:4326", multithread=True)
        virtual_load.append(Warp("/vsimem/projected.vrt", ds, options=options))
        
    return virtual_load


def geodetics_to_gcps(*geodetics: NETCDFSubDataset,
                      grid_dilation: int = 1) -> tuple[int]:
    """
    Return a geotransformation according to a collection of GCPs.

    Use case expects X, Y, Z to be provided in separate dataset objects
    that contain the geoinformation in arrays.
    """
    # Will fail if number of elements differs.
    longitude, latitude, elevation = geodetics
    
    # Scale of data.
    scaleX = longitude.scale
    scaleY = latitude.scale
    scaleZ = elevation.scale

    # Offset of data.
    offsetX = longitude.offset
    offsetY = latitude.offset
    offsetZ = elevation.offset

    # Dimensions of array. Assumes all 3 have equal dimensions.
    Xsize = latitude.dataset.RasterXSize
    Ysize = latitude.dataset.RasterYSize

    X: ndarray = longitude.dataset.ReadAsArray().flatten()
    Y: ndarray = latitude.dataset.ReadAsArray().flatten()
    Z: ndarray = elevation.dataset.ReadAsArray().flatten()

    GCPs = []

    for i in range(0, X.size, grid_dilation):
        z = float(min(9000, max(Z[i] * scaleZ + offsetZ, 0)))
        x = X[i] * scaleX + offsetX
        y = Y[i] * scaleY + offsetY
        print(x, y, z, i % Xsize, i // Ysize)
        print(scaleX, scaleY, scaleZ)

        # GCP constructor positional arguments:
        #         x, y, z,     pixel,       line
        gcp = GCP(x, y, z, i % Xsize, i // Ysize)
        GCPs.append(gcp)

    return GCPs


def get_bounds(dataset: Dataset) -> tuple[int]:
    """
    Use the GeoTransform and the array dimensions
    to derive the geometric bounding box of the dataset,
    expressed in Upper-Left and Bottom-Right corner coordinates.
    """
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
                        #   outputBounds=outputbounds,
                        #   outputBoundsSRS=sen2.GetSpatialRef(),
                          srcSRS=sen3.GetSpatialRef(),
                          dstSRS=sen2.GetSpatialRef())
    
    sen3_reproj = Warp("sen3_cropped_output.tif", sen3, options=options)

    options = TranslateOptions(outputBounds=outputbounds,
                               outputSRS=sen2.GetSpatialRef())
    # return Translate("sen3_cropped.tif", sen3_reproj, options=options)

