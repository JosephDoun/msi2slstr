import unittest

from msi2slstr.data.modelio import ModelOutput
from msi2slstr.metadata.abc import Metadata


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
                     "")
            ])

        self.assertTrue("test_metadata_key" in
                        self.data.dataset.GetMetadata().keys())

    def test_band_metadata_write_success(self):
        self.data.write_band_metadata(m_list=[
            Meta({"test_band_metadata_key": "test"},
                 "")
        ])

        self.assertTrue(self.data.dataset.GetRasterBand(3)
                        .GetMetadata()
                        ["test_band_metadata_key"] == "s")

    def test_band_metadata_write_incompatible(self):
        self.assertRaises(ValueError,
                          self.data.write_band_metadata,
                          [Meta({"test_band_metadata_key": "tests"},
                                "TEST_BAND_DOMAIN")])
