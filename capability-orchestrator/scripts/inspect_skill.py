#!/usr/bin/env python3
"""Inspect an existing Codex Agent Skill folder and emit a structured report."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")


def _parse_frontmatter(skill_md: Path) -> tuple[dict[str, str], str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    try:
        raw_frontmatter, body = text.split("---\n", 2)[1:]
    except ValueError as exc:
        raise ValueError("SKILL.md frontmatter is not closed") from exc

    fields: dict[str, str] = {}
    for line_number, line in enumerate(raw_frontmatter.splitlines(), start=2):
        if not line.strip():
            continue
        if line[:1].isspace():
            continue
        if ":" not in line:
            raise ValueError(f"frontmatter line {line_number} must use 'key: value'")
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key in fields:
            raise ValueError(f"duplicate frontmatter key: {key}")
        fields[key] = value
    return fields, body


def _relative_files(root: Path, dirname: str) -> list[str]:
    target = root / dirname
    if not target.exists():
        return []
    if not target.is_dir():
        raise ValueError(f"{dirname} exists but is not a directory")
    return sorted(str(path.relative_to(root).as_posix()) for path in target.rglob("*") if path.is_file())


def inspect_skill(path: Path) -> dict[str, Any]:
    root = path.resolve()
    if not root.is_dir():
        raise ValueError(f"{path} is not a directory")
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        raise ValueError("skill folder must contain SKILL.md")

    frontmatter, body = _parse_frontmatter(skill_md)
    errors: list[str] = []
    warnings: list[str] = []

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if not name:
        errors.append("missing required frontmatter field: name")
    elif not SKILL_NAME_RE.match(name):
        errors.append("name must use lowercase letters, digits, and hyphens")
    if not description:
        errors.append("missing required frontmatter field: description")
    elif len(description) > 1000:
        warnings.append("description is longer than 1000 characters")
    if not body.strip():
        warnings.append("SKILL.md body is empty")

    allowed_keys = {"name", "description", "compatibility", "allowed-tools", "metadata"}
    unknown_keys = sorted(set(frontmatter) - allowed_keys)
    if unknown_keys:
        warnings.append(f"unknown frontmatter keys: {', '.join(unknown_keys)}")

    scripts = _relative_files(root, "scripts")
    references = _relative_files(root, "references")
    assets = _relative_files(root, "assets")

    return {
        "path": str(root),
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "frontmatter": frontmatter,
        "resources": {
            "scripts": scripts,
            "references": references,
            "assets": assets,
        },
        "summary": {
            "body_lines": len(body.splitlines()),
            "script_count": len(scripts),
            "reference_count": len(references),
            "asset_count": len(assets),
        },
    }


def candidate_manifest(report: dict[str, Any]) -> dict[str, Any]:
    frontmatter = report["frontmatter"]
    capabilities = [frontmatter["name"]]
    if frontmatter.get("description"):
        capabilities.append(frontmatter["description"][:200])
    return {
        "name": frontmatter["name"],
        "description": frontmatter["description"],
        "version": "0.0.0",
        "compatibility": frontmatter.get("compatibility"),
        "allowed_tools": frontmatter.get("allowed-tools", "").split(),
        "provenance": f"local:{report['path']}",
        "capabilities": capabilities,
        "install": {},
        "security_notes": report["warnings"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", help="Path to an existing skill folder")
    parser.add_argument("--manifest", action="store_true", help="Emit a CandidateSkillManifest JSON object")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    try:
        report = inspect_skill(Path(args.skill_dir))
        if args.manifest:
            if not report["valid"]:
                raise ValueError("cannot emit manifest for invalid skill")
            output = candidate_manifest(report)
        else:
            output = report
    except (OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps(output, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
