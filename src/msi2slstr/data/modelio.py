from collections.abc import Generator
from dataclasses import dataclass, field
from osgeo.gdal import Dataset, TermProgress
from osgeo.gdal_array import NumericTypeCodeToGDALTypeCode
from numpy import _dtype, ndarray
from typing import Any, Sequence

from .sentinel2 import Sentinel2L1C
from .sentinel3 import Sentinel3SLSTR, Sentinel3RBT, Sentinel3LST
from .gdalutils import crop_sen3_geometry
from .gdalutils import trim_sen3_geometry
from .gdalutils import trim_sen2_geometry
from .gdalutils import create_dataset

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
class ModelOutput:
    """
    Defines the output and provides a method for data writing.
    """
    dataset: Dataset = field(init=False)
    geotransform: tuple[int, int, int, int, int, int] =\
          field(init=True, default_factory=tuple)
    projection: str = field(init=True, default=None)
    name: str = field()
    dtype: _dtype = field()
    xsize: int = field()
    ysize: int = field()
    nbands: int = field()
    t_size: int = field()

    def __post_init__(self):
        
        self.dataset = create_dataset(xsize=self.xsize, ysize=self.ysize,
                                      nbands=self.nbands,
                                      driver="JPEG2000",
                                      name=self.name,
                                      etype=NumericTypeCodeToGDALTypeCode(self.dtype),
                                      geotransform=self.geotransform,
                                      proj=self.projection,
                                      options=[])
        self._coords_generator = get_array_coords_generator(t_size=self.t_size,
                                                            sizex=self.xsize,
                                                            sizey=self.ysize
                                                            ).__next__
    
    def write_tile(self, load: ndarray):
        coords = self._coords_generator()
        self.dataset.WriteArray(load.swapaxes(0, -1), *coords[:2],
                                range(self.nbands),
                                callback=TermProgress)


def get_array_coords_generator(t_size: int, sizex: int, sizey: int) -> Generator:
    """
    Returns a tuple of tile coordinates given the source image dimensions,
    tile size and array stride for sequential indexing.
    
    :return: A generator of (xoffset, yoffset, tile_width, tile_height) values
        in terms of array elements.
    :rtype: Generator
    """
    xtiles = sizex // t_size
    ytiles = sizey // t_size
    return ((i % xtiles * t_size, i // ytiles * t_size, t_size, t_size)
             for i in range(xtiles * ytiles))
    
@dataclass
class TileGenerator:
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
    
    def __len__(self):
        return self.dataset.RasterXSize * self.dataset.RasterYSize // self.d_tile // self.d_tile


@dataclass
class TileDispatcher:

    tile_generators: tuple[TileGenerator]
    
    def __post_init__(self):
        if not isinstance(self.tile_generators, Sequence):
            self.tile_generators = (self.tile_generators,)
            
        assert all(
            map(lambda x:
                len(x) == len(self.tile_generators[0]),
                self.tile_generators)),\
                    "Tile generators of different lengths."

    def __iter__(self):
        return zip(self.tile_generators)
    