#!/usr/bin/env python3
"""Extract normalized project capabilities from prompts and repository manifests."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REGISTRY_PATH = SKILL_ROOT / "references" / "tech-registry.json"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from detect_project_stack import detect_project_stack  # noqa: E402


STOPWORDS = {
    "a",
    "an",
    "and",
    "app",
    "application",
    "build",
    "create",
    "for",
    "in",
    "product",
    "project",
    "site",
    "the",
    "to",
    "with",
}


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    capabilities = data.get("capabilities")
    if not isinstance(capabilities, list):
        raise ValueError("tech registry is missing capabilities")
    return data


def alias_map(registry: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in registry["capabilities"]:
        capability_id = item["id"]
        result[capability_id.lower()] = capability_id
        for alias in item.get("aliases", []):
            result[str(alias).lower()] = capability_id
    return result


def canonicalize(term: str, aliases: dict[str, str]) -> str:
    normalized = re.sub(r"\s+", " ", term.strip().lower())
    if normalized in aliases:
        return aliases[normalized]
    hyphen = normalized.replace(" ", "-")
    if hyphen in aliases:
        return aliases[hyphen]
    packageish = normalized.lstrip("@")
    for segment in re.split(r"[/]", packageish):
        if segment in aliases:
            return aliases[segment]
        prefix = segment.split("-", 1)[0]
        if prefix in aliases:
            return aliases[prefix]
    return hyphen


def add_capability(
    found: dict[str, dict[str, Any]],
    capability: str,
    *,
    source: str,
    evidence: str,
    confidence: float,
    aliases: dict[str, str],
) -> None:
    canonical = canonicalize(capability, aliases)
    if not canonical or canonical in STOPWORDS:
        return
    item = found.setdefault(
        canonical,
        {"id": canonical, "confidence": 0.0, "sources": [], "evidence": [], "known": canonical in aliases.values()},
    )
    item["confidence"] = max(float(item["confidence"]), confidence)
    if source not in item["sources"]:
        item["sources"].append(source)
    if evidence not in item["evidence"]:
        item["evidence"].append(evidence)
    item["known"] = bool(item["known"] or canonical in aliases.values())


def extract_from_request(request: str, aliases: dict[str, str]) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {}
    lowered = request.lower()
    for alias, canonical in sorted(aliases.items(), key=lambda pair: len(pair[0]), reverse=True):
        if re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", lowered):
            matches.setdefault(canonical, []).append(alias)
    for raw in re.findall(r"[A-Za-z][A-Za-z0-9+.#-]{1,30}", request):
        token = raw.lower()
        if token not in STOPWORDS and token in aliases:
            matches.setdefault(aliases[token], []).append(raw)
    return matches


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _load_toml(path: Path) -> dict[str, Any]:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def package_names(project_root: Path) -> list[tuple[str, str]]:
    names: list[tuple[str, str]] = []
    package_json = _load_json(project_root / "package.json")
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        deps = package_json.get(key)
        if isinstance(deps, dict):
            names.extend((name, f"package.json {key}") for name in deps)

    composer = _load_json(project_root / "composer.json")
    for key in ("require", "require-dev"):
        deps = composer.get(key)
        if isinstance(deps, dict):
            names.extend((name.split("/")[-1], f"composer.json {key}") for name in deps)
            names.extend((name, f"composer.json {key}") for name in deps)

    pyproject = _load_toml(project_root / "pyproject.toml")
    project = pyproject.get("project")
    if isinstance(project, dict):
        deps = project.get("dependencies")
        if isinstance(deps, list):
            names.extend((str(dep).split("=")[0].strip(), "pyproject.toml dependencies") for dep in deps)
    poetry = pyproject.get("tool", {}).get("poetry", {}) if isinstance(pyproject.get("tool"), dict) else {}
    if isinstance(poetry, dict):
        deps = poetry.get("dependencies")
        if isinstance(deps, dict):
            names.extend((name, "pyproject.toml poetry dependencies") for name in deps)

    requirements = _text(project_root / "requirements.txt")
    for line in requirements.splitlines():
        clean = re.split(r"[<>=~!]", line.strip(), maxsplit=1)[0]
        if clean and not clean.startswith("#"):
            names.append((clean, "requirements.txt"))

    gemfile = _text(project_root / "Gemfile")
    for match in re.findall(r"gem\s+['\"]([^'\"]+)['\"]", gemfile):
        names.append((match, "Gemfile"))

    go_mod = _text(project_root / "go.mod")
    for line in go_mod.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("module ", "go ", "require (", ")")):
            names.append((stripped.split()[0].split("/")[-1], "go.mod"))

    cargo = _load_toml(project_root / "Cargo.toml")
    deps = cargo.get("dependencies")
    if isinstance(deps, dict):
        names.extend((name, "Cargo.toml dependencies") for name in deps)

    pubspec = _text(project_root / "pubspec.yaml")
    for line in pubspec.splitlines():
        if re.match(r"^\s{2}[a-zA-Z_][\w-]*:", line):
            names.append((line.split(":", 1)[0].strip(), "pubspec.yaml"))

    return names


def extract_capabilities(project_root: Path, request: str = "") -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"project root is not a directory: {root}")
    registry = load_registry()
    aliases = alias_map(registry)
    found: dict[str, dict[str, Any]] = {}

    if request:
        for capability, matched_aliases in extract_from_request(request, aliases).items():
            add_capability(
                found,
                capability,
                source="request",
                evidence=", ".join(sorted(set(matched_aliases))),
                confidence=0.95,
                aliases=aliases,
            )
        for raw in re.findall(r"[A-Za-z][A-Za-z0-9+.#-]{2,30}", request):
            lowered = raw.lower()
            if lowered in STOPWORDS or lowered in aliases or lowered == "css":
                continue
            if raw[0].isupper() or any(char in raw for char in ".#+-"):
                add_capability(
                    found,
                    raw,
                    source="request",
                    evidence=raw,
                    confidence=0.4,
                    aliases=aliases,
                )

    stack_result = detect_project_stack(root)
    for item in stack_result["detected"]:
        for part in re.split(r"\s+", item["stack"]):
            add_capability(
                found,
                part,
                source="project",
                evidence="; ".join(item["evidence"]),
                confidence=item["confidence"],
                aliases=aliases,
            )
        add_capability(
            found,
            item["stack"],
            source="project",
            evidence="; ".join(item["evidence"]),
            confidence=item["confidence"],
            aliases=aliases,
        )

    for name, source in package_names(root):
        canonical = canonicalize(name, aliases)
        if canonical in aliases.values():
            add_capability(found, canonical, source="project", evidence=f"{source}: {name}", confidence=0.9, aliases=aliases)
        elif len(canonical) > 2 and canonical not in STOPWORDS:
            add_capability(found, canonical, source="project", evidence=f"{source}: {name}", confidence=0.35, aliases=aliases)

    capabilities = sorted(found.values(), key=lambda item: (-item["confidence"], item["id"]))
    return {
        "project_root": str(root),
        "request": request,
        "capabilities": capabilities,
        "registry": str(REGISTRY_PATH),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to inspect")
    parser.add_argument("--request", default="", help="User request to mine for named technologies")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()
    try:
        result = extract_capabilities(args.project_root, args.request)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if result["capabilities"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
