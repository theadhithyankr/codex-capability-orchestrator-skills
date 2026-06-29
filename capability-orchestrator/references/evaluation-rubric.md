# Evaluation Rubric

Use this rubric before selecting, installing, enabling, or persisting any candidate capability.

## Weighted Score

Composite score is:

```text
0.45 * task_success
+ 0.25 * reliability
+ 0.15 * latency
+ 0.10 * token_efficiency
+ 0.05 * maintainability_security_fit
```

Definitions:

- `task_success`: fraction of benchmark tasks completed with required artifacts and passing deterministic checks.
- `reliability`: `1 - error_rate`, adjusted down for flaky retries, non-deterministic outputs, malformed responses, or missing evidence.
- `latency`: normalized score in `[0, 1]`; lower measured wall-clock latency is better, but timeout or missing telemetry is `0`.
- `token_efficiency`: normalized score in `[0, 1]`; lower total token use for equivalent success is better.
- `maintainability_security_fit`: review score for minimal scope, clear provenance, small dependency surface, sandbox compatibility, and least-privilege behavior.

## Benchmark Protocol

1. Evaluate each candidate in an isolated subprocess, sub-agent, container, or sandbox with no shared mutable state.
2. Use identical prompts, files, environment variables, timeout limits, and task order for every candidate.
3. Capture telemetry per candidate per task: exit status, duration, tokens when available, tool calls, artifacts, stderr/stdout summaries, deterministic test results, and provenance.
4. Prefer deterministic tests over LLM judges. Use LLM-as-judge only for qualitative dimensions that deterministic checks cannot express.
5. Validate judge output against `LLMJudgeResult` before using it. Reject free-form commentary as scoring evidence.
6. Reject any candidate that requires host credentials, uncontrolled network access, privileged filesystem writes, or unreviewed dependency installation.
7. Run `scripts/score_candidates.py` on strict telemetry JSON to rank valid candidates.

## Failure Handling

- Missing telemetry: candidate is invalid.
- Malformed JSON: candidate is invalid.
- Sandbox timeout: the task receives `success_score = 0`, `latency_score = 0`, and reliability is capped at `0.25`.
- Registry provenance missing: candidate is invalid.
- Judge schema validation failure: ignore the judge result; do not backfill a qualitative score.
- Candidate ties: choose the safer, smaller, more maintainable candidate. If still tied, prefer local or trusted provenance over unknown registry provenance.
