#!/usr/bin/env python3
"""Emit a deterministic sandbox harness manifest for synthesized tools."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import PurePosixPath
from typing import Any


def _mount(value: str) -> dict[str, str]:
    if ":" not in value:
        raise ValueError("mounts must use host_path:guest_path")
    host, guest = value.split(":", 1)
    if not host or not guest:
        raise ValueError("mount host and guest paths must be non-empty")
    return {"host_path": host, "guest_path": guest, "mode": "ro"}


def _command(runtime: str, entrypoint: str) -> list[str]:
    if runtime == "python":
        return ["python", entrypoint]
    if runtime == "node":
        return ["node", entrypoint]
    raise ValueError("runtime must be python or node")


def _require_relative(path: str, field: str) -> str:
    parsed = PurePosixPath(path.replace("\\", "/"))
    if parsed.is_absolute() or ".." in parsed.parts:
        raise ValueError(f"{field} must be a relative path without '..'")
    if not path:
        raise ValueError(f"{field} must be non-empty")
    return path


def build_manifest(args: argparse.Namespace) -> dict[str, Any]:
    entrypoint = _require_relative(args.entrypoint, "entrypoint")
    output_dir = _require_relative(args.output_dir, "output_dir")
    test_command = json.loads(args.test_command)
    if not isinstance(test_command, list) or not all(isinstance(item, str) and item for item in test_command):
        raise ValueError("test_command must be a JSON array of non-empty strings")

    return {
        "schema_version": "1.0.0",
        "runtime": args.runtime,
        "network": args.network,
        "commands": {
            "tool": _command(args.runtime, entrypoint),
            "test": test_command,
        },
        "limits": {
            "timeout_ms": args.timeout_ms,
            "cpu_count": args.cpu_count,
            "memory_mb": args.memory_mb,
            "max_output_bytes": args.max_output_bytes,
            "process_count": args.process_count,
        },
        "filesystem": {
            "read_only_mounts": [_mount(item) for item in args.mount],
            "writable_output_dir": output_dir,
        },
        "safety": {
            "host_credentials": "deny",
            "ambient_environment": "deny",
            "shell": "deny",
            "fail_closed_on_missing_logs": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", required=True, choices=["python", "node"])
    parser.add_argument("--entrypoint", required=True, help="Relative generated tool entrypoint")
    parser.add_argument("--test-command", required=True, help='JSON array command, e.g. ["python","-m","pytest"]')
    parser.add_argument("--output-dir", default="out", help="Relative writable output directory")
    parser.add_argument("--mount", action="append", default=[], help="Read-only mount as host_path:guest_path")
    parser.add_argument("--network", default="disabled", help="Network policy: disabled or allowlist name")
    parser.add_argument("--timeout-ms", type=int, default=120000)
    parser.add_argument("--cpu-count", type=int, default=1)
    parser.add_argument("--memory-mb", type=int, default=512)
    parser.add_argument("--max-output-bytes", type=int, default=1048576)
    parser.add_argument("--process-count", type=int, default=16)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    try:
        for field in ("timeout_ms", "cpu_count", "memory_mb", "max_output_bytes", "process_count"):
            if getattr(args, field) <= 0:
                raise ValueError(f"{field.replace('_', '-')} must be positive")
        manifest = build_manifest(args)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(manifest, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
