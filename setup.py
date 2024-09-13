from setuptools import setup

import subprocess


def get_gdal_system_version():
    return subprocess.run(["gdal-config", "--version"],
                           capture_output=True)\
                            .stdout\
                                .decode("utf-8")

setup(name="msi2slstr",
      install_requires=[f"gdal=={get_gdal_system_version()}",
                        "pyproj==3.6.1",
		                    "arosics==1.9.2",
                        "onnxruntime==1.18.1"])
