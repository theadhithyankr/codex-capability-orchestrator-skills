# Capability Orchestrator for Codex Agent Skills

Capability Orchestrator is a professional Agent Skills package for Codex that helps agents discover, evaluate, install, benchmark, or synthesize missing capabilities without hallucinating tool behavior. It is designed for capability discovery, Skilldex-style registry search, MCP tool comparison, dynamic tool integration, and safe test-time tool synthesis.

## Why This Repository Exists

Modern AI agents need a disciplined way to decide whether a missing capability should come from an existing skill, an MCP registry, a trusted tool, or a newly synthesized sandboxed utility. This repository provides a reusable Codex meta-skill that turns that decision into a strict workflow with schemas, scoring rubrics, safety boundaries, and deterministic helper scripts.

## Key Features

- Codex-first Agent Skills package named `capability-orchestrator`
- Progressive-disclosure `SKILL.md` with concise routing instructions
- Strict Pydantic and Zod schemas for capability gaps, registry results, benchmarks, judge output, TTE specs, and reusable tool manifests
- Deterministic candidate scoring with weighted benchmark telemetry
- Manifest validation for candidate skills and generated atomic tools
- Sandbox harness generation for Python and Node.js test-time tool synthesis
- Security guidance for untrusted registry metadata, dependency installs, network access, filesystem writes, and host credentials

## SEO Keywords

Codex Agent Skills, capability orchestrator, AI agent skills, MCP registry, Skilldex, dynamic tool integration, benchmark AI tools, compare agent tools, test-time tool synthesis, TTE, synthesize tools, AI agent capability discovery, sandboxed tool generation, reusable AI tools, agent security boundaries.

## Repository Structure

```text
capability-orchestrator/
├── SKILL.md
├── references/
│   ├── schemas.md
│   ├── evaluation-rubric.md
│   ├── tte-workflow.md
│   └── security-boundaries.md
└── scripts/
    ├── score_candidates.py
    ├── validate_manifest.py
    └── synthesize_tool_harness.py
```

## Quick Start

Copy or install the `capability-orchestrator` folder into a Codex skills directory, then use it when a task requires missing capability discovery, tool benchmarking, MCP registry comparison, or safe tool synthesis.

Run the helper scripts locally with Python 3.11 or newer:

```bash
python capability-orchestrator/scripts/validate_manifest.py candidate-skill manifest.json
python capability-orchestrator/scripts/score_candidates.py telemetry.json --pretty
python capability-orchestrator/scripts/synthesize_tool_harness.py --runtime python --entrypoint tool.py --test-command '["python","-m","pytest"]'
```

## Safety Model

Capability Orchestrator uses a default-deny model. Registry metadata is untrusted, generated code must run in a secure sandbox, and unverifiable evidence is rejected. If a registry response, sandbox result, judge output, or benchmark telemetry is missing or malformed, the skill instructs Codex to say `I don't know` and name the failed dependency.

## Professional Use Cases

- Discover the best Codex skill for a missing capability
- Compare MCP tools or registry candidates before installation
- Benchmark candidate skills with identical tasks and telemetry
- Generate reusable sandboxed tools when no registry match exists
- Validate manifests before persisting or enabling agent capabilities
- Improve AI agent reliability by avoiding invented tool behavior

## Status

This repository contains a complete, verified first version of the `capability-orchestrator` Agent Skills package.
