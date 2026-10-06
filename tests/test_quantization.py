import json
import unittest

from optimize_model import quantize_matrix
from train_model import LABELS, ROOT, load_rows, normalize, predict, split_rows


class QuantizationTests(unittest.TestCase):
    def test_weights_fit_int8(self):
        model = json.loads((ROOT / "model.json").read_text())
        for layer in ("hidden", "output"):
            weights, scale = quantize_matrix(model["weights"][f"{layer}_weights"])
            self.assertGreater(scale, 0)
            self.assertTrue(all(-127 <= value <= 127 for row in weights for value in row))

    def test_quantized_weights_keep_held_out_predictions(self):
        model = json.loads((ROOT / "model.json").read_text())
        weights = dict(model["weights"])
        for layer in ("hidden", "output"):
            quantized, scale = quantize_matrix(weights[f"{layer}_weights"])
            weights[f"{layer}_weights"] = [
                [value * scale for value in row] for row in quantized
            ]

        _, test_rows = split_rows(load_rows())
        for features, expected in test_rows:
            normalized = normalize(
                features, model["normalization"]["means"],
                model["normalization"]["scales"],
            )
            _, probabilities = predict(normalized, weights)
            actual = LABELS[max(range(len(LABELS)), key=probabilities.__getitem__)]
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
