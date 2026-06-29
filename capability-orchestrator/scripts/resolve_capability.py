#!/usr/bin/env python3
"""Resolve a requested capability to the best available Codex skill candidate."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from inspect_skill import inspect_skill  # noqa: E402
from scan_global_skills import default_global_root, discover_skill_dirs  # noqa: E402

TOKEN_STOPWORDS = {"js", "ts", "css"}


@dataclass(frozen=True)
class Candidate:
    name: str
    source: str
    path: Path
    valid: bool
    relevance: float
    quality: float
    installable: bool
    report: dict[str, Any]

    @property
    def score(self) -> float:
        return round((0.7 * self.relevance) + (0.3 * self.quality), 6)


def tokenize(text: str) -> set[str]:
    chars = [char.lower() if char.isalnum() else " " for char in text]
    return {part for part in "".join(chars).split() if len(part) > 1 and part not in TOKEN_STOPWORDS}


def expand_query(query: str) -> str:
    return " ".join(query_phrases(query))


def query_phrases(query: str) -> list[str]:
    registry_path = SKILL_ROOT / "references" / "tech-registry.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [query]
    for item in registry.get("capabilities", []):
        capability_id = str(item.get("id", "")).lower()
        aliases = [str(alias) for alias in item.get("aliases", [])]
        if query.lower() == capability_id or query.lower() in [alias.lower() for alias in aliases]:
            return [query, str(item.get("display_name", "")), *aliases]
    return [query]


def relevance(query: str, report: dict[str, Any]) -> float:
    expanded_query = expand_query(query)
    query_tokens = tokenize(expanded_query)
    if not query_tokens:
        return 0.0
    frontmatter = report["frontmatter"]
    resource_text = " ".join(
        report["resources"]["scripts"] + report["resources"]["references"] + report["resources"]["assets"]
    )
    haystack = " ".join(
        [
            frontmatter.get("name", ""),
            frontmatter.get("description", ""),
            frontmatter.get("compatibility", ""),
            resource_text,
        ]
    )
    haystack_tokens = tokenize(haystack)
    overlap = len(query_tokens & haystack_tokens) / len(query_tokens)
    haystack_lower = haystack.lower()
    exact_bonus = 0.0
    for phrase in query_phrases(query):
        phrase_lower = phrase.lower()
        is_specific_phrase = any(separator in phrase_lower for separator in (" ", ".", "-")) or phrase_lower == query.lower()
        if phrase_lower and is_specific_phrase and phrase_lower in haystack_lower:
            exact_bonus = 0.25
            break
    return round(min(1.0, overlap + exact_bonus), 6)


def quality(report: dict[str, Any]) -> float:
    if not report["valid"]:
        return 0.0
    result = 0.75
    if report["summary"]["reference_count"]:
        result += 0.1
    if report["summary"]["script_count"]:
        result += 0.1
    if report["warnings"]:
        result -= min(0.25, 0.05 * len(report["warnings"]))
    return round(max(0.0, min(1.0, result)), 6)


def inspect_candidate(path: Path, source: str, query: str, *, installable: bool = True) -> Candidate | None:
    try:
        report = inspect_skill(path)
    except (OSError, ValueError):
        return None
    name = report["frontmatter"].get("name") or path.name
    return Candidate(
        name=name,
        source=source,
        path=path.resolve(),
        valid=report["valid"],
        relevance=relevance(query, report),
        quality=quality(report),
        installable=installable,
        report=report,
    )


def skill_dirs_from_root(root: Path, *, include_system: bool) -> list[Path]:
    try:
        return discover_skill_dirs(root, include_system=include_system)
    except ValueError:
        return []


def discover_local_candidates(query: str, roots: list[Path], *, include_system: bool) -> list[Candidate]:
    candidates: list[Candidate] = []
    for root in roots:
        for skill_dir in skill_dirs_from_root(root.expanduser().resolve(), include_system=include_system):
            candidate = inspect_candidate(skill_dir, "local", query)
            if candidate and candidate.valid and candidate.relevance > 0:
                candidates.append(candidate)
    return candidates


def run_json(args: list[str]) -> Any:
    result = subprocess.run(args, text=True, capture_output=True)
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or result.stdout.strip() or f"command failed: {' '.join(args)}")
    return json.loads(result.stdout)


def find_skill_dirs(repo_dir: Path) -> list[Path]:
    return sorted(path.parent for path in repo_dir.rglob("SKILL.md"))


def discover_github_candidates(query: str, *, limit: int, keep_dir: Path) -> list[Candidate]:
    search_query = f"{query} codex skill OR agent skill"
    repos = run_json(
        [
            "gh",
            "search",
            "repos",
            search_query,
            "--json",
            "fullName,url,description,stargazersCount,updatedAt",
            "--limit",
            str(limit),
        ]
    )
    candidates: list[Candidate] = []
    for index, repo in enumerate(repos):
        full_name = repo.get("fullName")
        url = repo.get("url")
        if not full_name or not url:
            continue
        clone_dir = keep_dir / f"repo-{index}"
        clone = subprocess.run(["git", "clone", "--depth", "1", url, str(clone_dir)], text=True, capture_output=True)
        if clone.returncode != 0:
            continue
        for skill_dir in find_skill_dirs(clone_dir):
            candidate = inspect_candidate(skill_dir, f"github:{full_name}", query)
            if candidate and candidate.valid and candidate.relevance > 0:
                candidates.append(candidate)
    return candidates


def install_candidate(candidate: Candidate, scope: str, target_root: Path | None = None) -> Path:
    if scope == "global":
        root = target_root or default_global_root()
    elif scope == "local":
        root = target_root or (Path.cwd() / ".codex" / "skills")
    else:
        raise ValueError("scope must be global or local")
    destination = root.expanduser().resolve() / candidate.name
    root.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(candidate.path, destination)
    return destination


def candidate_json(candidate: Candidate) -> dict[str, Any]:
    return {
        "name": candidate.name,
        "source": candidate.source,
        "path": str(candidate.path),
        "valid": candidate.valid,
        "relevance": candidate.relevance,
        "quality": candidate.quality,
        "score": candidate.score,
        "scripts": candidate.report["summary"]["script_count"],
        "references": candidate.report["summary"]["reference_count"],
        "assets": candidate.report["summary"]["asset_count"],
        "description": candidate.report["frontmatter"].get("description", ""),
    }


def resolve(args: argparse.Namespace) -> dict[str, Any]:
    roots = [Path(item) for item in args.root]
    if args.global_root:
        roots.append(args.global_root)
    if args.project_root:
        roots.append(args.project_root / ".codex" / "skills")
    candidates = discover_local_candidates(args.capability, roots, include_system=args.include_system)

    github_temp: tempfile.TemporaryDirectory[str] | None = None
    if args.allow_github:
        github_temp = tempfile.TemporaryDirectory()
        candidates.extend(
            discover_github_candidates(args.capability, limit=args.github_limit, keep_dir=Path(github_temp.name))
        )

    ranked = sorted(candidates, key=lambda item: (-item.score, -item.relevance, item.name))
    winner = ranked[0] if ranked else None
    installed_to = None
    if args.install:
        if not winner:
            raise ValueError("no validated candidates found to install")
        if not args.yes:
            raise ValueError("installation requires --yes")
        installed_to = str(install_candidate(winner, args.scope, args.target_root))

    result = {
        "capability": args.capability,
        "searched": {
            "local_roots": [str(path) for path in roots],
            "github": bool(args.allow_github),
        },
        "winner": candidate_json(winner) if winner else None,
        "installed_to": installed_to,
        "candidates": [candidate_json(candidate) for candidate in ranked],
    }
    if github_temp:
        github_temp.cleanup()
    return result


def print_table(result: dict[str, Any]) -> None:
    print(f"Capability: {result['capability']}")
    if result["winner"]:
        print(f"Winner: {result['winner']['name']} ({result['winner']['source']}) score={result['winner']['score']}")
    else:
        print("Winner: none")
    if result["installed_to"]:
        print(f"Installed to: {result['installed_to']}")
    print()
    rows = result["candidates"]
    if not rows:
        print("No validated matching candidates found.")
        return
    headers = ["Name", "Source", "Score", "Relevance", "Quality", "Refs", "Scripts"]
    table = [
        [
            row["name"],
            row["source"],
            str(row["score"]),
            str(row["relevance"]),
            str(row["quality"]),
            str(row["references"]),
            str(row["scripts"]),
        ]
        for row in rows
    ]
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
    parser.add_argument("capability", help="Capability to resolve, e.g. laravel, nextjs, github actions")
    parser.add_argument("--root", action="append", default=[], help="Skills root to search")
    parser.add_argument("--global-root", type=Path, default=default_global_root(), help="Global Codex skills root")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root for .codex/skills search")
    parser.add_argument("--include-system", action="store_true", help="Include built-in .system skills")
    parser.add_argument("--allow-github", action="store_true", help="Search GitHub using gh and clone candidates for inspection")
    parser.add_argument("--github-limit", type=int, default=10, help="Maximum GitHub repositories to inspect")
    parser.add_argument("--install", action="store_true", help="Install the winning validated candidate")
    parser.add_argument("--scope", choices=["global", "local"], default="local", help="Install destination scope")
    parser.add_argument("--target-root", type=Path, help="Override skills install root")
    parser.add_argument("--yes", action="store_true", help="Required for installation")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    try:
        result = resolve(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print_table(result)
    return 0 if result["winner"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
