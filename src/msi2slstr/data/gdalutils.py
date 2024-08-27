from osgeo.gdal import BuildVRT, BuildVRTOptions
from osgeo.gdal import Translate, TranslateOptions
from osgeo.gdal import Warp, WarpOptions
from osgeo.gdal import Dataset, GCP
from osgeo.gdal import GDT_Float32, TermProgress
from osgeo.gdal import Open, OpenEx, ReadDir
from osgeo.gdal import VSIFCloseL, VSIFOpenL, VSIStatL, StatBuf
from osgeo.gdal import VSI_STAT_EXISTS_FLAG, VSI_STAT_NATURE_FLAG
from osgeo.gdal import VSI_STAT_SIZE_FLAG, Rmdir


from numpy import ndarray

from .typing import NETCDFSubDataset, Sentinel2L1C, Sentinel3RBT


def build_unified_dataset(*datasets: Dataset) -> Dataset:
    """
    Combine an array of datasets into a Virtual dataset.

    Args
    ----
        :param datasets: A collection of gdal Dataset objects to
            combine in a virtual dataset.

    :returns: A virtual in-memory gdal.Dataset combining the inputs.
    """
    options = BuildVRTOptions(resolution="highest", separate=True,
                              callback=TermProgress)
    
    f"/vsimem/mem_{len(datasets)}.vrt"
    vrt: Dataset = BuildVRT("", list(datasets), options=options)

    for dataset in datasets: del dataset

    options = TranslateOptions(callback=TermProgress,)
    return Translate(f"built{len(datasets)}.tif", vrt, options=options)


def load_unscaled_S3_data(*netcdfs: NETCDFSubDataset | str) -> list[Dataset]:
    """
    Record unscaling as a preprocessing workflow
    and change to proper datatype.
    """
    options = TranslateOptions(unscale=True,
                               format="VRT",
                               outputType=GDT_Float32,
                               noData=-32768,
                               outputSRS="EPSG:4326")
    for netcdf in netcdfs:
        ds: Dataset = Translate(f"/vsimem/unscaled_{netcdf.name}.vrt",
                                netcdf.dataset,
                                options=options)
        
        netcdf.dataset = ds
        
        
def execute_geolocation(*netcdfs: NETCDFSubDataset):
    """
    Simply runs Warp with the geoloc switch activated.
    """
    options = WarpOptions(geoloc=True,
                          dstSRS="EPSG:4326",
                          multithread=True,
                          callback=TermProgress,
                          format="VRT")
    for netcdf in netcdfs:
        
        netcdf.dataset = Warp(f"/vsimem/geolocated_{netcdf.name}.vrt",
                              netcdf.dataset,
                              options=options)


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

        z = Z[i] * scaleZ + offsetZ
        x = X[i] * scaleX + offsetX
        y = Y[i] * scaleY + offsetY

        if 0 > z > 9000: continue
        if -90 > x > 90: continue
        if -180 > y > 180: continue

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


def crop_sen3_geometry(sen2: Sentinel2L1C, sen3: Sentinel3RBT) -> Dataset:
    # crop_b_to_a = Translate("/vsimem/mem_output.tif")
    outputbounds = get_bounds(sen2)
    print("Reprojecting and cropping Sen3")
    options = WarpOptions(targetAlignedPixels=True,
                          xRes=500,
                          yRes=500,
                          outputBounds=outputbounds,
                          outputBoundsSRS=sen2.GetSpatialRef(),
                          srcSRS=sen3.GetSpatialRef(),
                          dstSRS=sen2.GetSpatialRef(),
                          callback=TermProgress)
    
    sen3.dataset = Warp("sen3_cropped_output.tif", sen3, options=options)

