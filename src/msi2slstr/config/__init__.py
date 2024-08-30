
from os import chdir, getcwd, PathLike
from os.path import dirname, realpath
from yaml import safe_load


__all__ = ["SEN2_MINMAX",
           "SEN3_MINMAX"]


class _OpenLocalFile:
    """
    Context manager for dealing with reading package-level files.
    """
    def __init__(self, localpath: PathLike) -> None:
        self.localpath = localpath

    def __enter__(self):
        self.root = getcwd()
        real = realpath(__file__)
        local = dirname(real)
        chdir(local)
        self.f_handle = open(self.localpath, "rt")
        return self.f_handle

    def __exit__(self, exc_type, exc_value, traceback):
        self.f_handle.close()
        chdir(self.root)



with _OpenLocalFile("./normalization.yaml") as stream:
    _NORMAL_MAXMIN = safe_load(stream)


SEN2_MINMAX = _NORMAL_MAXMIN['SEN2']
SEN3_MINMAX = _NORMAL_MAXMIN['SEN3']
