import unittest

from numpy import array
from numpy import allclose

from msi2slstr.transform.resizing import ValidAverageDownsampling


class Test_ValidAverageDownsampling(unittest.TestCase):
    down = ValidAverageDownsampling(2)
    data = array(
            [[
                [
                    [1, 1, 2, 2],
                    [1, 1, 2, 2],
                    [3, 3, 4, 4],
                    [3, 3, 4, 4]
                ]
            ]]
        )

    def test_down_shape(self):
        data = self.down(self.data)
        self.assertTrue(data.shape == (1, 1, 2, 2))

    def test_averaged_values(self):
        data = self.down(self.data)
        self.assertTrue(allclose(data.flatten(), [1, 2, 3, 4]))
