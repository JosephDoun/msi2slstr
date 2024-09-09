from collections.abc import Generator
from dataclasses import dataclass, field
from osgeo.gdal import Dataset, TermProgress
from osgeo.gdal_array import NumericTypeCodeToGDALTypeCode
from numpy import dtype, ndarray, float32, int16, int32
from typing import Any, Sequence

from .sentinel2 import Sentinel2L1C
from .sentinel3 import Sentinel3SLSTR, Sentinel3RBT, Sentinel3LST
from .gdalutils import crop_sen3_geometry
from .gdalutils import trim_sen3_geometry
from .gdalutils import trim_sen2_geometry
from .gdalutils import create_dataset

from ..align.corregistration import corregister_datasets
from ..metadata.abc import Metadata



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
          field(init=True)
    projection: str = field(init=True)
    name: str = field()
    xsize: int = field()
    ysize: int = field()
    nbands: int = field()
    t_size: int = field()
    d_type: dtype = field(default=float32)

    def __post_init__(self):
        assert len(self.geotransform) == 6
        self.dataset = create_dataset(xsize=self.xsize, ysize=self.ysize,
                                      nbands=self.nbands,
                                      driver="GTiff",
                                      name=self.name,
                                      etype=NumericTypeCodeToGDALTypeCode(self.d_type),
                                      geotransform=self.geotransform,
                                      proj=self.projection,
                                      options=[])
        self._coords_generator = get_array_coords_generator(t_size=self.t_size,
                                                            sizex=self.xsize,
                                                            sizey=self.ysize
                                                            ).__next__
    
    def write_tiles(self, load: ndarray):
        """
        Tile-writing method for 4D arrays containing N*3D tiles to be written
        to dataset.

        :param load: 4D array of 3D tiles.
        :param load: `numpy.ndarray`
        """
        for tile in load:
            coords = self._coords_generator()
            self.dataset.WriteArray(tile, *coords[:2],
                                    range(1, self.nbands + 1),)
        
    def write_metadata(self, m_list: list[Metadata]):
        ...


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
    batch_size: int = field(default=1)

    def __post_init__(self):
        self.coords = get_array_coords_generator(self.d_tile,
                                                 self.dataset.RasterXSize,
                                                 self.dataset.RasterYSize)
        self.__batches__ = range(0, len(self), self.batch_size)

    def __iter__(self):
        return (self.__get_batch__() for _ in self.__batches__)
    
    def __get_batch__(self):
        # Extract an array-tuple of size `batch_size` at a time.
        return tuple(self.dataset.ReadAsArray(*coords) for _, coords
                     in zip(range(self.batch_size), self.coords))
    
    def __len__(self):
        return self.dataset.RasterXSize * self.dataset.RasterYSize\
              // self.d_tile // self.d_tile


@dataclass
class TileDispatcher:

    tile_generators: tuple[TileGenerator]
    batch_size: int = field(default=1)
    
    def __post_init__(self):
        if not isinstance(self.tile_generators, Sequence):
            self.tile_generators = (self.tile_generators,)
            
        assert all(
            map(lambda x: -(-len(x) // x.batch_size) == len(self),
                self.tile_generators)
            ), "Tile generators of different lengths."

    def __iter__(self):
        return zip(*self.tile_generators, strict=True)
    
    def __len__(self):
        return - ( - len(self.tile_generators[0]) //
                  self.tile_generators[0].batch_size )
    