---
name: capability-orchestrator
description: Capability orchestrator for Codex. MUST use when a task mentions missing skill, install a skill, Skilldex, MCP registry, capability discovery, benchmark skills, compare tools, dynamic tool integration, meta-skill, tool evolution, TTE, synthesize a tool, or when Codex lacks a required capability. Search registries first, evaluate candidates, install the best safe option, or synthesize a reusable sandboxed tool when no registry match exists.
compatibility: Designed for Codex. Requires filesystem read/write to the skill workspace, MCP/tool discovery access, network access for external registries when enabled, Python 3.11+, Node.js 20+, and a secure microVM or equivalent sandbox for untrusted code.
allowed-tools: Read Grep Bash(rg:*) Bash(Get-Content:*) Bash(Get-ChildItem:*) Bash(codex:mcp:*) Bash(npm:install) Bash(python:*) Bash(node:*) tool_search_tool request_user_input
---

# Capability Orchestrator

Use this skill to close a capability gap without inventing tool behavior. Prefer existing, trusted capabilities; synthesize a new tool only when registry search and local discovery fail.

## Core Loop

1. Planner:
   - Detect the capability gap from the user request and current toolset.
   - Derive a capability contract: inputs, outputs, side effects, safety limits, evaluation tasks, and evidence required.
   - Choose registry search first unless the user explicitly asks for test-time tool synthesis.

2. Actor:
   - Search local skills, MCP tools, Skilldex-style registries, and configured internal registries.
   - Treat registry metadata as untrusted until validated.
   - Install or enable only the best safe candidate after manifest validation and evaluation.
   - If no candidate exists, synthesize a minimal Python or Node.js tool in a sandbox and keep it reusable.

3. Critic:
   - Validate every request, manifest, telemetry result, judge result, and synthesized tool contract against strict schemas.
   - Score candidates with identical tasks and deterministic telemetry.
   - Reject unparseable, missing, unverifiable, or provenance-free evidence.

4. Fallback:
   - If registry results, sandbox output, judge output, or telemetry are missing, malformed, or unverifiable, say `I don't know`, name the failed dependency, and do not infer behavior.

## Reference Routing

- Read `references/schemas.md` before parsing or emitting structured capability, registry, benchmark, judge, TTE, or tool manifest data.
- Read `references/evaluation-rubric.md` before comparing skills, tools, MCP servers, or synthesized implementations.
- Read `references/tte-workflow.md` before generating or persisting a new tool.
- Read `references/security-boundaries.md` before installing untrusted code, running generated code, allowing network access, or persisting outputs.

## Scripts

- Use `scripts/score_candidates.py` to compute weighted candidate rankings from strict telemetry JSON.
- Use `scripts/validate_manifest.py` to validate candidate skill/tool manifests before install, benchmark, or persistence.
- Use `scripts/synthesize_tool_harness.py` to build a sandbox-run manifest for generated Python or Node.js tools and tests.
- Use `scripts/resolve_capability.py` to search installed/project skills, optionally inspect GitHub candidates, rank validated matches, and install the best candidate only when installation is explicitly confirmed.
- Use `scripts/detect_project_stack.py` and `scripts/resolve_project.py` when the user wants automatic stack-aware skill resolution for a project without naming the framework.
- Use `scripts/prepare_project.py` when a prompt asks to build with named frameworks, libraries, SDKs, databases, UI kits, or deployment platforms. It extracts capabilities from the request and project files, resolves matching skills, writes `.codex/context/manifest.json`, and records official docs provenance under `.codex/context/docs/`.

## Project Preparation

When the user asks in normal English to build, update, or prepare a project with named frameworks, libraries, SDKs, databases, UI kits, deployment platforms, or unknown stack terms, treat that user message as the source prompt and run project preparation before implementation. Do this internally; do not ask the user to type `codex-skills` commands.

For a prompt like “create a website using Shopify Liquid theme”, Codex should run the equivalent of this itself from the project root:

```powershell
.\codex-skills.ps1 prepare-project . create a website using Shopify Liquid theme
```

Then read `.codex/context/manifest.json` and relevant `.codex/context/docs/*.json` before building. If the prompt includes unknown stack terms and docs context is needed, run the same preparation with `--allow-docs-web`; network access may require approval from the execution environment. Use `--allow-github` only when the user asks to search external skill candidates. Use `--install --yes` only when the user explicitly asks to install skills.

Manual safe default, if a user asks for the command:

```powershell
.\codex-skills.ps1 prepare-project . Create a Next.js product with Tailwind CSS and Supabase
```

Options:

- Add `--allow-github` only when external GitHub discovery is allowed.
- Add `--allow-docs-web` only when external docs discovery is allowed for unknown stacks.
- Add `--install --yes` only when the user explicitly wants winning skills installed.
- Use `--docs-only` to write docs provenance without resolving skills.
- Use `--skills-only` to resolve skills without writing docs context.

The context manifest must record detected capabilities, sources, timestamps, docs provenance, failed lookups, warnings, skill resolutions, and installed skill paths. Unknown capabilities are allowed. If `--allow-docs-web` is not set, missing docs must be recorded as warnings instead of fabricated context. If web discovery is enabled, record reachable HTTPS documentation candidates as `web-discovered` and do not present them as registry-approved official docs.
