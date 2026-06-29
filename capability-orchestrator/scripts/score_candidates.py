#!/usr/bin/env python3
"""Rank capability candidates from strict benchmark telemetry JSON."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from typing import Any

WEIGHTS = {
    "task_success": 0.45,
    "reliability": 0.25,
    "latency": 0.15,
    "token_efficiency": 0.10,
    "maintainability_security_fit": 0.05,
}

REQUIRED_FIELDS = {
    "candidate_id",
    "task_id",
    "success_score",
    "error_rate",
    "reliability_score",
    "latency_ms",
    "latency_score",
    "input_tokens",
    "output_tokens",
    "token_efficiency_score",
    "maintainability_security_score",
    "evidence",
}


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _score(value: Any, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{field} must be a number")
    result = float(value)
    if result < 0 or result > 1:
        raise ValueError(f"{field} must be in [0, 1]")
    return result


def _non_negative_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _validate_record(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError("telemetry records must be objects")
    keys = set(record)
    missing = REQUIRED_FIELDS - keys
    extra = keys - REQUIRED_FIELDS
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")
    if extra:
        raise ValueError(f"unknown fields: {sorted(extra)}")
    if not isinstance(record["candidate_id"], str) or not record["candidate_id"]:
        raise ValueError("candidate_id must be a non-empty string")
    if not isinstance(record["task_id"], str) or not record["task_id"]:
        raise ValueError("task_id must be a non-empty string")
    if not isinstance(record["evidence"], list) or not record["evidence"]:
        raise ValueError("evidence must be a non-empty list")
    if not all(isinstance(item, str) and item for item in record["evidence"]):
        raise ValueError("evidence entries must be non-empty strings")

    return {
        "candidate_id": record["candidate_id"],
        "task_id": record["task_id"],
        "success_score": _score(record["success_score"], "success_score"),
        "error_rate": _score(record["error_rate"], "error_rate"),
        "reliability_score": _score(record["reliability_score"], "reliability_score"),
        "latency_ms": _non_negative_int(record["latency_ms"], "latency_ms"),
        "latency_score": _score(record["latency_score"], "latency_score"),
        "input_tokens": _non_negative_int(record["input_tokens"], "input_tokens"),
        "output_tokens": _non_negative_int(record["output_tokens"], "output_tokens"),
        "token_efficiency_score": _score(record["token_efficiency_score"], "token_efficiency_score"),
        "maintainability_security_score": _score(
            record["maintainability_security_score"], "maintainability_security_score"
        ),
        "evidence": record["evidence"],
    }


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def rank(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["candidate_id"]].append(record)

    rankings = []
    for candidate_id, items in grouped.items():
        task_success = _mean([item["success_score"] for item in items])
        reliability = _mean([item["reliability_score"] for item in items])
        latency = _mean([item["latency_score"] for item in items])
        token_efficiency = _mean([item["token_efficiency_score"] for item in items])
        maintainability = _mean([item["maintainability_security_score"] for item in items])
        composite = (
            WEIGHTS["task_success"] * task_success
            + WEIGHTS["reliability"] * reliability
            + WEIGHTS["latency"] * latency
            + WEIGHTS["token_efficiency"] * token_efficiency
            + WEIGHTS["maintainability_security_fit"] * maintainability
        )
        rankings.append(
            {
                "candidate_id": candidate_id,
                "composite_score": round(composite, 6),
                "task_count": len(items),
                "dimensions": {
                    "task_success": round(task_success, 6),
                    "reliability": round(reliability, 6),
                    "latency": round(latency, 6),
                    "token_efficiency": round(token_efficiency, 6),
                    "maintainability_security_fit": round(maintainability, 6),
                },
            }
        )

    return sorted(rankings, key=lambda item: (-item["composite_score"], item["candidate_id"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("telemetry_json", help="Path to a JSON array of BenchmarkTelemetry objects")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    try:
        data = _load_json(args.telemetry_json)
        if not isinstance(data, list) or not data:
            raise ValueError("telemetry JSON must be a non-empty array")
        records = [_validate_record(item) for item in data]
        output = {"winner": rank(records)[0]["candidate_id"], "rankings": rank(records)}
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(output, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
