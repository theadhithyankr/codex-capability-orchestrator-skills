#!/usr/bin/env python3
"""Run deterministic self-tests for the capability orchestrator repository."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


THIS_FILE = Path(__file__).resolve()
if THIS_FILE.parents[1].name == "capability-orchestrator":
    SKILL_ROOT = THIS_FILE.parents[1]
    ROOT = SKILL_ROOT.parent
else:
    ROOT = THIS_FILE.parents[2]
    SKILL_ROOT = ROOT / "capability-orchestrator"
SCRIPTS = SKILL_ROOT / "scripts"
EXAMPLES = SKILL_ROOT / "examples"
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
        run([PYTHON, str(SCRIPTS / "inspect_skill.py"), str(EXAMPLES / "valid-skill"), "--pretty"])
    )
    assert isinstance(report, dict)
    assert report["valid"] is True
    assert report["summary"]["reference_count"] == 1
    assert report["summary"]["script_count"] == 1

    invalid = run(
        [PYTHON, str(SCRIPTS / "inspect_skill.py"), str(EXAMPLES / "invalid-skill-missing-description")],
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
                str(EXAMPLES / "valid-skill"),
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
                str(EXAMPLES / "manifests" / "candidate-valid.json"),
            ]
        )
    ) == {"valid": True}
    assert load_stdout_json(
        run(
            [
                PYTHON,
                str(SCRIPTS / "validate_manifest.py"),
                "atomic-tool",
                str(EXAMPLES / "manifests" / "atomic-tool-valid.json"),
            ]
        )
    ) == {"valid": True}

    scored = load_stdout_json(
        run([PYTHON, str(SCRIPTS / "score_candidates.py"), str(EXAMPLES / "telemetry" / "good.json")])
    )
    assert isinstance(scored, dict)
    assert scored["winner"] == "valid-example-skill"

    run([PYTHON, str(SCRIPTS / "score_candidates.py"), str(EXAMPLES / "telemetry" / "malformed.json")], expect=2)

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
        run([PYTHON, str(SCRIPTS / "benchmark_skills.py"), str(EXAMPLES / "benchmark" / "static-skills.json")])
    )
    assert isinstance(benchmark, dict)
    assert benchmark["ranking"][0]["candidate_id"] == "valid-example-skill"

    scan = load_stdout_json(
        run(
            [
                PYTHON,
                str(SCRIPTS / "scan_global_skills.py"),
                "--root",
                str(EXAMPLES),
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
                str(EXAMPLES),
                "--json",
            ],
            expect=1,
        )
    )
    assert isinstance(cli_scan, dict)
    assert cli_scan["invalid"] >= 1

    resolved = load_stdout_json(
        run(
            [
                PYTHON,
                str(SCRIPTS / "resolve_capability.py"),
                "laravel",
                "--root",
                str(EXAMPLES),
                "--global-root",
                "missing-global-skills",
                "--project-root",
                "missing-project",
                "--json",
            ]
        )
    )
    assert isinstance(resolved, dict)
    assert resolved["winner"]["name"] == "laravel-workflow"

    cli_resolved = load_stdout_json(
        run(
            [
                PYTHON,
                str(SCRIPTS / "codex_skills.py"),
                "resolve",
                "laravel",
                "--root",
                str(EXAMPLES),
                "--global-root",
                "missing-global-skills",
                "--project-root",
                "missing-project",
                "--json",
            ]
        )
    )
    assert isinstance(cli_resolved, dict)
    assert cli_resolved["winner"]["name"] == "laravel-workflow"

    with tempfile.TemporaryDirectory() as tmp:
        target_root = Path(tmp) / "skills"
        installed = load_stdout_json(
            run(
                [
                    PYTHON,
                    str(SCRIPTS / "resolve_capability.py"),
                    "laravel",
                    "--root",
                    str(EXAMPLES),
                    "--global-root",
                    "missing-global-skills",
                    "--project-root",
                    "missing-project",
                    "--install",
                    "--scope",
                    "local",
                    "--target-root",
                    str(target_root),
                    "--yes",
                    "--json",
                ]
            )
        )
        assert installed["installed_to"]
        assert (target_root / "laravel-workflow" / "SKILL.md").is_file()

    detected = load_stdout_json(
        run([PYTHON, str(SCRIPTS / "detect_project_stack.py"), str(EXAMPLES / "projects" / "nextjs")])
    )
    assert isinstance(detected, dict)
    assert detected["detected"][0]["stack"] == "nextjs"

    project_resolved = load_stdout_json(
        run(
            [
                PYTHON,
                str(SCRIPTS / "resolve_project.py"),
                str(EXAMPLES / "projects" / "nextjs"),
                "--root",
                str(EXAMPLES),
                "--global-root",
                "missing-global-skills",
                "--json",
            ]
        )
    )
    assert isinstance(project_resolved, dict)
    assert project_resolved["project"]["detected"][0]["stack"] == "nextjs"
    assert project_resolved["resolutions"][0]["winner"]["name"] == "nextjs-workflow"

    django_resolved = load_stdout_json(
        run(
            [
                PYTHON,
                str(SCRIPTS / "codex_skills.py"),
                "resolve-project",
                str(EXAMPLES / "projects" / "django"),
                "--root",
                str(EXAMPLES),
                "--global-root",
                "missing-global-skills",
                "--json",
            ]
        )
    )
    assert isinstance(django_resolved, dict)
    assert django_resolved["project"]["detected"][0]["stack"] == "django"
    assert django_resolved["resolutions"][0]["winner"]["name"] == "django-workflow"

    print("self-test ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
