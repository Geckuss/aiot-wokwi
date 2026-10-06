import json
import unittest

from optimize_model import quantize_matrix
from train_model import LABELS, ROOT, load_rows, normalize, predict, split_rows


class QuantizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads((ROOT / "model.json").read_text())
        cls.weights = dict(cls.model["weights"])
        for layer in ("hidden", "output"):
            quantized, scale = quantize_matrix(
                cls.weights[f"{layer}_weights"]
            )
            cls.weights[f"{layer}_weights"] = [
                [value * scale for value in row] for row in quantized
            ]

    def test_weights_fit_int8(self):
        for layer in ("hidden", "output"):
            weights, scale = quantize_matrix(
                self.model["weights"][f"{layer}_weights"]
            )
            self.assertGreater(scale, 0)
            self.assertTrue(all(-127 <= value <= 127 for row in weights for value in row))

    def test_quantized_weights_keep_held_out_predictions(self):
        _, test_rows = split_rows(load_rows())
        correct = 0
        for features, expected in test_rows:
            normalized = normalize(
                features, self.model["normalization"]["means"],
                self.model["normalization"]["scales"],
            )
            _, probabilities = predict(normalized, self.weights)
            actual = LABELS[max(range(len(LABELS)), key=probabilities.__getitem__)]
            correct += actual == expected
        self.assertGreaterEqual(correct / len(test_rows), 0.95)

    def test_comfort_warning_and_poor_boundaries(self):
        examples = {
            (19, 30): "comfortable",
            (22, 45): "comfortable",
            (18.5, 45): "warning",
            (26, 45): "warning",
            (22, 25): "warning",
            (22, 65): "warning",
            (16.9, 45): "poor",
            (18.8, 45): "warning",
            (25.2, 45): "warning",
            (27.1, 45): "poor",
            (16.5, 45): "poor",
            (27.5, 45): "poor",
            (22, 72.5): "poor",
        }
        for features, expected in examples.items():
            normalized = normalize(
                features, self.model["normalization"]["means"],
                self.model["normalization"]["scales"],
            )
            _, probabilities = predict(normalized, self.weights)
            actual = LABELS[max(range(len(LABELS)), key=probabilities.__getitem__)]
            self.assertEqual(actual, expected, f"wrong label at {features}")


if __name__ == "__main__":
    unittest.main()
