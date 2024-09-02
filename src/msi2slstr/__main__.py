import argparse

from sys import argv
from os import PathLike

from .data.modelio import ModelInput, ModelOutput
from .data.modelio import TileGenerator, TileDispatcher


parser = argparse.ArgumentParser("msi2slstr",
                                 usage=None,
                                 description=None,
                                 epilog=None)
parser.description =\
"""
Deep Learning infused piece of software that attempts to fuse MSI and SLSTR
sensor derived products onboard the Sentinel-2 and Sentinel-3 satellite
platforms. Currently supporting the fusion of RBT and LST products to Sentinel-2 
L1C.
"""

parser.epilog =\
"""
The model in use has been trained on daytime images of Central Europe\n
at a maximum of 5 minutes different of acquisition time and that is\n
the context in which it is expected to perform best.\n
"""

set_arg = parser.add_argument
set_arg("-l1c", "--sentinel2l1c", help="Path to a Sentinel-2 L1C SAFE archive.",
        type=PathLike, required=True, metavar="\"SEN2/L1C/PATH\"")
set_arg("-rbt", "--sentinel3rbt", help="Path to a Sentinel-3 RBT SEN3 archive.",
        type=PathLike, required=True, metavar="\"SEN3/RBT/PATH\"")
set_arg("-lst", "--sentinel3lst", help="Path to a Sentinel-3 LST SEN3 archive.",
        type=PathLike, required=True, metavar="\"SEN3/LST/PATH\"")


args = parser.parse_args(args=argv);

def main(args):

    inputs = ModelInput(sen2=args.l1c, sen3rbt=args.rbt, sen3lst=args.lst)
    generators = (TileGenerator(500, inputs.sen2), TileGenerator(10, inputs.sen3))
    data = TileDispatcher(generators)
    output = ModelOutput(inputs.sen2.dataset.GetGeoTransform(),
                         inputs.sen2.dataset.GetProjection(),
                         name=...,
                         xsize=inputs.sen2.dataset.RasterXSize)
    model = ...

    return 0


if __name__ == "__main__":
    main(args);
