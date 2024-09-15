from setuptools import setup
from importlib import util

import sys
import subprocess

sys.path.append(".")

import version


spec = util.spec_from_file_location("init", "src/msi2slstr/__init__.py")
module = util.module_from_spec(spec)
spec.loader.exec_module(module)


def get_gdal_system_version():
    return subprocess.run(["gdal-config", "--version"],
                           capture_output=True)\
                            .stdout\
                                .decode("utf-8")

setup(name="msi2slstr",
      version=version.__version__,
      description=module.__doc__.strip(),
      install_requires=[f"gdal=={get_gdal_system_version()}",
                        "pyproj==3.6.1",
                        "arosics==1.9.2",
                        "onnxruntime==1.18.1"])
