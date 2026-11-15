"""Metrics with denominators. 0/0 is None (N/A), never 0."""

from __future__ import annotations


def benchmark(true_positives: int, false_positives: int, false_negatives: int) -> dict[str, object]:
    precision_denominator = true_positives + false_positives
    recall_denominator = true_positives + false_negatives
    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": round(true_positives / precision_denominator, 4) if precision_denominator else None,
        "recall": round(true_positives / recall_denominator, 4) if recall_denominator else None,
        "denominators": {
            "precision": precision_denominator,
            "recall": recall_denominator,
        },
    }
