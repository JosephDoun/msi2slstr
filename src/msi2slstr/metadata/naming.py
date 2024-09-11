from os.path import split

from ..data.sentinel2 import Sen2Name
from ..data.sentinel3 import Sen3Name


class ProductName(str):
    """
    A fused product name-factory class.

    :param sen2name: The file name of the Sentinel-2 SAFE archive.
    :param sen2name: Sen2Name
    :param sen3name: The file name of the Sentinel-3 SEN3 archive.
    :param sen3name: Sen3Name
    """
    __template__ = "M2S_{0}.tif".format

    def __new__(cls, sen2name: str, sen3name: str):
        sen2name = Sen2Name(sen2name)
        sen3name = Sen3Name(sen3name)
        content = cls.__format_product_name__(sen2name, sen3name)
        content = cls.__template__("_".join(content))
        obj = str.__new__(cls, content)
        return obj

    @classmethod
    def __format_product_name__(cls, sen2name: Sen2Name, sen3name: Sen3Name) -> list[str]:
        """
        Returns an iterable of strings to include in the output file name.
        """
        data = [sen2name.platform,
                sen3name.platform,
                sen2name.acquisition_date,
                sen3name.time,
                sen2name.tile]
        return data
