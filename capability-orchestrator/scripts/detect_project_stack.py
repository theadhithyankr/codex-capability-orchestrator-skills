#!/usr/bin/env python3
"""Detect common project stacks from repository files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return ""


def _package_has(package_json: dict[str, Any], *names: str) -> bool:
    deps = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = package_json.get(key)
        if isinstance(value, dict):
            deps.update(value)
    return any(name in deps for name in names)


def detect_project_stack(project_root: Path) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"project root is not a directory: {root}")

    detections: list[dict[str, Any]] = []

    composer = _load_json(root / "composer.json")
    composer_require = {}
    for key in ("require", "require-dev"):
        value = composer.get(key)
        if isinstance(value, dict):
            composer_require.update(value)
    if "laravel/framework" in composer_require or (root / "artisan").exists():
        detections.append({"stack": "laravel", "confidence": 1.0, "evidence": ["composer.json laravel/framework or artisan"]})
    elif composer:
        detections.append({"stack": "php", "confidence": 0.55, "evidence": ["composer.json"]})

    package_json = _load_json(root / "package.json")
    if package_json:
        if _package_has(package_json, "next"):
            detections.append({"stack": "nextjs", "confidence": 1.0, "evidence": ["package.json next"]})
        if _package_has(package_json, "tailwindcss", "@tailwindcss/postcss", "@tailwindcss/vite"):
            detections.append({"stack": "tailwindcss", "confidence": 0.95, "evidence": ["package.json tailwindcss"]})
        if _package_has(package_json, "@supabase/supabase-js", "@supabase/ssr", "supabase"):
            detections.append({"stack": "supabase", "confidence": 0.95, "evidence": ["package.json supabase"]})
        if _package_has(package_json, "react-native", "expo"):
            if _package_has(package_json, "expo"):
                detections.append({"stack": "expo", "confidence": 0.95, "evidence": ["package.json expo"]})
            if _package_has(package_json, "react-native"):
                detections.append({"stack": "react-native", "confidence": 0.95, "evidence": ["package.json react-native"]})
        if _package_has(package_json, "react") and not any(item["stack"] == "nextjs" for item in detections):
            detections.append({"stack": "react", "confidence": 0.8, "evidence": ["package.json react"]})
        if _package_has(package_json, "vue", "nuxt"):
            detections.append({"stack": "vue nuxt", "confidence": 0.85, "evidence": ["package.json vue/nuxt"]})
        if _package_has(package_json, "@angular/core"):
            detections.append({"stack": "angular", "confidence": 0.9, "evidence": ["package.json @angular/core"]})
        if _package_has(package_json, "svelte", "@sveltejs/kit"):
            detections.append({"stack": "sveltekit", "confidence": 0.9, "evidence": ["package.json svelte"]})
        if _package_has(package_json, "vite"):
            detections.append({"stack": "vite", "confidence": 0.7, "evidence": ["package.json vite"]})
        if not detections:
            detections.append({"stack": "nodejs", "confidence": 0.55, "evidence": ["package.json"]})

    pyproject = _text(root / "pyproject.toml")
    requirements = _text(root / "requirements.txt")
    manage_py = (root / "manage.py").exists()
    python_text = " ".join([pyproject, requirements])
    if "django" in python_text or manage_py:
        detections.append({"stack": "django", "confidence": 1.0, "evidence": ["django dependency or manage.py"]})
    elif "fastapi" in python_text:
        detections.append({"stack": "fastapi", "confidence": 0.95, "evidence": ["fastapi dependency"]})
    elif "flask" in python_text:
        detections.append({"stack": "flask", "confidence": 0.9, "evidence": ["flask dependency"]})
    elif pyproject or requirements:
        detections.append({"stack": "python", "confidence": 0.55, "evidence": ["python dependency file"]})

    gemfile = _text(root / "Gemfile")
    if "rails" in gemfile or (root / "config" / "application.rb").exists():
        detections.append({"stack": "rails", "confidence": 1.0, "evidence": ["Gemfile rails or config/application.rb"]})
    elif gemfile:
        detections.append({"stack": "ruby", "confidence": 0.55, "evidence": ["Gemfile"]})

    go_mod = _text(root / "go.mod")
    if go_mod:
        stack = "go"
        confidence = 0.6
        if "gin-gonic/gin" in go_mod:
            stack = "go gin"
            confidence = 0.85
        detections.append({"stack": stack, "confidence": confidence, "evidence": ["go.mod"]})

    cargo = _text(root / "Cargo.toml")
    if cargo:
        detections.append({"stack": "rust", "confidence": 0.6, "evidence": ["Cargo.toml"]})

    if (root / "pom.xml").exists() or (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        java_text = " ".join([_text(root / "pom.xml"), _text(root / "build.gradle"), _text(root / "build.gradle.kts")])
        stack = "spring boot" if "spring-boot" in java_text else "java"
        confidence = 0.9 if stack == "spring boot" else 0.55
        detections.append({"stack": stack, "confidence": confidence, "evidence": ["java build file"]})

    if (root / "pubspec.yaml").exists():
        pubspec = _text(root / "pubspec.yaml")
        detections.append({"stack": "flutter" if "flutter:" in pubspec else "dart", "confidence": 0.85, "evidence": ["pubspec.yaml"]})

    unique: dict[str, dict[str, Any]] = {}
    for item in detections:
        existing = unique.get(item["stack"])
        if not existing or item["confidence"] > existing["confidence"]:
            unique[item["stack"]] = item

    ordered = sorted(unique.values(), key=lambda item: (-item["confidence"], item["stack"]))
    return {"project_root": str(root), "detected": ordered}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".", help="Project root to inspect")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    try:
        result = detect_project_stack(Path(args.project_root))
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if result["detected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
