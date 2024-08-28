from osgeo.gdal import BuildVRT, BuildVRTOptions
from osgeo.gdal import Translate, TranslateOptions
from osgeo.gdal import Warp, WarpOptions
from osgeo.gdal import Info, InfoOptions
from osgeo.gdal import Dataset, GCP
from osgeo.gdal import GDT_Float32, TermProgress
from osgeo.gdal import Driver, GetDriverByName

from numpy import ndarray

from .typing import NETCDFSubDataset, Sentinel2L1C, Sentinel3RBT


def build_unified_dataset(*datasets: Dataset) -> None:
    """
    Combine an array of datasets into a Virtual dataset.

    Args
    ----
        :param datasets: A collection of gdal Dataset objects to
            combine in a virtual dataset.

    :returns: A virtual in-memory gdal.Dataset combining the inputs.
    """
    options = BuildVRTOptions(resolution="highest",
                              separate=True,
                              callback=TermProgress)
    
    vrt: Dataset = BuildVRT("", list(datasets), options=options)
    vrt.FlushCache()

    options = TranslateOptions(callback=TermProgress)
    
    # This output has to have a path to be seeked and opened by arosics.
    vrt = Translate(f"/vsimem/built_{len(datasets)}.vrt", vrt, options=options)
    vrt.FlushCache()

    return vrt


def load_unscaled_S3_data(*netcdfs: NETCDFSubDataset | str) -> None:
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
        # This output has to be a VRT file in order to be
        # infused with geolocation arrays.
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
                          format="VRT",
                          srcNodata=-32768,
                          dstNodata=-32768)
    for netcdf in netcdfs:
        netcdf.dataset = Warp(f"/vsimem/geolocated_{netcdf.name}.vrt",
                              netcdf.dataset,
                              options=options)


def geodetics_to_gcps(*geodetics: NETCDFSubDataset,
                      grid_dilation: int = 1) -> list[GCP]:
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
    expressed in xmin, ymin, xmax, ymax quantities.
    """
    transform = dataset.GetGeoTransform()
    xlen = dataset.RasterXSize
    ylen = dataset.RasterYSize
            # X min.
    return (transform[0],
            # Y min.
            transform[3] + xlen * transform[4] + ylen * transform[5], 
            # X max.
            transform[0] + xlen * transform[1] + ylen * transform[2],                       
            # Y max
            transform[3])


def crop_sen3_geometry(sen2: Sentinel2L1C, sen3: Sentinel3RBT) -> None:
    outputbounds = get_bounds(sen2.dataset)
    options = WarpOptions(targetAlignedPixels=True,
                          xRes=500,
                          yRes=500,
                          outputBounds=outputbounds,
                          srcSRS=sen3.dataset.GetSpatialRef(),
                          dstSRS=sen2.dataset.GetSpatialRef(),
                          callback=TermProgress,
                          format="GTIFF",
                          srcNodata=-32768,
                          dstNodata=-32768)
    sen3.dataset = Warp("/vsimem/cropped_S3.tif", sen3.dataset, options=options)
    sen3.dataset.FlushCache()


def trim_sen3_geometry(sen3: Sentinel3RBT) -> None:
    """
    Trim Sentinel-3 geometry to ensure it is contained within the
    Sentinel-2 bounds.

    Default trimming window is of dimensions 210x210 at a 4 pixel offset
    from the upper left corner. i.e. `srcWin=(4, 4, 210, 210)`
    """
    options = TranslateOptions(format="VRT",
                               # Offset can be increased to 5.
                               # Test image dimensions are 220 x 221.
                               srcWin=(4, 4, 210, 210),
                               callback=TermProgress,)
    sen3.dataset = Translate("", sen3.dataset, options=options)
    sen3.dataset.FlushCache()


def trim_sen2_geometry(sen2: Sentinel2L1C, sen3: Sentinel3RBT) -> None:
    """
    Trim Sentinel-2 image geometry to match the bounding box of Sentinel-3 scene.
    """
    corners = get_corners(sen3.dataset)
    options = TranslateOptions(format="VRT",
                               projWin=(*corners['upperLeft'],
                                        *corners['lowerRight']),
                               callback=TermProgress,)
    sen2.dataset = Translate("", sen2.dataset, options=options)
    sen2.dataset.FlushCache()


def create_dataset(xsize: int, ysize: int, nbands: int, *, driver: str,
                   name: str = "", etype: int = GDT_Float32, proj: str = "",
                   geotransform: tuple[int] = (),
                   options: list[str] = []) -> Dataset:
    driver: Driver = GetDriverByName(driver)
    dataset: Dataset = driver.Create(name, xsize, ysize, nbands, etype, options=options)
    dataset.SetProjection(proj)
    dataset.SetGeoTransform(geotransform)
    return dataset


def create_mem_dataset(xsize: int, ysize: int, nbands: int, *,
                       etype: int = GDT_Float32, proj: str = "",
                       geotransform: tuple[int] = (),
                       options: list[str] = []) -> Dataset:
    return create_dataset(driver="MEM", name="", **locals())


def get_vsi_size(dirname: str) -> dict:
    from osgeo.gdal import VSIStatL, ReadDir
    
    files = ReadDir(dirname)
    
    def get_size(x):
        __file = VSIStatL(x);
        if __file:
            return __file.size
    
    return {
        fpath: get_size(dirname + fpath) for fpath in files 
    }


def get_corners(dataset: Dataset):
    options = InfoOptions(format='json', deserialize=True)
    return Info(dataset, options=options)['cornerCoordinates']