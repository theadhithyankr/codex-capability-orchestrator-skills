<div align="center">

# Codex Capability Orchestrator Skills

**Codex Agent Skills package for capability discovery, MCP registry search, skill benchmarking, dynamic tool integration, and safe test-time tool synthesis.**

![Codex Agent Skills](https://img.shields.io/badge/Codex-Agent%20Skills-111111?style=for-the-badge)
![Capability Discovery](https://img.shields.io/badge/Capability-Discovery-2563eb?style=for-the-badge)
![MCP Registry](https://img.shields.io/badge/MCP-Registry-0f766e?style=for-the-badge)
![Test Time Tool Synthesis](https://img.shields.io/badge/TTE-Tool%20Synthesis-7c3aed?style=for-the-badge)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)
![Node.js 20+](https://img.shields.io/badge/Node.js-20%2B-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![Security First](https://img.shields.io/badge/Security-Default%20Deny-b91c1c?style=for-the-badge)
![CI](https://img.shields.io/github/actions/workflow/status/theadhithyankr/codex-capability-orchestrator-skills/ci.yml?branch=main&style=for-the-badge&label=CI)
![License](https://img.shields.io/github/license/theadhithyankr/codex-capability-orchestrator-skills?style=for-the-badge)

</div>

Codex Capability Orchestrator Skills is a professional Agent Skills package for Codex that helps AI agents discover, evaluate, install, benchmark, or synthesize missing capabilities without hallucinating tool behavior. It is designed for Codex skill discovery, Skilldex-style registry search, MCP tool comparison, dynamic tool integration, benchmark-driven selection, and safe test-time tool synthesis.

## Why This Repository Exists

Modern AI agents need a disciplined way to decide whether a missing capability should come from an existing Codex skill, an MCP registry, a trusted tool, or a newly synthesized sandboxed utility. This repository provides a reusable Codex meta-skill that turns that decision into a strict workflow with schemas, scoring rubrics, safety boundaries, and deterministic helper scripts.

## Key Features

- Codex-first Agent Skills package named `capability-orchestrator`
- Search-friendly repository positioning for `codex-capability-orchestrator-skills`
- Progressive-disclosure `SKILL.md` with concise routing instructions
- Strict Pydantic and Zod schemas for capability gaps, registry results, benchmarks, judge output, TTE specs, and reusable tool manifests
- Deterministic candidate scoring with weighted benchmark telemetry
- Manifest validation for candidate skills and generated atomic tools
- Sandbox harness generation for Python and Node.js test-time tool synthesis
- Security guidance for untrusted registry metadata, dependency installs, network access, filesystem writes, and host credentials

## Repository Structure

```text
.
├── capability-orchestrator/
│   ├── SKILL.md
│   ├── references/
│   │   ├── tech-registry.json
│   │   ├── schemas.md
│   │   ├── evaluation-rubric.md
│   │   ├── tte-workflow.md
│   │   └── security-boundaries.md
│   └── scripts/
│       ├── benchmark_skills.py
│       ├── codex_skills.py
│       ├── detect_project_stack.py
│       ├── extract_capabilities.py
│       ├── fetch_docs_context.py
│       ├── inspect_skill.py
│       ├── prepare_project.py
│       ├── resolve_capability.py
│       ├── resolve_project.py
│       ├── run_self_test.py
│       ├── scan_global_skills.py
│       ├── score_candidates.py
│       ├── validate_manifest.py
│       └── synthesize_tool_harness.py
├── examples/
│   ├── benchmark/
│   ├── projects/
│   ├── manifests/
│   ├── telemetry/
│   ├── django-skill/
│   ├── laravel-skill/
│   ├── nextjs-skill/
│   ├── valid-skill/
│   └── invalid-skill-missing-description/
├── .github/workflows/ci.yml
├── LICENSE
├── VERSION
├── codex-skills
├── codex-skills.ps1
├── install.sh
└── install.ps1
```

## Quick Start

Clone the repository:

```bash
git clone https://github.com/theadhithyankr/codex-capability-orchestrator-skills.git
cd codex-capability-orchestrator-skills
```

Install with the interactive script:

```bash
./install.sh
```

Install locally without a prompt:

```bash
./install.sh --local
```

On Windows PowerShell:

```powershell
.\install.ps1
```

Windows local install without a prompt:

```powershell
.\install.ps1 -Scope local
```

The installer asks whether to install globally into your Codex skills directory or locally into the current project's `.codex/skills` folder.

Manual global install:

```bash
mkdir -p ~/.codex/skills
cp -R capability-orchestrator ~/.codex/skills/
```

Manual Windows PowerShell install:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills"
Copy-Item -Recurse -Force .\capability-orchestrator "$env:USERPROFILE\.codex\skills\"
```

Use the skill when a task requires missing capability discovery, Codex skill benchmarking, MCP registry comparison, dynamic tool integration, or safe tool synthesis.

Run the deterministic self-test locally with Python 3.11 or newer:

```bash
python capability-orchestrator/scripts/run_self_test.py
```

## Natural Prompt Flow

The primary workflow is prompt-driven. When this skill is installed, Codex should treat a normal build prompt as the source request, prepare project context internally, read the generated manifest/docs, and then implement.

Example user prompts:

- `create a website using Shopify Liquid theme`
- `build a product site with Astro and Drizzle`
- `create a Next.js app with Tailwind CSS and Supabase`
- `add a Django admin dashboard with Celery`

For these prompts, Codex should run project preparation itself. The generated context lives in `.codex/context/manifest.json` and `.codex/context/docs/`.

## Manual Project Preparation

Manual commands are useful for testing the workflow directly. They are not required when Codex is using the skill automatically.

```bash
./codex-skills prepare-project . Create a Next.js product with Tailwind CSS and Supabase
```

On Windows PowerShell:

```powershell
.\codex-skills.ps1 prepare-project . Create a Next.js product with Tailwind CSS and Supabase
```

This extracts capabilities from the prompt and project manifests, searches local and global skills, writes `.codex/context/manifest.json`, and records verified official docs provenance under `.codex/context/docs/`. GitHub discovery stays opt-in:

```bash
./codex-skills prepare-project . Build a Laravel app --allow-github
```

Allow docs discovery for unknown stacks:

```bash
./codex-skills prepare-project . Build with Astro and Drizzle --allow-docs-web
```

Skill installation is also explicit:

```bash
./codex-skills prepare-project . Build a Laravel app --allow-github --install --yes
```

The English prompt can be positional text after the project path, or supplied with `--request` for scripts that prefer explicit flags. Use `--docs-only` to write docs context without resolving skills, or `--skills-only` to resolve skills without docs context. Missing docs sources, unknown capabilities, and unresolved skills are recorded as warnings in the manifest instead of being inferred. With `--allow-docs-web`, unknown capabilities can get reachable HTTPS documentation candidates marked as `web-discovered`; registry entries remain the only sources treated as approved official docs.

## One-Command Self Test

Run the full deterministic self-test suite:

```bash
python capability-orchestrator/scripts/run_self_test.py
```

After global installation, test the installed skill copy directly:

```powershell
python "$env:USERPROFILE\.codex\skills\capability-orchestrator\scripts\run_self_test.py"
```

The self-test compiles every bundled Python script, inspects valid and invalid example skills, validates candidate and atomic tool manifests, scores benchmark telemetry, checks malformed telemetry failure behavior, verifies harness path safety, runs a static skill benchmark, and verifies project preparation context generation.

## Examples

This repository includes fixtures for quick testing:

- `examples/valid-skill`: valid Codex skill with bundled script and reference files
- `examples/invalid-skill-missing-description`: invalid skill fixture for failure testing
- `examples/manifests`: valid candidate skill and atomic tool manifests
- `examples/telemetry`: valid and malformed benchmark telemetry
- `examples/benchmark`: static benchmark spec for comparing skill folders
- `examples/laravel-skill`: Laravel fixture for automatic capability resolution
- `examples/nextjs-skill`: Next.js fixture for automatic project stack resolution
- `examples/django-skill`: Django fixture for automatic project stack resolution
- `examples/projects`: tiny Laravel, Next.js, Django, Flutter, and Go project fixtures for detector tests

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

## Who Should Use This

Use this repository if you build or maintain Codex skills, agent tool registries, MCP integrations, dynamic tool selection workflows, or benchmark-driven AI agent infrastructure.

## What This Does Not Do

- It does not automatically trust or install registry code.
- It does not search GitHub unless `--allow-github` is provided.
- It does not search the web for unknown stack docs unless `--allow-docs-web` is provided.
- It does not install anything unless `--install --yes` is provided.
- It does not prove behavioral success from static inspection alone.
- It does not provide a secure sandbox by itself; it emits contracts and harness manifests for a configured sandbox runner.
- It does not invent registry results, benchmark scores, or tool behavior when evidence is missing.

## Roadmap

- Add richer behavioral benchmark adapters for real task execution.
- Add optional JSON Schema exports alongside Pydantic and Zod schemas.
- Add release archives for direct skill installation.
- Add example MCP registry search transcripts with redacted provenance.

## Status

This repository contains a complete, verified `v0.2.0` release of the `capability-orchestrator` Agent Skills package.

## Suggested GitHub Topics

`codex`, `codex-skills`, `agent-skills`, `ai-agents`, `mcp`, `mcp-registry`, `skilldex`, `tool-synthesis`, `tte`, `capability-discovery`, `agent-tools`, `ai-tooling`
