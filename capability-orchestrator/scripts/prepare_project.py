#!/usr/bin/env python3
"""Prepare project-local Codex context for a requested technology stack."""

from __future__ import annotations

import argparse
import json
import sys
from argparse import Namespace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from extract_capabilities import extract_capabilities  # noqa: E402
from fetch_docs_context import write_docs_context  # noqa: E402
from resolve_capability import resolve  # noqa: E402
from scan_global_skills import default_global_root  # noqa: E402


def timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_skills(args: argparse.Namespace, project_root: Path, capabilities: list[str]) -> list[dict[str, Any]]:
    resolutions = []
    target_root = args.target_root
    if args.install and args.scope == "local" and target_root is None:
        target_root = project_root / ".codex" / "skills"
    for capability in capabilities:
        resolution_args = Namespace(
            capability=capability,
            root=args.root,
            global_root=args.global_root,
            project_root=project_root,
            include_system=args.include_system,
            allow_github=args.allow_github,
            github_limit=args.github_limit,
            install=args.install,
            scope=args.scope,
            target_root=target_root,
            yes=args.yes,
            json=True,
            pretty=False,
        )
        resolutions.append(resolve(resolution_args))
    return resolutions


def prepare_project(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.expanduser().resolve()
    if not project_root.is_dir():
        raise ValueError(f"project root is not a directory: {project_root}")
    if args.docs_only and args.skills_only:
        raise ValueError("--docs-only and --skills-only cannot be combined")
    if args.install and not args.yes:
        raise ValueError("installation requires --yes")

    context_root = project_root / ".codex" / "context"
    context_root.mkdir(parents=True, exist_ok=True)

    request = args.request or " ".join(args.prompt).strip()
    extracted = extract_capabilities(project_root, request)
    capabilities = [item["id"] for item in extracted["capabilities"]]
    warnings = []
    for item in extracted["capabilities"]:
        if not item["known"]:
            warnings.append(f"unknown capability from project/request: {item['id']}")

    docs_result = {"docs_root": str(context_root / "docs"), "written": [], "warnings": [], "generated_at": timestamp()}
    if not args.skills_only:
        docs_result = write_docs_context(
            project_root,
            capabilities,
            allow_web=args.allow_docs_web,
            web_limit=args.docs_web_limit,
            timeout=args.docs_timeout,
        )
        warnings.extend(docs_result["warnings"])

    resolutions: list[dict[str, Any]] = []
    if not args.docs_only:
        resolutions = resolve_skills(args, project_root, capabilities)
        for resolution in resolutions:
            if not resolution["winner"]:
                warnings.append(f"no matching skill found for capability: {resolution['capability']}")

    installed = [item["installed_to"] for item in resolutions if item.get("installed_to")]
    manifest_path = context_root / "manifest.json"
    manifest = {
        "schema_version": "1.0.0",
        "generated_at": timestamp(),
        "manifest_path": str(manifest_path),
        "project_root": str(project_root),
        "request": request,
        "options": {
            "allow_github": bool(args.allow_github),
            "install": bool(args.install),
            "docs_only": bool(args.docs_only),
            "skills_only": bool(args.skills_only),
            "include_system": bool(args.include_system),
            "allow_docs_web": bool(args.allow_docs_web),
        },
        "detected_capabilities": extracted["capabilities"],
        "docs": docs_result,
        "skill_resolutions": resolutions,
        "installed_skills": installed,
        "warnings": warnings,
        "sources": {
            "tech_registry": extracted["registry"],
            "local_roots": [str(Path(item)) for item in args.root],
            "global_root": str(args.global_root) if args.global_root else None,
            "project_skills_root": str(project_root / ".codex" / "skills"),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def print_summary(result: dict[str, Any]) -> None:
    print(f"Project: {result['project_root']}")
    print(f"Manifest: {result['manifest_path']}")
    capabilities = result["detected_capabilities"]
    if capabilities:
        print("Capabilities:")
        for item in capabilities:
            sources = ", ".join(item["sources"])
            print(f"  - {item['id']} confidence={item['confidence']} sources={sources}")
    else:
        print("Capabilities: none")
    if result["skill_resolutions"]:
        print("Skills:")
        for resolution in result["skill_resolutions"]:
            winner = resolution["winner"]
            label = winner["name"] if winner else "none"
            print(f"  - {resolution['capability']}: {label}")
    if result["docs"]["written"]:
        print("Docs:")
        for doc in result["docs"]["written"]:
            print(f"  - {doc['capability']}: {doc['path']}")
    if result["warnings"]:
        print("Warnings:")
        for warning in result["warnings"]:
            print(f"  - {warning}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to prepare")
    parser.add_argument("prompt", nargs="*", help="English build request to mine for technologies")
    parser.add_argument("--request", default="", help="User build request containing desired technologies")
    parser.add_argument("--root", action="append", default=[], help="Additional skills root to search")
    parser.add_argument("--global-root", type=Path, default=default_global_root(), help="Global Codex skills root")
    parser.add_argument("--include-system", action="store_true", help="Include built-in .system skills")
    parser.add_argument("--allow-github", action="store_true", help="Search GitHub with gh")
    parser.add_argument("--github-limit", type=int, default=10, help="Maximum GitHub repositories to inspect per capability")
    parser.add_argument("--install", action="store_true", help="Install winning validated candidates")
    parser.add_argument("--scope", choices=["global", "local"], default="local", help="Install destination scope")
    parser.add_argument("--target-root", type=Path, help="Override skills install root")
    parser.add_argument("--yes", action="store_true", help="Required for installation")
    parser.add_argument("--docs-only", action="store_true", help="Write docs context without resolving skills")
    parser.add_argument("--skills-only", action="store_true", help="Resolve skills without writing docs context")
    parser.add_argument("--allow-docs-web", action="store_true", help="Search/probe web docs for unknown capabilities")
    parser.add_argument("--docs-web-limit", type=int, default=3, help="Maximum web docs candidates per capability")
    parser.add_argument("--docs-timeout", type=float, default=5.0, help="Per-request docs discovery timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    try:
        result = prepare_project(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
