#!/usr/bin/env python3
"""Run deterministic self-tests for the capability orchestrator repository."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "capability-orchestrator" / "scripts"
PYTHON = sys.executable


def run(args: list[str], *, expect: int = 0, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if result.returncode != expect:
        print("command failed:", " ".join(args), file=sys.stderr)
        print("stdout:", result.stdout, file=sys.stderr)
        print("stderr:", result.stderr, file=sys.stderr)
        raise SystemExit(1)
    return result


def load_stdout_json(result: subprocess.CompletedProcess[str]) -> object:
    return json.loads(result.stdout)


def main() -> int:
    for script in SCRIPTS.glob("*.py"):
        compile(script.read_text(encoding="utf-8"), str(script), "exec")

    report = load_stdout_json(
        run([PYTHON, str(SCRIPTS / "inspect_skill.py"), "examples/valid-skill", "--pretty"])
    )
    assert isinstance(report, dict)
    assert report["valid"] is True
    assert report["summary"]["reference_count"] == 1
    assert report["summary"]["script_count"] == 1

    invalid = run(
        [PYTHON, str(SCRIPTS / "inspect_skill.py"), "examples/invalid-skill-missing-description"],
        expect=0,
    )
    invalid_report = load_stdout_json(invalid)
    assert isinstance(invalid_report, dict)
    assert invalid_report["valid"] is False
    assert invalid_report["errors"]

    with tempfile.TemporaryDirectory() as tmp:
        manifest = Path(tmp) / "candidate.json"
        generated = run(
            [
                PYTHON,
                str(SCRIPTS / "inspect_skill.py"),
                "examples/valid-skill",
                "--manifest",
                "--pretty",
            ]
        )
        manifest.write_text(generated.stdout, encoding="utf-8")
        valid_manifest = load_stdout_json(
            run([PYTHON, str(SCRIPTS / "validate_manifest.py"), "candidate-skill", str(manifest)])
        )
        assert valid_manifest == {"valid": True}

    assert load_stdout_json(
        run(
            [
                PYTHON,
                str(SCRIPTS / "validate_manifest.py"),
                "candidate-skill",
                "examples/manifests/candidate-valid.json",
            ]
        )
    ) == {"valid": True}
    assert load_stdout_json(
        run(
            [
                PYTHON,
                str(SCRIPTS / "validate_manifest.py"),
                "atomic-tool",
                "examples/manifests/atomic-tool-valid.json",
            ]
        )
    ) == {"valid": True}

    scored = load_stdout_json(
        run([PYTHON, str(SCRIPTS / "score_candidates.py"), "examples/telemetry/good.json"])
    )
    assert isinstance(scored, dict)
    assert scored["winner"] == "valid-example-skill"

    run([PYTHON, str(SCRIPTS / "score_candidates.py"), "examples/telemetry/malformed.json"], expect=2)

    harness = load_stdout_json(
        run(
            [
                PYTHON,
                str(SCRIPTS / "synthesize_tool_harness.py"),
                "--runtime",
                "python",
                "--entrypoint",
                "tool.py",
                "--test-command",
                '["python","-m","pytest"]',
            ]
        )
    )
    assert isinstance(harness, dict)
    assert harness["runtime"] == "python"
    run(
        [
            PYTHON,
            str(SCRIPTS / "synthesize_tool_harness.py"),
            "--runtime",
            "python",
            "--entrypoint",
            "../tool.py",
            "--test-command",
            '["python","-m","pytest"]',
        ],
        expect=2,
    )

    benchmark = load_stdout_json(
        run([PYTHON, str(SCRIPTS / "benchmark_skills.py"), "examples/benchmark/static-skills.json"])
    )
    assert isinstance(benchmark, dict)
    assert benchmark["ranking"][0]["candidate_id"] == "valid-example-skill"

    scan = load_stdout_json(
        run(
            [
                PYTHON,
                str(SCRIPTS / "scan_global_skills.py"),
                "--root",
                "examples",
                "--json",
            ],
            expect=1,
        )
    )
    assert isinstance(scan, dict)
    assert scan["total"] >= 2

    cli_scan = load_stdout_json(
        run(
            [
                PYTHON,
                str(SCRIPTS / "codex_skills.py"),
                "scan-global",
                "--root",
                "examples",
                "--json",
            ],
            expect=1,
        )
    )
    assert isinstance(cli_scan, dict)
    assert cli_scan["invalid"] >= 1

    print("self-test ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
