from osgeo.gdal import BuildVRT, BuildVRTOptions
from osgeo.gdal import Translate, TranslateOptions
from osgeo.gdal import Warp, WarpOptions
from osgeo.gdal import Dataset


def build_unified_dataset(datasets: list[Dataset]) -> Dataset:
    options = BuildVRTOptions(resolution="highest",
                              separate=True)
    return BuildVRT("/vsimem/mem_output.tif", datasets, options=options)


def crop_sen3_geometry(sen2: Dataset, sen3: Dataset) -> Dataset:
    # crop_b_to_a = Translate("/vsimem/mem_output.tif")
    transform_a: tuple = sen2.GetGeoTransform()
    transform_b: tuple = sen3.GetGeoTransform()
    
    outputbounds = ((transform_a[0],
                     transform_a[3]),
                    (transform_a[0] + xlen * transform_a[1] + ylen * transform_a[2],
                     transform_a[3] + xlen * transform_a[4] + ylen * transform_a[5]))
    
    options = WarpOptions(creationOptions=["TILED=YES",
                                           "BLOCKXSIZE=16",
                                           "BLOCKYSIZE=16"],
                          targetAlignedPixels=True,
                          xRes=500,
                          yRes=500,
                          outputBounds=outputbounds,
                          srcSRS=sen2.GetSpatialRef(),
                          outputBoundsSRS=sen2.GetSpatialRef())
    sen3_cropped = Warp("/vsimem/sen3_cropped_output.tif", sen3, options=options)

    return

