#!/usr/bin/env python3
"""Run deterministic self-tests for the capability orchestrator scripts."""

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


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_fixtures(root: Path) -> Path:
    examples = root / "examples"
    write(
        examples / "valid-skill" / "SKILL.md",
        "---\nname: valid-example-skill\ndescription: Example Codex skill used for self-tests.\n---\n\n# Valid\n",
    )
    write(examples / "valid-skill" / "references" / "guide.md", "# Guide\n")
    write(examples / "valid-skill" / "scripts" / "hello.py", "print('hello')\n")
    write(
        examples / "invalid-skill-missing-description" / "SKILL.md",
        "---\nname: invalid-example-skill\n---\n\n# Invalid\n",
    )
    write(
        examples / "manifests" / "candidate-valid.json",
        json.dumps(
            {
                "name": "demo-skill",
                "description": "Demo capability for validating candidate skill manifests.",
                "version": "1.0.0",
                "compatibility": None,
                "allowed_tools": ["Read"],
                "provenance": "local:self-test",
                "capabilities": ["demo"],
                "install": {},
                "security_notes": [],
            }
        ),
    )
    write(
        examples / "manifests" / "atomic-tool-valid.json",
        json.dumps(
            {
                "tool_id": "demo.tool",
                "name": "Demo Tool",
                "version": "1.0.0",
                "runtime": "python",
                "entrypoint": "tool.py",
                "input_schema": {},
                "output_schema": {},
                "tests": ["python -m pytest"],
                "sandbox_requirements": ["network disabled"],
                "provenance": "local:self-test",
            }
        ),
    )
    write(
        examples / "telemetry" / "good.json",
        json.dumps(
            [
                {
                    "candidate_id": "valid-example-skill",
                    "task_id": "static-quality",
                    "success_score": 1.0,
                    "error_rate": 0.0,
                    "reliability_score": 1.0,
                    "latency_ms": 12,
                    "latency_score": 1.0,
                    "input_tokens": 120,
                    "output_tokens": 40,
                    "token_efficiency_score": 0.9,
                    "maintainability_security_score": 0.95,
                    "evidence": ["valid SKILL.md"],
                },
                {
                    "candidate_id": "partial-example-skill",
                    "task_id": "static-quality",
                    "success_score": 0.4,
                    "error_rate": 0.6,
                    "reliability_score": 0.4,
                    "latency_ms": 20,
                    "latency_score": 0.8,
                    "input_tokens": 260,
                    "output_tokens": 90,
                    "token_efficiency_score": 0.5,
                    "maintainability_security_score": 0.5,
                    "evidence": ["missing references"],
                },
            ]
        ),
    )
    write(examples / "telemetry" / "malformed.json", json.dumps([{"candidate_id": "broken"}]))
    write(
        examples / "benchmark" / "static-skills.json",
        json.dumps(
            {
                "tasks": [{"task_id": "static-quality", "prompt": "Inspect skill quality."}],
                "candidates": [
                    {"candidate_id": "valid-example-skill", "skill_dir": str(examples / "valid-skill")},
                    {
                        "candidate_id": "invalid-example-skill",
                        "skill_dir": str(examples / "invalid-skill-missing-description"),
                    },
                ],
            }
        ),
    )
    write(
        examples / "laravel-skill" / "SKILL.md",
        "---\nname: laravel-workflow\ndescription: Laravel Codex skill for PHP routes, controllers, Eloquent, migrations, queues, tests, Sail, Artisan, and deployment checks.\n---\n\n# Laravel\n",
    )
    write(examples / "laravel-skill" / "references" / "checklist.md", "# Laravel Checklist\n")
    write(
        examples / "nextjs-skill" / "SKILL.md",
        "---\nname: nextjs-workflow\ndescription: Next.js Codex skill for App Router, React Server Components, route handlers, metadata, caching, server actions, TypeScript, Tailwind, and deployment checks.\n---\n\n# Next.js\n",
    )
    write(
        examples / "django-skill" / "SKILL.md",
        "---\nname: django-workflow\ndescription: Django Codex skill for models, migrations, views, templates, Django REST Framework, tests, management commands, and deployment checks.\n---\n\n# Django\n",
    )
    write(
        examples / "tailwind-skill" / "SKILL.md",
        "---\nname: tailwind-workflow\ndescription: Tailwind CSS Codex skill for utility classes, responsive layout, design tokens, components, and styling checks.\n---\n\n# Tailwind\n",
    )
    write(
        examples / "supabase-skill" / "SKILL.md",
        "---\nname: supabase-workflow\ndescription: Supabase Codex skill for auth, database schema, row level security, edge functions, storage, and client SDK usage.\n---\n\n# Supabase\n",
    )
    write(examples / "projects" / "nextjs" / "package.json", json.dumps({"dependencies": {"next": "^15.0.0"}}))
    write(
        examples / "projects" / "nextjs-full" / "package.json",
        json.dumps(
            {
                "dependencies": {
                    "next": "^15.0.0",
                    "@supabase/supabase-js": "^2.0.0",
                },
                "devDependencies": {"tailwindcss": "^4.0.0"},
            }
        ),
    )
    write(examples / "projects" / "django" / "requirements.txt", "django==5.0.0\n")
    write(examples / "projects" / "django" / "manage.py", "print('django')\n")
    write(examples / "projects" / "laravel" / "composer.json", json.dumps({"require": {"laravel/framework": "^11.0"}}))
    write(examples / "projects" / "laravel" / "artisan", "#!/usr/bin/env php\n")
    write(examples / "projects" / "flutter" / "pubspec.yaml", "name: demo\n\ndependencies:\n  flutter:\n    sdk: flutter\n")
    write(examples / "projects" / "go" / "go.mod", "module example.com/demo\n\ngo 1.22\n")
    return examples


