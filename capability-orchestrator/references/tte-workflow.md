# Test-Time Tool Synthesis Workflow

Use this workflow only after local skill/tool discovery and registry search fail to produce a safe, validated candidate, or when the user explicitly requests TTE or synthesized tooling.

## Loop

1. Decompose the missing capability into atomic tool contracts.
   - Define one narrow behavior per tool.
   - Specify JSON input and output schemas.
   - Specify allowed side effects and forbidden side effects.
   - Define deterministic tests before implementation.

2. Deduplicate.
   - Search local scripts, skills, MCP tools, and package manifests.
   - If an equivalent tool exists, benchmark it instead of generating new code.

3. Generate a minimal implementation.
   - Prefer Python for filesystem/text/data tasks.
   - Prefer Node.js when the surrounding ecosystem or target APIs are JavaScript-native.
   - Avoid global state, ambient configuration, shell injection, and undeclared network access.
   - Pin or avoid dependencies; do not install untrusted dependencies on the host.

4. Run only inside a secure sandbox.
   - Use a microVM, container, or equivalent isolation boundary configured by the host.
   - Apply CPU, memory, filesystem, network, and timeout limits.
   - Mount only explicit input files and a scratch output directory.

5. Iterate with a fixed retry limit.
   - Default maximum retries: 3.
   - On failure, patch the implementation or tests only when the failure is understood.
   - Stop immediately on sandbox uncertainty, missing logs, parse errors, or suspected policy violation.

6. Persist only validated reusable tools.
   - Save the minimal implementation, tests, and `ReusableAtomicToolManifest`.
   - Include provenance: generation request, test results, sandbox profile, and timestamp.
   - Do not persist one-off, task-private, credential-bearing, or host-specific code.

## Harness Generation

Use `scripts/synthesize_tool_harness.py` to produce a sandbox run manifest. The harness does not provide isolation by itself; it emits a deterministic contract for the configured sandbox runner.

Required inputs:

- Runtime: `python` or `node`
- Entrypoint path
- Test command
- Timeout milliseconds
- Read-only input mounts
- Writable output directory

Required outputs:

- Strict JSON harness manifest
- Explicit resource limits
- Network policy
- Command arguments as arrays, never shell strings

## Stop Conditions

Say `I don't know` and name the failed dependency when:

- The sandbox runner is unavailable.
- The generated implementation cannot be tested.
- Test results are malformed or missing.
- The synthesized tool requires unsafe privileges.
- The requested capability cannot be decomposed into a bounded atomic contract.
