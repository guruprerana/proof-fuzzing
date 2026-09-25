import unittest

from paper_data.plotting_stats import wilson_interval


class WilsonIntervalTests(unittest.TestCase):
    def test_known_symmetric_interval(self) -> None:
        low, high = wilson_interval(5, 10)
        self.assertAlmostEqual(low, 0.2365930905)
        self.assertAlmostEqual(high, 0.7634069095)

    def test_boundary_intervals_are_clamped(self) -> None:
        self.assertEqual(wilson_interval(0, 10)[0], 0.0)
        self.assertEqual(wilson_interval(10, 10)[1], 1.0)

    def test_rejects_invalid_counts(self) -> None:
        for successes, total in ((-1, 10), (11, 10), (0, 0)):
            with self.subTest(successes=successes, total=total):
                with self.assertRaises(ValueError):
                    wilson_interval(successes, total)

    def test_rejects_invalid_confidence(self) -> None:
        for confidence in (0.0, 1.0):
            with self.subTest(confidence=confidence):
                with self.assertRaises(ValueError):
                    wilson_interval(5, 10, confidence)


if __name__ == "__main__":
    unittest.main()
