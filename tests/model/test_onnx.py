import unittest

from msi2slstr.model import Runtime
from numpy.random import randn
from numpy import float32


class TestONNXRuntime(unittest.TestCase):
    sen2 = randn(1, 13, 500, 500).astype(float32)
    sen3 = randn(1, 12, 10, 10).astype(float32)
    model = Runtime()

    def setUp(self) -> None:
        super().setUp()

    def test_gpu_support(self):
        ...

    def test_model_runs(self):
        _ = self.model(self.sen2, self.sen3)
        self.assertTrue(True)

    def test_batch_size(self):
        ...

    def test_patch_size(self):
        ...

    def test_channel_size(self):
        ...

    def test_io_binding(self):
        ...
