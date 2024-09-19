import unittest
import numpy as np

from msi2slstr.evaluation.metrics import Pearson, SRMSE, SSIM


class Test_Pearson(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.a = np.random.rand(12, 10, 10)
        self.b = np.ones((12, 10, 10))
        self.c = np.random.rand(1, 10, 10)

    def test_min(self):
        result = Pearson(self.a, -self.a)
        self.assertTrue(np.isclose(result, -1))

    def test_max(self):
        result = Pearson(self.a, self.a)
        self.assertTrue(np.isclose(result, 1))

    def test_unrelated(self):
        result = Pearson(self.a, np.zeros_like(self.a) + 1e-8)
        self.assertTrue(np.isclose(result, 0))


class Test_SRMSE(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.a = np.random.randn(12, 10, 10)
        self.b = np.ones((12, 10, 10))
        self.c = np.random.randn(1, 10, 10)
        self.mean = 0
        self.c = 0

    def test_min(self):
        result = SRMSE(self.a, self.a)
        self.assertTrue(np.allclose(result, 0))

    def test_max(self):
        scale = np.random.randn(1, 12, 1, 1)
        offset = np.random.randn(1, 12, 1, 1)
        result = SRMSE(self.a * scale + offset, -self.a * scale - offset)
        self.assertTrue((result > 1).all())
        self.assertTrue((result < 2).all())


class Test_SSIM(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.a = np.random.rand(1, 12, 10, 10)
        self.b = np.ones((1, 12, 10, 10))
        self.c = np.random.rand(1, 1, 10, 10)

    def test_maximum(self):
        self.assertTrue(np.allclose(SSIM(self.a, self.a, None), 1))

    def test_minimum(self):
        self.assertTrue(np.allclose(SSIM(self.a, -self.a), 0))

    def test_output_shape(self):
        result = SSIM(self.a, self.a)
        self.assertTrue(result.shape[-1] == self.a.shape[-3])
