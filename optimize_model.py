"""Export the trained model with int8 weights."""

import json
import math

from train_model import ROOT


def quantize_matrix(matrix):
    largest = max(abs(value) for row in matrix for value in row)
    scale = largest / 127 if largest else 1.0
    quantized = [
        [int(math.floor(value / scale + 0.5) if value >= 0
             else math.ceil(value / scale - 0.5)) for value in row]
        for row in matrix
    ]
    return quantized, scale


def render_header(model):
    hidden, hidden_scale = quantize_matrix(model["weights"]["hidden_weights"])
    output, output_scale = quantize_matrix(model["weights"]["output_weights"])
    lines = [
        "#pragma once",
        "",
        "#include <stdint.h>",
        "",
        "const int MODEL_INPUTS = 2;",
        "const int MODEL_HIDDEN_UNITS = 8;",
        "const int MODEL_OUTPUTS = 3;",
        "",
    ]
    for name, values in (
        ("NORMALIZATION_MEANS", model["normalization"]["means"]),
        ("NORMALIZATION_SCALES", model["normalization"]["scales"]),
    ):
        lines.extend([
            f"const float {name}[MODEL_INPUTS] = {{",
            "  " + ", ".join(f"{value:.9g}f" for value in values),
            "};",
            "",
        ])
    for name, matrix, scale, biases in (
        ("HIDDEN", hidden, hidden_scale, model["weights"]["hidden_bias"]),
        ("OUTPUT", output, output_scale, model["weights"]["output_bias"]),
    ):
        lines.append(f"const float {name}_WEIGHT_SCALE = {scale:.9g}f;")
        lines.append(
            f"const int8_t {name}_WEIGHTS[{len(matrix)}][{len(matrix[0])}] = {{"
        )
        lines.extend("  {" + ", ".join(map(str, row)) + "}," for row in matrix)
        lines.extend([
            "};",
            f"const float {name}_BIAS[{len(biases)}] = {{",
            "  " + ", ".join(f"{value:.9g}f" for value in biases),
            "};",
            "",
        ])
    lines.extend([
        "const char* MODEL_LABELS[MODEL_OUTPUTS] = {",
        "  " + ", ".join(json.dumps(label) for label in model["labels"]),
        "};",
        "",
    ])
    return "\n".join(lines)


def main():
    model = json.loads((ROOT / "model.json").read_text())
    (ROOT / "model_data.h").write_text(render_header(model), encoding="utf-8")
    print("Wrote int8 weights to model_data.h")


if __name__ == "__main__":
    main()
