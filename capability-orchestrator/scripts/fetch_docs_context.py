#!/usr/bin/env python3
"""Write project-local docs context metadata for detected capabilities."""

from __future__ import annotations

import argparse
import html.parser
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REGISTRY_PATH = SKILL_ROOT / "references" / "tech-registry.json"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from extract_capabilities import load_registry  # noqa: E402


def registry_by_id() -> dict[str, dict[str, Any]]:
    registry = load_registry(REGISTRY_PATH)
    return {item["id"]: item for item in registry["capabilities"]}


class LinkParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for key, value in attrs:
            if key == "href" and value:
                self.links.append(value)


def slugify(capability: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in capability).strip("-")


def unwrap_search_url(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if "uddg" in query and query["uddg"]:
        return unquote(query["uddg"][0])
    if parsed.path.startswith("/l/") and "uddg" in query and query["uddg"]:
        return unquote(query["uddg"][0])
    return url


def is_docs_like(url: str, capability: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        return False
    lowered = url.lower()
    slug = slugify(capability)
    docs_terms = ("docs", "documentation", "guide", "learn", "reference")
    if not any(term in lowered for term in docs_terms):
        return False
    return slug in lowered or slug.replace("-", "") in lowered.replace("-", "")


def reachable(url: str, *, timeout: float) -> bool:
    request = Request(url, headers={"User-Agent": "codex-capability-orchestrator/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return 200 <= int(response.status) < 400
    except OSError:
        return False


def search_docs_web(capability: str, *, limit: int, timeout: float) -> list[dict[str, str]]:
    slug = slugify(capability)
    tlds = ("dev", "com", "org", "io", "build", "app", "team", "sh")
    candidates = []
    for tld in tlds:
        candidates.extend(
            [
                f"https://{slug}.{tld}/docs",
                f"https://www.{slug}.{tld}/docs",
                f"https://docs.{slug}.{tld}/",
                f"https://docs.{slug}.{tld}/docs",
                f"https://orm.{slug}.{tld}/docs",
            ]
        )
    search_url = f"https://duckduckgo.com/html/?q={quote_plus(capability + ' official documentation')}"
    try:
        request = Request(search_url, headers={"User-Agent": "codex-capability-orchestrator/1.0"})
        with urlopen(request, timeout=timeout) as response:
            body = response.read(512_000).decode("utf-8", errors="ignore")
        parser = LinkParser()
        parser.feed(body)
        for link in parser.links:
            unwrapped = unwrap_search_url(link)
            if is_docs_like(unwrapped, capability):
                candidates.append(unwrapped)
    except OSError:
        pass

    seen: set[str] = set()
    sources: list[dict[str, str]] = []
    for url in candidates:
        clean = url.split("#", 1)[0]
        if clean in seen or not is_docs_like(clean, capability):
            continue
        seen.add(clean)
        if reachable(clean, timeout=timeout):
            sources.append({"title": f"{capability} documentation candidate", "url": clean})
        if len(sources) >= limit:
            break
    return sources


def write_docs_context(
    project_root: Path,
    capabilities: list[str],
    *,
    allow_web: bool = False,
    web_limit: int = 3,
    timeout: float = 5.0,
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    context_root = root / ".codex" / "context"
    docs_root = context_root / "docs"
    docs_root.mkdir(parents=True, exist_ok=True)
    registry = registry_by_id()
    written: list[dict[str, Any]] = []
    warnings: list[str] = []
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    for capability in capabilities:
        item = registry.get(capability)
        if not item:
            docs = search_docs_web(capability, limit=web_limit, timeout=timeout) if allow_web else []
            if not docs:
                warning = f"no verified docs source for capability: {capability}"
                if not allow_web:
                    warning += " (use --allow-docs-web to search)"
                warnings.append(warning)
                continue
            display_name = capability
            mode = "web-discovered"
            notes = [
                "Documentation candidates were discovered from the web and verified as reachable HTTPS URLs.",
                "Treat these as provenance-bearing candidates, not as registry-approved official docs.",
            ]
        else:
            docs = item.get("docs", [])
            display_name = item.get("display_name", capability)
            mode = "provenance-only"
            notes = [
                "Official documentation source recorded from the local tech registry.",
                "No page content was fetched by this offline-safe command.",
            ]
        doc_record = {
            "capability": capability,
            "display_name": display_name,
            "fetched_at": timestamp,
            "mode": mode,
            "sources": docs,
            "notes": notes,
        }
        destination = docs_root / f"{capability}.json"
        destination.write_text(json.dumps(doc_record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append({"capability": capability, "path": str(destination), "sources": docs})

    return {"docs_root": str(docs_root), "written": written, "warnings": warnings, "generated_at": timestamp}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root")
    parser.add_argument("capabilities", nargs="*", help="Capabilities to write docs context for")
    parser.add_argument("--allow-docs-web", action="store_true", help="Search/probe web docs for unknown capabilities")
    parser.add_argument("--web-limit", type=int, default=3, help="Maximum web docs candidates per capability")
    parser.add_argument("--timeout", type=float, default=5.0, help="Per-request network timeout in seconds")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()
    try:
        result = write_docs_context(
            args.project_root,
            args.capabilities,
            allow_web=args.allow_docs_web,
            web_limit=args.web_limit,
            timeout=args.timeout,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
