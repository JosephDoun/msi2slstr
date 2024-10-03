import unittest

from numpy import float32
from numpy.random import randn
from msi2slstr.evaluation.scene import Evaluate


class TestEvaluation(unittest.TestCase):
    a = randn(4, 12, 10, 10).astype(float32)
    b = randn(4, 12, 10, 10).astype(float32)

    def setUp(self) -> None:
        super().setUp()
        self.evaluate = Evaluate()

    def test_registered_metrics(self):
        """TODO"""
        self.assertTrue(True)

    def test_evaluate_call(self):
        self.evaluate(self.a, self.b)
        self.assertListEqual(list(map(lambda x: x.__name__,
                                      self.evaluate.metrics)),
                             list(self.evaluate.metric_maps.keys()))

    def test_record_length(self):
        # The records length should be times the batch size.

        for _ in range(10):
            self.evaluate(self.a, self.a)

        for records in self.evaluate.metric_maps.values():
            self.assertEqual(len(records), 10 * self.a.shape[0])
