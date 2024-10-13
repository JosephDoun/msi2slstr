import unittest

from msi2slstr.data.modelio import ModelOutput
from msi2slstr.metadata.abc import Metadata
from osgeo.gdal import Band


class Meta(Metadata):
    def __init__(self, content: dict, domain: str) -> None:
        super().__init__()
        self._content = content
        self._domain = domain

    @property
    def content(self):
        return self._content

    @property
    def domain(self):
        return self._domain


class TestModelOutput(unittest.TestCase):
    data = ModelOutput(geotransform=(1, 1, 1, 1, 1, 1),
                       projection="",
                       name="/vsimem/test.tif",
                       xsize=1,
                       ysize=1,
                       nbands=4,
                       t_size=1)

    def setUp(self) -> None:
        super().setUp()
        
    def test_metadata_write(self):
        self.data.write_metadata([
                Meta({"test_metadata_key": "test_metadata_value"},
                     "TEST_DOMAIN")
            ])

        self.assertTrue("TEST_DOMAIN" in
                        self.data.dataset.GetMetadataDomainList())

    def test_band_metadata_write_success(self):
        self.data.write_band_metadata(m_list=[
            Meta({"test_band_metadata_key": "test"},
                 "TEST_BAND_DOMAIN")
        ])
        
        self.assertTrue(self.data.dataset.GetRasterBand(3)
                        .GetMetadata("TEST_BAND_DOMAIN")
                        ["test_band_metadata_key"] == "s")

    def test_band_metadata_write_incompatible(self):
        self.assertRaises(ValueError,
                          self.data.write_band_metadata,
                          [Meta({"test_band_metadata_key": "tests"},
                                "TEST_BAND_DOMAIN")])