#!/usr/bin/env python3
"""Detect a project's stack and resolve matching Codex skills."""

from __future__ import annotations

import argparse
import json
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from detect_project_stack import detect_project_stack  # noqa: E402
from resolve_capability import resolve  # noqa: E402
from scan_global_skills import default_global_root  # noqa: E402


def resolve_project(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.expanduser().resolve()
    detected = detect_project_stack(project_root)
    stacks = [item["stack"] for item in detected["detected"][: args.max_stacks]]
    resolutions = []
    for stack in stacks:
        resolution_args = Namespace(
            capability=stack,
            root=args.root,
            global_root=args.global_root,
            project_root=project_root,
            include_system=args.include_system,
            allow_github=args.allow_github,
            github_limit=args.github_limit,
            install=args.install,
            scope=args.scope,
            target_root=args.target_root,
            yes=args.yes,
            json=True,
            pretty=False,
        )
        resolutions.append(resolve(resolution_args))
    return {"project": detected, "resolutions": resolutions}


def print_summary(result: dict[str, Any]) -> None:
    project = result["project"]
    print(f"Project: {project['project_root']}")
    if not project["detected"]:
        print("Detected stacks: none")
        return
    print("Detected stacks:")
    for item in project["detected"]:
        print(f"  - {item['stack']} confidence={item['confidence']} evidence={', '.join(item['evidence'])}")
    print()
    for resolution in result["resolutions"]:
        winner = resolution["winner"]
        print(f"Capability: {resolution['capability']}")
        if winner:
            print(f"  Winner: {winner['name']} ({winner['source']}) score={winner['score']}")
        else:
            print("  Winner: none")
        if resolution["installed_to"]:
            print(f"  Installed to: {resolution['installed_to']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to inspect")
    parser.add_argument("--root", action="append", default=[], help="Additional skills root to search")
    parser.add_argument("--global-root", type=Path, default=default_global_root(), help="Global Codex skills root")
    parser.add_argument("--include-system", action="store_true", help="Include built-in .system skills")
    parser.add_argument("--allow-github", action="store_true", help="Search GitHub using gh")
    parser.add_argument("--github-limit", type=int, default=10, help="Maximum GitHub repositories to inspect per stack")
    parser.add_argument("--max-stacks", type=int, default=3, help="Maximum detected stacks to resolve")
    parser.add_argument("--install", action="store_true", help="Install winning validated candidates")
    parser.add_argument("--scope", choices=["global", "local"], default="local", help="Install destination scope")
    parser.add_argument("--target-root", type=Path, help="Override skills install root")
    parser.add_argument("--yes", action="store_true", help="Required for installation")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    try:
        result = resolve_project(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print_summary(result)
    has_winner = any(item["winner"] for item in result["resolutions"])
    return 0 if has_winner else 1


if __name__ == "__main__":
    raise SystemExit(main())
