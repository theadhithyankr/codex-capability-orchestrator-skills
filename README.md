<div align="center">

# Codex Capability Orchestrator Skills

**SEO-ready Codex Agent Skills package for capability discovery, MCP registry search, skill benchmarking, dynamic tool integration, and safe test-time tool synthesis.**

![Codex Agent Skills](https://img.shields.io/badge/Codex-Agent%20Skills-111111?style=for-the-badge)
![Capability Discovery](https://img.shields.io/badge/Capability-Discovery-2563eb?style=for-the-badge)
![MCP Registry](https://img.shields.io/badge/MCP-Registry-0f766e?style=for-the-badge)
![Test Time Tool Synthesis](https://img.shields.io/badge/TTE-Tool%20Synthesis-7c3aed?style=for-the-badge)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)
![Node.js 20+](https://img.shields.io/badge/Node.js-20%2B-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![Security First](https://img.shields.io/badge/Security-Default%20Deny-b91c1c?style=for-the-badge)

</div>

Codex Capability Orchestrator Skills is a professional Agent Skills package for Codex that helps AI agents discover, evaluate, install, benchmark, or synthesize missing capabilities without hallucinating tool behavior. It is designed for Codex skill discovery, Skilldex-style registry search, MCP tool comparison, dynamic tool integration, benchmark-driven selection, and safe test-time tool synthesis.

## Why This Repository Exists

Modern AI agents need a disciplined way to decide whether a missing capability should come from an existing Codex skill, an MCP registry, a trusted tool, or a newly synthesized sandboxed utility. This repository provides a reusable Codex meta-skill that turns that decision into a strict workflow with schemas, scoring rubrics, safety boundaries, and deterministic helper scripts.

## Key Features

- Codex-first Agent Skills package named `capability-orchestrator`
- SEO-ready repository positioning for `codex-capability-orchestrator-skills`
- Progressive-disclosure `SKILL.md` with concise routing instructions
- Strict Pydantic and Zod schemas for capability gaps, registry results, benchmarks, judge output, TTE specs, and reusable tool manifests
- Deterministic candidate scoring with weighted benchmark telemetry
- Manifest validation for candidate skills and generated atomic tools
- Sandbox harness generation for Python and Node.js test-time tool synthesis
- Security guidance for untrusted registry metadata, dependency installs, network access, filesystem writes, and host credentials

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

Clone the repository:

```bash
git clone https://github.com/theadhithyankr/codex-capability-orchestrator-skills.git
cd codex-capability-orchestrator-skills
```

Install the skill into your local Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R capability-orchestrator ~/.codex/skills/
```

On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills"
Copy-Item -Recurse -Force .\capability-orchestrator "$env:USERPROFILE\.codex\skills\"
```

Use the skill when a task requires missing capability discovery, Codex skill benchmarking, MCP registry comparison, dynamic tool integration, or safe tool synthesis.

Run the helper scripts locally with Python 3.11 or newer:

```bash
python capability-orchestrator/scripts/validate_manifest.py candidate-skill manifest.json
python capability-orchestrator/scripts/score_candidates.py telemetry.json --pretty
python capability-orchestrator/scripts/synthesize_tool_harness.py --runtime python --entrypoint tool.py --test-command '["python","-m","pytest"]'
```

## What This Helps With

- Codex Agent Skills discovery when a required capability is missing
- MCP registry and Skilldex-style candidate search
- AI agent tool comparison with benchmark telemetry
- Test-time tool synthesis for reusable Python or Node.js utilities
- Sandboxed tool generation with strict security boundaries
- Reliable agent workflows that reject unverifiable tool behavior

## Safety Model

Codex Capability Orchestrator Skills uses a default-deny model. Registry metadata is untrusted, generated code must run in a secure sandbox, and unverifiable evidence is rejected. If a registry response, sandbox result, judge output, or benchmark telemetry is missing or malformed, the skill instructs Codex to say `I don't know` and name the failed dependency.

## Professional Use Cases

- Discover the best Codex skill for a missing capability
- Compare MCP tools or registry candidates before installation
- Benchmark candidate skills with identical tasks and telemetry
- Generate reusable sandboxed tools when no registry match exists
- Validate manifests before persisting or enabling agent capabilities
- Improve AI agent reliability by avoiding invented tool behavior

## Status

This repository contains a complete, verified first version of the `capability-orchestrator` Agent Skills package.

## Suggested GitHub Topics

`codex`, `codex-skills`, `agent-skills`, `ai-agents`, `mcp`, `mcp-registry`, `skilldex`, `tool-synthesis`, `tte`, `capability-discovery`, `agent-tools`, `ai-tooling`
