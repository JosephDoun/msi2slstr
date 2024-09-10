from sys import path
from os import chdir, getcwd, PathLike
from os.path import dirname, realpath
from yaml import safe_load


__all__ = ["SEN2_MINMAX",
           "SEN3_MINMAX"]


site_packages_paths = [p for p in path if p.endswith("site-packages")]
onnx_providers = ["CPUExecutionProvider"]
onnx_provider_options = None



class _OpenRelativePath:
    """
    Context manager for dealing with reading package-level files.
    """
    def __init__(self, localpath: PathLike, mode: str = "rt") -> None:
        self.localpath = localpath
        self.mode = mode

    def __enter__(self):
        self.root = getcwd()
        real = realpath(__file__)
        local = dirname(real)
        chdir(local)
        self.f_handle = open(self.localpath, self.mode)
        return self.f_handle

    def __exit__(self, exc_type, exc_value, traceback):
        self.f_handle.close()
        chdir(self.root)



def get_yaml_dict(path: str) -> dict:
    with _OpenRelativePath(path) as stream:
        load = safe_load(stream)
    return load


from .libloader import cuda_failed


def is_cuda_available():
    """
    It checks if the dependencies are present and loaded. It does not
    check if there is a compatible device. TODO

    :return: Whether nvidia libs are loaded.
    :rtype: bool
    """
    return not bool(cuda_failed)


if is_cuda_available():
    # Set CUDA as priority.
    onnx_providers.insert(0, "CUDAExecutionProvider")


_NORMAL_MAXMIN = get_yaml_dict("./normalization.yaml")
SEN2_MINMAX = _NORMAL_MAXMIN['SEN2']
SEN3_MINMAX = _NORMAL_MAXMIN['SEN3']


def get_sen2name_length():
    return len("S2B_MSIL1C_20231004T103809_N0509_R008_T31TDG_20231004T141941.SAFE")


def get_sen3name_length():
    return len("S3B_SL_1_RBT____20240826T102602_20240826T102902_20240826T122206_0180_097_008_2340_PS2_O_NR_004.SEN3")


