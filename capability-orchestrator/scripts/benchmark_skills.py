#!/usr/bin/env python3
"""Generate static benchmark telemetry for existing Codex skill folders."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from inspect_skill import inspect_skill  # noqa: E402
from score_candidates import rank  # noqa: E402


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a non-empty array")
    return value


def _resolve(base: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (base / path).resolve()


def _token_efficiency(skill_dir: Path) -> float:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return 0.0
    size = len(skill_md.read_text(encoding="utf-8"))
    if size <= 2500:
        return 1.0
    if size >= 10000:
        return 0.25
    return round(1.0 - ((size - 2500) / 10000), 6)


def _maintainability(report: dict[str, Any]) -> float:
    if not report["valid"]:
        return 0.0
    score = 1.0
    if report["warnings"]:
        score -= min(0.4, 0.1 * len(report["warnings"]))
    if report["summary"]["body_lines"] > 500:
        score -= 0.2
    if report["summary"]["reference_count"] == 0 and report["summary"]["script_count"] == 0:
        score -= 0.1
    return round(max(0.0, score), 6)


def _telemetry(candidate_id: str, task_id: str, skill_dir: Path) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        report = inspect_skill(skill_dir)
        elapsed = int((time.perf_counter() - start) * 1000)
        valid = bool(report["valid"])
        errors = report["errors"]
        evidence = [f"inspected {skill_dir}"]
        if valid:
            evidence.append("valid SKILL.md frontmatter")
        evidence.extend(report["warnings"] or [])
        evidence.extend(errors or [])
        return {
            "candidate_id": candidate_id,
            "task_id": task_id,
            "success_score": 1.0 if valid else 0.0,
            "error_rate": 0.0 if valid else 1.0,
            "reliability_score": 1.0 if valid else 0.0,
            "latency_ms": elapsed,
            "latency_score": 1.0 if elapsed < 1000 else 0.5,
            "input_tokens": 0,
            "output_tokens": 0,
            "token_efficiency_score": _token_efficiency(skill_dir),
            "maintainability_security_score": _maintainability(report),
            "evidence": evidence,
        }
    except (OSError, ValueError) as exc:
        elapsed = int((time.perf_counter() - start) * 1000)
        return {
            "candidate_id": candidate_id,
            "task_id": task_id,
            "success_score": 0.0,
            "error_rate": 1.0,
            "reliability_score": 0.0,
            "latency_ms": elapsed,
            "latency_score": 0.0,
            "input_tokens": 0,
            "output_tokens": 0,
            "token_efficiency_score": 0.0,
            "maintainability_security_score": 0.0,
            "evidence": [str(exc)],
        }


def run_benchmark(spec_path: Path) -> dict[str, Any]:
    spec = _load_json(spec_path)
    if not isinstance(spec, dict):
        raise ValueError("benchmark spec must be an object")
    tasks = _require_list(spec.get("tasks"), "tasks")
    candidates = _require_list(spec.get("candidates"), "candidates")
    base = spec_path.parent.parent.parent if "examples/benchmark" in spec_path.as_posix() else Path.cwd()

    records = []
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("task_id"), str):
            raise ValueError("each task must include task_id")
        for candidate in candidates:
            if not isinstance(candidate, dict):
                raise ValueError("each candidate must be an object")
            candidate_id = candidate.get("candidate_id")
            skill_dir = candidate.get("skill_dir")
            if not isinstance(candidate_id, str) or not isinstance(skill_dir, str):
                raise ValueError("each candidate must include candidate_id and skill_dir")
            records.append(_telemetry(candidate_id, task["task_id"], _resolve(base, skill_dir)))

    return {"telemetry": records, "ranking": rank(records)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark_json", help="Path to benchmark spec JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    try:
        output = run_benchmark(Path(args.benchmark_json).resolve())
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps(output, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
