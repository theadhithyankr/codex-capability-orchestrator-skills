#!/usr/bin/env python3
"""Scan globally installed Codex skills and report validation status."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from inspect_skill import inspect_skill  # noqa: E402


def default_global_root() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "skills"
    return Path.home() / ".codex" / "skills"


def discover_skill_dirs(root: Path, *, include_system: bool) -> list[Path]:
    if not root.exists():
        raise ValueError(f"global skills directory does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"global skills path is not a directory: {root}")

    skills: list[Path] = []
    for child in sorted(root.iterdir(), key=lambda item: item.name.lower()):
        if not child.is_dir():
            continue
        if child.name == ".system":
            if include_system:
                skills.extend(sorted((item for item in child.iterdir() if item.is_dir()), key=lambda item: item.name.lower()))
            continue
        skills.append(child)
    return skills


def scan_global_skills(root: Path, *, include_system: bool) -> dict[str, Any]:
    reports = []
    for skill_dir in discover_skill_dirs(root, include_system=include_system):
        try:
            report = inspect_skill(skill_dir)
            frontmatter = report.get("frontmatter", {})
            reports.append(
                {
                    "name": frontmatter.get("name") or skill_dir.name,
                    "valid": report["valid"],
                    "errors": report["errors"],
                    "warnings": report["warnings"],
                    "scripts": report["summary"]["script_count"],
                    "references": report["summary"]["reference_count"],
                    "assets": report["summary"]["asset_count"],
                    "path": str(skill_dir),
                }
            )
        except (OSError, ValueError) as exc:
            reports.append(
                {
                    "name": skill_dir.name,
                    "valid": False,
                    "errors": [str(exc)],
                    "warnings": [],
                    "scripts": 0,
                    "references": 0,
                    "assets": 0,
                    "path": str(skill_dir),
                }
            )
    return {
        "root": str(root),
        "include_system": include_system,
        "total": len(reports),
        "valid": sum(1 for report in reports if report["valid"]),
        "invalid": sum(1 for report in reports if not report["valid"]),
        "skills": reports,
    }


def print_table(result: dict[str, Any]) -> None:
    rows = result["skills"]
    print(f"Global skills root: {result['root']}")
    print(f"Skills scanned: {result['total']} | valid: {result['valid']} | invalid: {result['invalid']}")
    print()
    if not rows:
        print("No skills found.")
        return

    headers = ["Name", "Valid", "Scripts", "Refs", "Assets", "Errors"]
    table = []
    for row in rows:
        table.append(
            [
                row["name"],
                "yes" if row["valid"] else "no",
                str(row["scripts"]),
                str(row["references"]),
                str(row["assets"]),
                "; ".join(row["errors"]),
            ]
        )
    widths = [len(header) for header in headers]
    for row in table:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    print("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("  ".join("-" * width for width in widths))
    for row in table:
        print("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=default_global_root(), help="Global Codex skills root")
    parser.add_argument("--include-system", action="store_true", help="Include built-in skills under .system")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    try:
        result = scan_global_skills(args.root.expanduser().resolve(), include_system=args.include_system)
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print_table(result)
    return 0 if result["invalid"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
