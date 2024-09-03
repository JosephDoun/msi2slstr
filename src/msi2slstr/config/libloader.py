from os import PathLike
from os.path import join
from ctypes import cdll


from . import get_yaml_dict
from . import site_packages_paths



def load_libraries(*paths: list[PathLike]):
    failed = list()
    for site in site_packages_paths:
        for _p in paths:
            try:
                cdll.LoadLibrary(join(site, _p))
            except OSError:
                failed.append(_p)
    return failed


# Cuda
libs: dict = get_yaml_dict("./paths.yaml")["nvidia"]
cuda_failed = load_libraries(*libs.values())

# ...