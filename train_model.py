"""Train a tiny temperature/humidity classifier without external packages."""

import csv
import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).parent
DATASET_DIR = ROOT / "datasets"
MODEL_PATH = ROOT / "model.json"
METRICS_PATH = ROOT / "training_metrics.json"
LABELS = ["comfortable", "warning", "poor"]
FEATURES = ["temperature_c", "humidity_percent"]
HIDDEN_UNITS = 24
TEST_FRACTION = 0.2
SEED = 7


def load_rows():
    rows = []
    for label in LABELS:
        with (DATASET_DIR / f"{label}.csv").open(newline="") as file:
            for row in csv.DictReader(file):
                rows.append(
                    ([float(row[feature]) for feature in FEATURES], label)
                )
    return rows


def split_rows(rows):
    randomizer = random.Random(SEED)
    train_rows = []
    test_rows = []
    boundary_temperatures = {17.0, 19.0, 25.0, 27.0}
    boundary_humidities = {20.0, 30.0, 60.0, 70.0}
    for label in LABELS:
        class_rows = [row for row in rows if row[1] == label]
        randomizer.shuffle(class_rows)
        boundary_rows = [
            row for row in class_rows
            if row[0][0] in boundary_temperatures
            or row[0][1] in boundary_humidities
        ]
        other_rows = [
            row for row in class_rows
            if row[0][0] not in boundary_temperatures
            and row[0][1] not in boundary_humidities
        ]
        test_count = max(1, round(len(other_rows) * TEST_FRACTION))
        test_rows.extend(other_rows[:test_count])
        train_rows.extend(other_rows[test_count:] + boundary_rows)
    randomizer.shuffle(train_rows)
    return train_rows, test_rows


def fit_scaler(rows):
    means = []
    scales = []
    for index in range(len(FEATURES)):
        values = [features[index] for features, _ in rows]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        means.append(mean)
        scales.append(math.sqrt(variance) or 1.0)
    return means, scales


def normalize(features, means, scales):
    return [(value - mean) / scale for value, mean, scale in zip(features, means, scales)]


def softmax(values):
    largest = max(values)
    exponentials = [math.exp(value - largest) for value in values]
    total = sum(exponentials)
    return [value / total for value in exponentials]


def relu(value):
    return max(0.0, value)


def predict(features, weights):
    hidden = [
        relu(sum(features[i] * weights["hidden_weights"][unit][i]
                for i in range(len(FEATURES))) + weights["hidden_bias"][unit])
        for unit in range(HIDDEN_UNITS)
    ]
    logits = [
        sum(hidden[i] * weights["output_weights"][label_index][i]
            for i in range(HIDDEN_UNITS)) + weights["output_bias"][label_index]
        for label_index in range(len(LABELS))
    ]
    return hidden, softmax(logits)


def train(train_rows, means, scales):
    randomizer = random.Random(SEED)
    class_weights = {
        label: len(train_rows) / (len(LABELS) * sum(row[1] == label for row in train_rows))
        for label in LABELS
    }
    weights = {
        "hidden_weights": [
            [randomizer.uniform(-0.1, 0.1) for _ in FEATURES]
            for _ in range(HIDDEN_UNITS)
        ],
        "hidden_bias": [0.0] * HIDDEN_UNITS,
        "output_weights": [
            [randomizer.uniform(-0.1, 0.1) for _ in range(HIDDEN_UNITS)]
            for _ in LABELS
        ],
        "output_bias": [0.0] * len(LABELS),
    }
    learning_rate = 0.03

    for _ in range(3500):
        randomizer.shuffle(train_rows)
        for raw_features, label in train_rows:
            features = normalize(raw_features, means, scales)
            hidden, probabilities = predict(features, weights)
            target = [1.0 if item == label else 0.0 for item in LABELS]

            sample_weight = class_weights[label]
            output_error = [
                sample_weight * (probability - expected)
                for probability, expected in zip(probabilities, target)
            ]
            hidden_error = [
                sum(output_error[label_index] *
                    weights["output_weights"][label_index][unit]
                    for label_index in range(len(LABELS)))
                if hidden[unit] > 0 else 0.0
                for unit in range(HIDDEN_UNITS)
            ]

            for label_index in range(len(LABELS)):
                for unit in range(HIDDEN_UNITS):
                    weights["output_weights"][label_index][unit] -= (
                        learning_rate * output_error[label_index] * hidden[unit]
                    )
                weights["output_bias"][label_index] -= (
                    learning_rate * output_error[label_index]
                )

            for unit in range(HIDDEN_UNITS):
                for feature_index in range(len(FEATURES)):
                    weights["hidden_weights"][unit][feature_index] -= (
                        learning_rate * hidden_error[unit] * features[feature_index]
                    )
                weights["hidden_bias"][unit] -= learning_rate * hidden_error[unit]
    return weights


def evaluate(rows, weights, means, scales):
    correct = 0
    predictions = []
    for raw_features, expected in rows:
        _, probabilities = predict(normalize(raw_features, means, scales), weights)
        predicted_index = max(range(len(LABELS)), key=probabilities.__getitem__)
        predicted = LABELS[predicted_index]
        correct += predicted == expected
        predictions.append({
            "temperature_c": raw_features[0],
            "humidity_percent": raw_features[1],
            "expected": expected,
            "predicted": predicted,
            "confidence": round(probabilities[predicted_index], 4),
        })
    return correct / len(rows), predictions


def main():
    rows = load_rows()
    train_rows, test_rows = split_rows(rows)
    means, scales = fit_scaler(train_rows)
    weights = train(train_rows, means, scales)
    train_accuracy, _ = evaluate(train_rows, weights, means, scales)
    test_accuracy, predictions = evaluate(test_rows, weights, means, scales)

    model = {
        "architecture": f"2 inputs -> {HIDDEN_UNITS} ReLU units -> 3 softmax outputs",
        "features": FEATURES,
        "labels": LABELS,
        "normalization": {"means": means, "scales": scales},
        "weights": weights,
    }
    metrics = {
        "seed": SEED,
        "rows": len(rows),
        "train_rows": len(train_rows),
        "test_rows": len(test_rows),
        "train_accuracy": round(train_accuracy, 4),
        "test_accuracy": round(test_accuracy, 4),
        "test_predictions": predictions,
    }
    MODEL_PATH.write_text(json.dumps(model, indent=2) + "\n")
    METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n")
    print(f"Rows: {len(rows)} (train={len(train_rows)}, test={len(test_rows)})")
    print(f"Train accuracy: {train_accuracy:.1%}")
    print(f"Test accuracy: {test_accuracy:.1%}")
    print(f"Wrote {MODEL_PATH.name} and {METRICS_PATH.name}")


if __name__ == "__main__":
    main()
