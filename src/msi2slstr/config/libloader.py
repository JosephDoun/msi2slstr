from os import PathLike
from os.path import join
from ctypes import cdll
from sys import platform

from . import get_yaml_dict
from . import site_packages_paths



def load_libraries(*paths: list[PathLike]):
    """
    Go through the python package installation sites
    and try to load corresponding libraries.

    :param paths: A relative path to a c shared library object.
    :type paths: PathLike | str

    :return: A list of failed paths.
    :rtype: list
    """
    failed = list(paths)
    for _p in paths:
        for site in site_packages_paths:
            try:
                cdll.LoadLibrary(join(site, _p))
                failed.remove(_p)
                break
            except OSError:
                continue
    return failed


# Cuda
libs: dict = get_yaml_dict("./libs.yaml")[platform]["nvidia"]
cuda_failed = load_libraries(*libs.values())

# ...