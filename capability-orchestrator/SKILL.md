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
