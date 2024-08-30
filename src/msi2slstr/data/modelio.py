from collections.abc import Generator
from dataclasses import dataclass, field
from osgeo.gdal import Dataset
from typing import Any

from .sentinel2 import Sentinel2L1C
from .sentinel3 import Sentinel3SLSTR, Sentinel3RBT, Sentinel3LST
from .gdalutils import crop_sen3_geometry
from .gdalutils import trim_sen3_geometry
from .gdalutils import trim_sen2_geometry

from ..align.corregistration import corregister_datasets


@dataclass
class ModelInput:
    sen2: Sentinel2L1C = field()
    sen3: Sentinel3SLSTR = field(init=False)
    sen3rbt: Sentinel3RBT = field(repr=False)
    sen3lst: Sentinel3LST = field(repr=False)

    def __post_init__(self):
        self.sen2 = Sentinel2L1C(self.sen2)
        self.sen3 = Sentinel3SLSTR(self.sen3rbt, self.sen3lst)
        crop_sen3_geometry(self.sen2, self.sen3)
        corregister_datasets(self.sen2, self.sen3)
        trim_sen3_geometry(self.sen3)
        trim_sen2_geometry(self.sen2, self.sen3)

        del self.sen3rbt, self.sen3lst


@dataclass
class Tiles:
    """
    Generator dataclass for tiling the ModelInput datamodel.

    :param d_tile: The dimensions of the tiles to be produced an int.
    :type d_tiles: Int

    """
    d_tile: tuple[int] = field()
    dataset: Dataset = field()

    def __post_init__(self):
        self.coords = get_array_coords_generator(self.d_tile,
                                                 self.dataset.RasterXSize,
                                                 self.dataset.RasterYSize)

    def __iter__(self):
        return (self.dataset.ReadAsArray(*coords) for coords in self.coords)


def get_array_coords_generator(t_size: int, sizex: int, sizey: int) -> Generator:
    """
    Returns a tuple of tile coordinates given the source image dimensions,
    tile size and array stride for sequential indexing.
    
    :return: A generator of xoffset, yoffset, tile_height, tile_width values
        in terms of array elements.
    :rtype: Generator
    """
    xtiles = sizex // t_size
    ytiles = sizey // t_size

    return ((i % xtiles * t_size, i // ytiles * t_size, t_size, t_size)
             for i in range(xtiles * ytiles))
    
