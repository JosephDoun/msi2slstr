import unittest

from msi2slstr.data.modelio import ModelOutput
from msi2slstr.metadata.quality import FusionQualityMetadata

from numpy.random import randn
from numpy import isclose


class TestFusionQualityMetadata(unittest.TestCase):
    data = ModelOutput(geotransform=(1, 1, 1, 1, 1, 1),
                       projection="",
                       name="/vsimem/test_quality.tif",
                       xsize=1, ysize=1, nbands=4, t_size=1)
    meta = FusionQualityMetadata()

    def test_successful_write(self):
        a = randn(1, 4, 10, 10)

        for _ in range(10):
            self.meta.evaluate(a, a)

        self.data.write_band_metadata([self.meta])

        band_stats = self.data.dataset.GetRasterBand(2)\
            .GetMetadata("Fusion Quality")

        self.assertTrue(isclose(float(band_stats['r']), 1))
        self.assertTrue(isclose(float(band_stats['srmse']), 0))
        self.assertTrue(isclose(float(band_stats['ssim']), 1))
