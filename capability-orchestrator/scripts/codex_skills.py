#!/usr/bin/env python3
"""Codex Skills helper CLI for capability-orchestrator users."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
PYTHON = sys.executable

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from scan_global_skills import scan_global_skills, default_global_root, print_table  # noqa: E402


def run_python(script: str, args: Sequence[str]) -> int:
    return subprocess.call([PYTHON, str(SCRIPT_DIR / script), *args], cwd=Path.cwd())


def cmd_scan_global(args: argparse.Namespace) -> int:
    result = scan_global_skills(args.root.expanduser().resolve(), include_system=args.include_system)
    if args.json:
        print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print_table(result)
    return 0 if result["invalid"] == 0 else 1


def cmd_self_test(_: argparse.Namespace) -> int:
    return run_python("run_self_test.py", [])


def cmd_benchmark_examples(args: argparse.Namespace) -> int:
    cli_args = ["examples/benchmark/static-skills.json"]
    if args.pretty:
        cli_args.append("--pretty")
    return run_python("benchmark_skills.py", cli_args)


def cmd_inspect(args: argparse.Namespace) -> int:
    cli_args = [args.skill_dir]
    if args.manifest:
        cli_args.append("--manifest")
    if args.pretty:
        cli_args.append("--pretty")
    return run_python("inspect_skill.py", cli_args)


def cmd_resolve(args: argparse.Namespace) -> int:
    cli_args = [args.capability]
    for root in args.root:
        cli_args.extend(["--root", root])
    if args.global_root:
        cli_args.extend(["--global-root", args.global_root])
    if args.project_root:
        cli_args.extend(["--project-root", args.project_root])
    if args.include_system:
        cli_args.append("--include-system")
    if args.allow_github:
        cli_args.append("--allow-github")
    cli_args.extend(["--github-limit", str(args.github_limit)])
    if args.install:
        cli_args.append("--install")
    cli_args.extend(["--scope", args.scope])
    if args.target_root:
        cli_args.extend(["--target-root", args.target_root])
    if args.yes:
        cli_args.append("--yes")
    if args.json:
        cli_args.append("--json")
    if args.pretty:
        cli_args.append("--pretty")
    return run_python("resolve_capability.py", cli_args)


def cmd_detect(args: argparse.Namespace) -> int:
    cli_args = [args.project_root]
    if args.pretty:
        cli_args.append("--pretty")
    return run_python("detect_project_stack.py", cli_args)


def cmd_resolve_project(args: argparse.Namespace) -> int:
    cli_args = [args.project_root]
    for root in args.root:
        cli_args.extend(["--root", root])
    if args.global_root:
        cli_args.extend(["--global-root", args.global_root])
    if args.include_system:
        cli_args.append("--include-system")
    if args.allow_github:
        cli_args.append("--allow-github")
    cli_args.extend(["--github-limit", str(args.github_limit)])
    cli_args.extend(["--max-stacks", str(args.max_stacks)])
    if args.install:
        cli_args.append("--install")
    cli_args.extend(["--scope", args.scope])
    if args.target_root:
        cli_args.extend(["--target-root", args.target_root])
    if args.yes:
        cli_args.append("--yes")
    if args.json:
        cli_args.append("--json")
    if args.pretty:
        cli_args.append("--pretty")
    return run_python("resolve_project.py", cli_args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-skills",
        description="Easy CLI for scanning and testing Codex Agent Skills.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan-global", help="Scan globally installed Codex skills")
    scan.add_argument("--root", type=Path, default=default_global_root(), help="Global Codex skills root")
    scan.add_argument("--include-system", action="store_true", help="Include built-in .system skills")
    scan.add_argument("--json", action="store_true", help="Emit JSON")
    scan.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    scan.set_defaults(func=cmd_scan_global)

    self_test = subparsers.add_parser("self-test", help="Run repository self-tests")
    self_test.set_defaults(func=cmd_self_test)

    benchmark = subparsers.add_parser("benchmark-examples", help="Run the included static benchmark fixture")
    benchmark.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    benchmark.set_defaults(func=cmd_benchmark_examples)

    inspect = subparsers.add_parser("inspect", help="Inspect a skill folder")
    inspect.add_argument("skill_dir", help="Path to a Codex skill folder")
    inspect.add_argument("--manifest", action="store_true", help="Emit candidate manifest JSON")
    inspect.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    inspect.set_defaults(func=cmd_inspect)

    resolve = subparsers.add_parser("resolve", help="Find, compare, and optionally install the best skill")
    resolve.add_argument("capability", help="Capability to resolve, e.g. laravel")
    resolve.add_argument("--root", action="append", default=[], help="Skills root to search")
    resolve.add_argument("--global-root", help="Global Codex skills root")
    resolve.add_argument("--project-root", help="Project root for .codex/skills search")
    resolve.add_argument("--include-system", action="store_true", help="Include built-in .system skills")
    resolve.add_argument("--allow-github", action="store_true", help="Search GitHub with gh")
    resolve.add_argument("--github-limit", type=int, default=10, help="Maximum GitHub repositories to inspect")
    resolve.add_argument("--install", action="store_true", help="Install the winning validated candidate")
    resolve.add_argument("--scope", choices=["global", "local"], default="local", help="Install destination scope")
    resolve.add_argument("--target-root", help="Override skills install root")
    resolve.add_argument("--yes", action="store_true", help="Required for installation")
    resolve.add_argument("--json", action="store_true", help="Emit JSON")
    resolve.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    resolve.set_defaults(func=cmd_resolve)

    detect = subparsers.add_parser("detect", help="Detect project stacks from repository files")
    detect.add_argument("project_root", nargs="?", default=".", help="Project root to inspect")
    detect.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    detect.set_defaults(func=cmd_detect)

    resolve_project = subparsers.add_parser("resolve-project", help="Detect project stack and resolve matching skills")
    resolve_project.add_argument("project_root", nargs="?", default=".", help="Project root to inspect")
    resolve_project.add_argument("--root", action="append", default=[], help="Additional skills root to search")
    resolve_project.add_argument("--global-root", help="Global Codex skills root")
    resolve_project.add_argument("--include-system", action="store_true", help="Include built-in .system skills")
    resolve_project.add_argument("--allow-github", action="store_true", help="Search GitHub with gh")
    resolve_project.add_argument("--github-limit", type=int, default=10, help="Maximum GitHub repositories to inspect")
    resolve_project.add_argument("--max-stacks", type=int, default=3, help="Maximum detected stacks to resolve")
    resolve_project.add_argument("--install", action="store_true", help="Install winning validated candidates")
    resolve_project.add_argument("--scope", choices=["global", "local"], default="local", help="Install destination scope")
    resolve_project.add_argument("--target-root", help="Override skills install root")
    resolve_project.add_argument("--yes", action="store_true", help="Required for installation")
    resolve_project.add_argument("--json", action="store_true", help="Emit JSON")
    resolve_project.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    resolve_project.set_defaults(func=cmd_resolve_project)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
