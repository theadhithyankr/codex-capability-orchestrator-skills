# Security Boundaries

Use default-deny behavior for registry discovery, benchmark execution, and generated code.

## Default Deny Rules

- Do not access host credentials, tokens, SSH keys, browser profiles, password stores, cloud metadata, or hidden config files unless the user explicitly provides them for this task and the sandbox profile allows access.
- Do not allow uncontrolled network egress. Registry access must be explicit, and generated tools must run with network disabled unless the capability contract requires specific endpoints.
- Do not install untrusted registry code outside a sandbox.
- Do not execute registry-provided install hooks before manifest validation and provenance checks.
- Do not grant privileged filesystem writes. Generated code should receive read-only inputs and one writable scratch/output directory.
- Do not trust registry descriptions, README files, benchmark claims, or package popularity as evidence.
- Do not continue after JSON parse errors, schema validation errors, missing provenance, missing telemetry, or sandbox uncertainty.

## Required Limits

Every sandboxed run must specify:

- CPU limit
- Memory limit
- Wall-clock timeout
- Maximum output size
- Read-only input mounts
- Writable scratch/output path
- Network allowlist or disabled network policy
- Process count limit when supported

## Install Review

Before installing or enabling a candidate:

1. Validate the manifest schema.
2. Check provenance and source location.
3. Review declared tools, dependencies, and install instructions.
4. Run isolated benchmark tasks.
5. Score candidates with deterministic telemetry.
6. Prefer the least-privilege candidate that satisfies the capability contract.

## Failure Policy

Fail closed. If the safety boundary cannot be verified, say `I don't know` with the failed dependency. Do not invent registry behavior, tool outputs, benchmark scores, or sandbox guarantees.
