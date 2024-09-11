from setuptools import setup

import subprocess


gdal_version = subprocess.run(["gdal-config", "--version"],
                              capture_output=True
                              ).stdout.decode("utf-8")

setup(name="msi2slstr",
      install_requires=[f"gdal=={gdal_version}",
                        "pyproj==3.6.1",
		                "arosics==1.9.2",])