def main() -> int:
    for script in SCRIPTS.glob("*.py"):
        compile(script.read_text(encoding="utf-8"), str(script), "exec")

    with tempfile.TemporaryDirectory() as tmp:
        examples = create_fixtures(Path(tmp))

        report = load_stdout_json(
            run([PYTHON, str(SCRIPTS / "inspect_skill.py"), str(examples / "valid-skill"), "--pretty"])
        )
        assert isinstance(report, dict)
        assert report["valid"] is True
        assert report["summary"]["reference_count"] == 1
        assert report["summary"]["script_count"] == 1

        invalid = run(
            [PYTHON, str(SCRIPTS / "inspect_skill.py"), str(examples / "invalid-skill-missing-description")],
            expect=0,
        )
        invalid_report = load_stdout_json(invalid)
        assert isinstance(invalid_report, dict)
        assert invalid_report["valid"] is False
        assert invalid_report["errors"]

        manifest = Path(tmp) / "candidate.json"
        generated = run(
            [PYTHON, str(SCRIPTS / "inspect_skill.py"), str(examples / "valid-skill"), "--manifest", "--pretty"]
        )
        manifest.write_text(generated.stdout, encoding="utf-8")
        assert load_stdout_json(
            run([PYTHON, str(SCRIPTS / "validate_manifest.py"), "candidate-skill", str(manifest)])
        ) == {"valid": True}

        assert load_stdout_json(
            run(
                [
                    PYTHON,
                    str(SCRIPTS / "validate_manifest.py"),
                    "candidate-skill",
                    str(examples / "manifests" / "candidate-valid.json"),
                ]
            )
        ) == {"valid": True}
        assert load_stdout_json(
            run(
                [
                    PYTHON,
                    str(SCRIPTS / "validate_manifest.py"),
                    "atomic-tool",
                    str(examples / "manifests" / "atomic-tool-valid.json"),
                ]
            )
        ) == {"valid": True}

        scored = load_stdout_json(
            run([PYTHON, str(SCRIPTS / "score_candidates.py"), str(examples / "telemetry" / "good.json")])
        )
        assert isinstance(scored, dict)
        assert scored["winner"] == "valid-example-skill"
        run([PYTHON, str(SCRIPTS / "score_candidates.py"), str(examples / "telemetry" / "malformed.json")], expect=2)

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
            run([PYTHON, str(SCRIPTS / "benchmark_skills.py"), str(examples / "benchmark" / "static-skills.json")])
        )
        assert isinstance(benchmark, dict)
        assert benchmark["ranking"][0]["candidate_id"] == "valid-example-skill"

        scan = load_stdout_json(
            run([PYTHON, str(SCRIPTS / "scan_global_skills.py"), "--root", str(examples), "--json"], expect=1)
        )
        assert isinstance(scan, dict)
        assert scan["total"] >= 2

        cli_scan = load_stdout_json(
            run(
                [PYTHON, str(SCRIPTS / "codex_skills.py"), "scan-global", "--root", str(examples), "--json"],
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
                    str(examples),
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
                    str(examples),
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

        target_root = Path(tmp) / "skills"
        installed = load_stdout_json(
            run(
                [
                    PYTHON,
                    str(SCRIPTS / "resolve_capability.py"),
                    "laravel",
                    "--root",
                    str(examples),
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
            run([PYTHON, str(SCRIPTS / "detect_project_stack.py"), str(examples / "projects" / "nextjs")])
        )
        assert isinstance(detected, dict)
        assert detected["detected"][0]["stack"] == "nextjs"

        laravel_detected = load_stdout_json(
            run([PYTHON, str(SCRIPTS / "detect_project_stack.py"), str(examples / "projects" / "laravel")])
        )
        assert isinstance(laravel_detected, dict)
        assert laravel_detected["detected"][0]["stack"] == "laravel"

        flutter_detected = load_stdout_json(
            run([PYTHON, str(SCRIPTS / "detect_project_stack.py"), str(examples / "projects" / "flutter")])
        )
        assert isinstance(flutter_detected, dict)
        assert flutter_detected["detected"][0]["stack"] == "flutter"

        go_detected = load_stdout_json(
            run([PYTHON, str(SCRIPTS / "detect_project_stack.py"), str(examples / "projects" / "go")])
        )
        assert isinstance(go_detected, dict)
        assert go_detected["detected"][0]["stack"] == "go"

        extracted = load_stdout_json(
            run(
                [
                    PYTHON,
                    str(SCRIPTS / "extract_capabilities.py"),
                    str(examples / "projects" / "nextjs-full"),
                    "--request",
                    "Create a Next.js product with Tailwind CSS and Supabase",
                ]
            )
        )
        assert isinstance(extracted, dict)
        extracted_ids = {item["id"] for item in extracted["capabilities"]}
        assert {"nextjs", "tailwindcss", "supabase"}.issubset(extracted_ids)

        project_resolved = load_stdout_json(
            run(
                [
                    PYTHON,
                    str(SCRIPTS / "resolve_project.py"),
                    str(examples / "projects" / "nextjs"),
                    "--root",
                    str(examples),
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
                    str(examples / "projects" / "django"),
                    "--root",
                    str(examples),
                    "--global-root",
                    "missing-global-skills",
                    "--json",
                ]
            )
        )
        assert isinstance(django_resolved, dict)
        assert django_resolved["project"]["detected"][0]["stack"] == "django"
        assert django_resolved["resolutions"][0]["winner"]["name"] == "django-workflow"

        install_rejected = run(
            [
                PYTHON,
                str(SCRIPTS / "prepare_project.py"),
                str(examples / "projects" / "nextjs-full"),
                "--request",
                "Create a Next.js product with Tailwind CSS and Supabase",
                "--root",
                str(examples),
                "--global-root",
                "missing-global-skills",
                "--install",
                "--json",
            ],
            expect=2,
        )
        assert "installation requires --yes" in install_rejected.stderr

        prepared = load_stdout_json(
            run(
                [
                    PYTHON,
                    str(SCRIPTS / "prepare_project.py"),
                    str(examples / "projects" / "nextjs-full"),
                    "--request",
                    "Create a Next.js product with Tailwind CSS and Supabase",
                    "--root",
                    str(examples),
                    "--global-root",
                    "missing-global-skills",
                    "--json",
                ]
            )
        )
        assert isinstance(prepared, dict)
        prepared_ids = {item["id"] for item in prepared["detected_capabilities"]}
        assert {"nextjs", "tailwindcss", "supabase"}.issubset(prepared_ids)
        assert Path(prepared["manifest_path"]).is_file()
        assert (examples / "projects" / "nextjs-full" / ".codex" / "context" / "docs" / "nextjs.json").is_file()
        winners = {item["capability"]: item["winner"]["name"] for item in prepared["skill_resolutions"] if item["winner"]}
        assert winners["nextjs"] == "nextjs-workflow"
        assert winners["tailwindcss"] == "tailwind-workflow"
        assert winners["supabase"] == "supabase-workflow"

        docs_only = load_stdout_json(
            run(
                [
                    PYTHON,
                    str(SCRIPTS / "codex_skills.py"),
                    "prepare-project",
                    str(examples / "projects" / "nextjs-full"),
                    "--request",
                    "UnknownStack with Next.js",
                    "--root",
                    str(examples),
                    "--global-root",
                    "missing-global-skills",
                    "--docs-only",
                    "--json",
                ]
            )
        )
        assert isinstance(docs_only, dict)
        assert docs_only["skill_resolutions"] == []

        prompt_style = load_stdout_json(
            run(
                [
                    PYTHON,
                    str(SCRIPTS / "codex_skills.py"),
                    "prepare-project",
                    str(examples / "projects" / "nextjs-full"),
                    "Create",
                    "a",
                    "Next.js",
                    "product",
                    "with",
                    "Tailwind",
                    "CSS",
                    "and",
                    "Supabase",
                    "--root",
                    str(examples),
                    "--global-root",
                    "missing-global-skills",
                    "--json",
                ]
            )
        )
        assert isinstance(prompt_style, dict)
        assert prompt_style["request"] == "Create a Next.js product with Tailwind CSS and Supabase"
        prompt_ids = {item["id"] for item in prompt_style["detected_capabilities"]}
        assert {"nextjs", "tailwindcss", "supabase"}.issubset(prompt_ids)

        shopify_prompt = load_stdout_json(
            run(
                [
                    PYTHON,
                    str(SCRIPTS / "codex_skills.py"),
                    "prepare-project",
                    str(examples / "projects" / "nextjs-full"),
                    "create",
                    "a",
                    "website",
                    "using",
                    "Shopify",
                    "Liquid",
                    "theme",
                    "--docs-only",
                    "--json",
                ]
            )
        )
        assert isinstance(shopify_prompt, dict)
        shopify_ids = {item["id"] for item in shopify_prompt["detected_capabilities"]}
        assert {"shopify", "liquid"}.issubset(shopify_ids)
        docs_written = {item["capability"] for item in shopify_prompt["docs"]["written"]}
        assert {"shopify", "liquid"}.issubset(docs_written)

        unknown_docs = load_stdout_json(
            run(
                [
                    PYTHON,
                    str(SCRIPTS / "fetch_docs_context.py"),
                    str(examples / "projects" / "nextjs-full"),
                    "unknownstack",
                    "--pretty",
                ]
            )
        )
        assert isinstance(unknown_docs, dict)
        assert unknown_docs["written"] == []
        assert "use --allow-docs-web" in unknown_docs["warnings"][0]

    print("self-test ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
