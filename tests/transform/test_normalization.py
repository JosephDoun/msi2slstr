import unittest

from numpy import allclose, ones, zeros
from numpy.random import rand, randn, randint
from msi2slstr.transform.normalization import Normalizer, Standardizer


class TestNormalizer(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.size = randint(1, 10, 4)
        self.load = rand(*self.size)

    def test_scale(self):
        scale = randn(self.size[-3])
        offset = zeros(self.size[-3])
        normal = Normalizer(offset, scale)
        scaled_array = normal(self.load)
        means = self.load.mean((-1, -2))
        normal_means = scaled_array.mean((-1, -2))
        mean_ratio = means / normal_means
        self.assertTrue(allclose(mean_ratio, scale))


    def test_offset(self):
        scale = ones(self.size[-3])
        offset = randn(self.size[-3])
        scaled_array = Normalizer(offset, scale)(self.load)
        means = self.load.mean((-1, -2))
        normal_means = scaled_array.mean((-1, -2))
        mean_ratio = means - normal_means
        self.assertTrue(allclose(mean_ratio, offset))

    def test_unscaling(self):
        scale = randn(self.size[-3])
        offset = randn(self.size[-3])
        normal = Normalizer(offset, scale)
        scaled = normal(self.load)
        array = normal.reverse(scaled)
        self.assertTrue(allclose(array, self.load))


class TestStandardizer(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.dims = (-1, -2)
        self.size = randint(1, 10, 4)
        self.load = randn(*self.size)
        self.standard = Standardizer(self.dims)
        self.standard_load = self.standard(self.load)

    def test_mean(self):
        self.assertTrue(allclose(self.standard_load.mean(self.dims), 0))

    def test_var(self):
        self.assertTrue(allclose(self.standard_load.std(self.dims), 1))
