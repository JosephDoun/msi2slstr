import argparse

from os import environ
from sys import argv
from tqdm import tqdm

from .data.modelio import ModelInput, ModelOutput
from .data.modelio import TileGenerator, TileDispatcher
from .data.dataclasses import Dir
from .transform.preprocessing import DataPreprocessor
from .metadata.naming import ProductName
from .model import Runtime


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
        type=Dir, required=True, metavar="\"SEN2/L1C/PATH\"", dest="l1c")
set_arg("-rbt", "--sentinel3rbt", help="Path to a Sentinel-3 RBT SEN3 archive.",
        type=Dir, required=True, metavar="\"SEN3/RBT/PATH\"", dest="rbt")
set_arg("-lst", "--sentinel3lst", help="Path to a Sentinel-3 LST SEN3 archive.",
        type=Dir, required=True, metavar="\"SEN3/LST/PATH\"", dest="lst",)



environ["MODE"] = "INFER"


args = parser.parse_args(args=argv[1:]);

def main(args=args):

    inputs = ModelInput(sen2=args.l1c, sen3rbt=args.rbt, sen3lst=args.lst)
    generators = (TileGenerator(500, inputs.sen2.dataset),
                  TileGenerator(10, inputs.sen3.dataset))
    data = TileDispatcher(generators)
    output = ModelOutput(inputs.sen2.dataset.GetGeoTransform(),
                         inputs.sen2.dataset.GetProjection(),
                         name=ProductName(args.l1c, args.rbt),
                         xsize=inputs.sen2.dataset.RasterXSize,
                         ysize=inputs.sen2.dataset.RasterYSize,
                         nbands=inputs.sen3.dataset.RasterCount,
                         t_size=500)
    model = Runtime()
    preprocess = DataPreprocessor()
    for sen2tile, sen3tile in tqdm(data, desc="Fusing data..."):
        sen2tile, sen3tile = preprocess(sen2tile, sen3tile)
        Y_hat = model(sen2tile, sen3tile)[0]
        Y_hat = preprocess.reset_value_range(Y_hat)
        output.write_tiles(Y_hat)
    
    output.write_metadata([
        ...
    ])

    return 0


if __name__ == "__main__":
    main();
