#!/usr/bin/env python3
"""Validate capability orchestrator manifests without external dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,126}$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$")


class ValidationError(ValueError):
    pass


def _load(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must be an object")
    return value


def _check_fields(obj: dict[str, Any], allowed: set[str], required: set[str], path: str) -> None:
    extra = set(obj) - allowed
    missing = required - set(obj)
    if extra:
        raise ValidationError(f"{path} has unknown fields: {sorted(extra)}")
    if missing:
        raise ValidationError(f"{path} is missing fields: {sorted(missing)}")


def _str(value: Any, path: str, *, min_len: int = 0, max_len: int | None = None, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{path} must be a string")
    if len(value) < min_len:
        raise ValidationError(f"{path} is too short")
    if max_len is not None and len(value) > max_len:
        raise ValidationError(f"{path} is too long")
    if pattern and not pattern.match(value):
        raise ValidationError(f"{path} has invalid format")
    return value


def _str_list(value: Any, path: str, *, min_len: int = 0) -> list[str]:
    if not isinstance(value, list) or len(value) < min_len:
        raise ValidationError(f"{path} must be a list with at least {min_len} entries")
    for index, item in enumerate(value):
        _str(item, f"{path}[{index}]", min_len=1)
    return value


def _dict_str(value: Any, path: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must be an object")
    for key, item in value.items():
        _str(key, f"{path}.key", min_len=1)
        _str(item, f"{path}.{key}", min_len=1)
    return value


def _schema_obj(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must be an object")
    return value


def validate_candidate_skill_manifest(data: Any) -> dict[str, Any]:
    obj = _object(data, "$")
    allowed = {
        "name",
        "description",
        "version",
        "compatibility",
        "allowed_tools",
        "provenance",
        "capabilities",
        "install",
        "security_notes",
    }
    required = {"name", "description", "version", "provenance", "capabilities"}
    _check_fields(obj, allowed, required, "$")
    _str(obj["name"], "$.name", pattern=SKILL_NAME_RE)
    _str(obj["description"], "$.description", min_len=1, max_len=1000)
    _str(obj["version"], "$.version", pattern=SEMVER_RE)
    if obj.get("compatibility") is not None:
        _str(obj["compatibility"], "$.compatibility", max_len=1000)
    _str_list(obj.get("allowed_tools", []), "$.allowed_tools")
    _str(obj["provenance"], "$.provenance", min_len=1)
    _str_list(obj["capabilities"], "$.capabilities", min_len=1)
    _dict_str(obj.get("install", {}), "$.install")
    _str_list(obj.get("security_notes", []), "$.security_notes")
    return obj


def validate_reusable_atomic_tool_manifest(data: Any) -> dict[str, Any]:
    obj = _object(data, "$")
    allowed = {
        "tool_id",
        "name",
        "version",
        "runtime",
        "entrypoint",
        "input_schema",
        "output_schema",
        "tests",
        "sandbox_requirements",
        "provenance",
    }
    _check_fields(obj, allowed, allowed, "$")
    _str(obj["tool_id"], "$.tool_id", pattern=ID_RE)
    _str(obj["name"], "$.name", min_len=1)
    _str(obj["version"], "$.version", pattern=SEMVER_RE)
    if obj["runtime"] not in {"python", "node"}:
        raise ValidationError("$.runtime must be python or node")
    _str(obj["entrypoint"], "$.entrypoint", min_len=1)
    _schema_obj(obj["input_schema"], "$.input_schema")
    _schema_obj(obj["output_schema"], "$.output_schema")
    _str_list(obj["tests"], "$.tests", min_len=1)
    _str_list(obj["sandbox_requirements"], "$.sandbox_requirements", min_len=1)
    _str(obj["provenance"], "$.provenance", min_len=1)
    return obj


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", choices=["candidate-skill", "atomic-tool"])
    parser.add_argument("manifest_json")
    args = parser.parse_args()

    try:
        data = _load(args.manifest_json)
        if args.schema == "candidate-skill":
            validate_candidate_skill_manifest(data)
        else:
            validate_reusable_atomic_tool_manifest(data)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        return 2

    print(json.dumps({"valid": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
