import unittest
import numpy as np

from msi2slstr.evaluation.metrics import *


class Test_Pearson(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()
    
    def test_min_range(self):
        assert False

    def test_max_range(self):
        assert False


class Test_RelativeRMSE(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()
    
    def test_range(self):
        assert False


class Test_SSIM(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.a = np.random.rand(12, 10, 10)
        self.b = np.ones((12, 10, 10))
        self.c = np.random.rand(1, 10, 10)

    def test_maximum(self):
        self.assertEqual(SSIM(self.a, self.a, None), 1)

    def test_minimum(self):
        self.assertEqual(SSIM(self.a, -self.a), 0)
