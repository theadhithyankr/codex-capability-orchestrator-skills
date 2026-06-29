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
![CI](https://img.shields.io/github/actions/workflow/status/theadhithyankr/codex-capability-orchestrator-skills/ci.yml?branch=main&style=for-the-badge&label=CI)
![License](https://img.shields.io/github/license/theadhithyankr/codex-capability-orchestrator-skills?style=for-the-badge)

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
.
├── capability-orchestrator/
│   ├── SKILL.md
│   ├── references/
│   │   ├── schemas.md
│   │   ├── evaluation-rubric.md
│   │   ├── tte-workflow.md
│   │   └── security-boundaries.md
│   └── scripts/
│       ├── benchmark_skills.py
│       ├── codex_skills.py
│       ├── detect_project_stack.py
│       ├── inspect_skill.py
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

Run the helper scripts locally with Python 3.11 or newer:

```bash
./codex-skills scan-global
./codex-skills detect .
./codex-skills resolve-project .
./codex-skills resolve laravel
python capability-orchestrator/scripts/run_self_test.py
python capability-orchestrator/scripts/validate_manifest.py candidate-skill manifest.json
python capability-orchestrator/scripts/score_candidates.py telemetry.json --pretty
python capability-orchestrator/scripts/synthesize_tool_harness.py --runtime python --entrypoint tool.py --test-command '["python","-m","pytest"]'
```

## Codex Skills CLI

Use the top-level CLI wrapper for common tasks:

```bash
./codex-skills scan-global
./codex-skills scan-global --include-system
./codex-skills self-test
./codex-skills benchmark-examples --pretty
./codex-skills inspect ~/.codex/skills/example-skill --pretty
./codex-skills detect .
./codex-skills resolve-project .
./codex-skills resolve laravel
./codex-skills resolve laravel --allow-github
./codex-skills resolve laravel --allow-github --install --scope local --yes
```

On Windows PowerShell:

```powershell
.\codex-skills.ps1 scan-global
.\codex-skills.ps1 scan-global --include-system
.\codex-skills.ps1 self-test
.\codex-skills.ps1 benchmark-examples --pretty
.\codex-skills.ps1 inspect "$env:USERPROFILE\.codex\skills\example-skill" --pretty
.\codex-skills.ps1 detect .
.\codex-skills.ps1 resolve-project .
.\codex-skills.ps1 resolve laravel
.\codex-skills.ps1 resolve laravel --allow-github
.\codex-skills.ps1 resolve laravel --allow-github --install --scope local --yes
```

The CLI is intentionally small and repo-native. It gives Codex CLI users a single predictable interface for scanning installed skills, inspecting a skill folder, running self-tests, and trying the included benchmark fixture.

## Automatic Skill Resolution

Resolve an explicit capability such as Laravel, Next.js, Django, Rails, Expo, React, FastAPI, Spring Boot, Flutter, Go, Rust, or any other stack term against installed global and project skills:

```bash
./codex-skills resolve laravel
```

Search local skills first, then optionally search GitHub for better validated candidates:

```bash
./codex-skills resolve laravel --allow-github
```

Install the best validated candidate into the current project's `.codex/skills` folder:

```bash
./codex-skills resolve laravel --allow-github --install --scope local --yes
```

On Windows PowerShell:

```powershell
.\codex-skills.ps1 resolve laravel --allow-github --install --scope local --yes
```

The resolver compares candidates by relevance and static quality. It validates `SKILL.md`, checks bundled resources, ranks matches, and installs only when `--install --yes` is provided. GitHub search is opt-in with `--allow-github` because remote code is untrusted until inspected.

## Automatic Project Stack Detection

Detect the current project's stack:

```bash
./codex-skills detect .
```

Detect the stack and resolve matching skills automatically:

```bash
./codex-skills resolve-project .
```

Search GitHub for better candidates and install the best validated skill into the project:

```bash
./codex-skills resolve-project . --allow-github --install --scope local --yes
```

On Windows PowerShell:

```powershell
.\codex-skills.ps1 resolve-project . --allow-github --install --scope local --yes
```

Detection currently recognizes common project files for Laravel/PHP, Next.js, React, Expo React Native, Vue/Nuxt, Angular, SvelteKit, Vite, Django, FastAPI, Flask, Rails/Ruby, Go, Rust, Java/Spring Boot, Flutter, and Dart. Unknown stacks still work through explicit resolution, for example `./codex-skills resolve wordpress --allow-github`.

## One-Command Self Test

Run the full deterministic self-test suite:

```bash
python capability-orchestrator/scripts/run_self_test.py
```

The self-test compiles every bundled Python script, inspects valid and invalid example skills, validates candidate and atomic tool manifests, scores benchmark telemetry, checks malformed telemetry failure behavior, verifies harness path safety, and runs a static skill benchmark.

## Test Existing Skills

Scan globally installed user skills:

```bash
./codex-skills scan-global
```

Include built-in system skills:

```bash
./codex-skills scan-global --include-system
```

Inspect any existing Codex skill folder:

```bash
python capability-orchestrator/scripts/inspect_skill.py ~/.codex/skills/example-skill --pretty
```

On Windows PowerShell:

```powershell
python .\capability-orchestrator\scripts\inspect_skill.py "$env:USERPROFILE\.codex\skills\example-skill" --pretty
```

Convert an existing skill into a local candidate manifest:

```bash
python capability-orchestrator/scripts/inspect_skill.py ~/.codex/skills/example-skill --manifest --pretty > candidate.json
python capability-orchestrator/scripts/validate_manifest.py candidate-skill candidate.json
```

This checks whether the skill has a valid `SKILL.md`, usable frontmatter, and discoverable bundled resources. Behavioral benchmarking still requires benchmark tasks and telemetry, because a static skill inspection cannot prove whether the skill succeeds on real user work.

## Benchmark Skill Candidates

Run the included static benchmark fixture:

```bash
python capability-orchestrator/scripts/benchmark_skills.py examples/benchmark/static-skills.json --pretty
```

The benchmark runner inspects each candidate skill folder and emits `BenchmarkTelemetry`-compatible JSON plus a weighted ranking. Static benchmarking is useful for repository hygiene and first-pass candidate comparison; it does not replace real task execution.

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
- `examples/projects`: tiny Laravel, Next.js, and Django project fixtures for detector tests

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

This repository contains a complete, verified `v0.1.0` release of the `capability-orchestrator` Agent Skills package.

## Suggested GitHub Topics

`codex`, `codex-skills`, `agent-skills`, `ai-agents`, `mcp`, `mcp-registry`, `skilldex`, `tool-synthesis`, `tte`, `capability-discovery`, `agent-tools`, `ai-tooling`
