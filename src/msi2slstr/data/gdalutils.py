from osgeo.gdal import BuildVRT, BuildVRTOptions
from osgeo.gdal import Translate, TranslateOptions
from osgeo.gdal import Warp, WarpOptions
from osgeo.gdal import Dataset



def build_unified_dataset(datasets: list[Dataset]) -> Dataset:
    options = BuildVRTOptions(resolution="highest",
                              separate=True)
    return BuildVRT("/vsimem/mem_output.tif", datasets, options=options)


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

