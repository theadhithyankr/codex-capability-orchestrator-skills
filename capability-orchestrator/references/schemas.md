# Schemas

Use these contracts for all capability orchestration data. Fail closed when required fields are missing, extra fields appear, values use the wrong type, enum values are unknown, URLs are not provenance-bearing, or JSON cannot be parsed.

## Shared Rules

- IDs: `^[a-z0-9][a-z0-9._-]{1,126}$`
- Semver: `^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$`
- URLs: absolute `https://`, `file://`, or registry-specific opaque IDs with documented provenance.
- Timestamps: RFC 3339 UTC.
- Scores: floats in `[0, 1]`.
- Durations: non-negative milliseconds.
- Token counts: non-negative integers.
- `additionalProperties` / unknown keys: reject unless explicitly allowed.

## Pydantic Models

```python
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, conint, confloat


Score = confloat(ge=0, le=1)
Millis = conint(ge=0)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CapabilityGapRequest(StrictModel):
    request_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,126}$")
    user_goal: str = Field(min_length=1, max_length=4000)
    missing_capability: str = Field(min_length=1, max_length=1000)
    required_inputs: list[str] = Field(default_factory=list)
    required_outputs: list[str] = Field(default_factory=list)
    allowed_side_effects: list[str] = Field(default_factory=list)
    forbidden_side_effects: list[str] = Field(default_factory=list)
    evidence_required: list[str] = Field(default_factory=list)
    preferred_runtime: Literal["python", "node", "either"] = "either"


class RegistrySearchQuery(StrictModel):
    query_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,126}$")
    capability: str = Field(min_length=1, max_length=1000)
    registries: list[str] = Field(min_length=1)
    constraints: dict[str, str] = Field(default_factory=dict)
    max_results: conint(ge=1, le=50) = 10


class RegistrySearchResult(StrictModel):
    query_id: str
    registry: str
    candidate_id: str
    name: str
    version: str
    description: str
    provenance_url: HttpUrl | str
    manifest_url: HttpUrl | str
    trust_level: Literal["local", "trusted", "unknown", "untrusted"]
    capabilities: list[str]


class CandidateSkillManifest(StrictModel):
    name: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")
    description: str = Field(min_length=1, max_length=1000)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$")
    compatibility: str | None = Field(default=None, max_length=1000)
    allowed_tools: list[str] = Field(default_factory=list)
    provenance: str = Field(min_length=1)
    capabilities: list[str] = Field(min_length=1)
    install: dict[str, str] = Field(default_factory=dict)
    security_notes: list[str] = Field(default_factory=list)


class BenchmarkTask(StrictModel):
    task_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,126}$")
    prompt: str = Field(min_length=1, max_length=4000)
    expected_artifacts: list[str] = Field(default_factory=list)
    deterministic_checks: list[str] = Field(default_factory=list)
    qualitative_checks: list[str] = Field(default_factory=list)
    timeout_ms: Millis = 120000


class BenchmarkTelemetry(StrictModel):
    candidate_id: str
    task_id: str
    success_score: Score
    error_rate: Score
    reliability_score: Score
    latency_ms: Millis
    latency_score: Score
    input_tokens: conint(ge=0)
    output_tokens: conint(ge=0)
    token_efficiency_score: Score
    maintainability_security_score: Score
    evidence: list[str] = Field(min_length=1)


class LLMJudgeResult(StrictModel):
    judge_id: str
    candidate_id: str
    task_id: str
    qualitative_score: Score
    rationale: str = Field(min_length=1, max_length=2000)
    rubric_dimensions: dict[str, Score]
    evidence_refs: list[str] = Field(min_length=1)


class TTESynthesisSpec(StrictModel):
    spec_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,126}$")
    atomic_contract: str = Field(min_length=1, max_length=2000)
    runtime: Literal["python", "node"]
    inputs_schema: dict[str, Any]
    outputs_schema: dict[str, Any]
    tests: list[BenchmarkTask] = Field(min_length=1)
    sandbox_profile: str = Field(min_length=1)
    max_retries: conint(ge=0, le=5) = 3


class ReusableAtomicToolManifest(StrictModel):
    tool_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,126}$")
    name: str
    version: str = Field(pattern=r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$")
    runtime: Literal["python", "node"]
    entrypoint: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    tests: list[str] = Field(min_length=1)
    sandbox_requirements: list[str] = Field(min_length=1)
    provenance: str
```

## Zod Schemas

```typescript
import { z } from "zod";

const score = z.number().min(0).max(1);
const millis = z.number().int().nonnegative();
const id = z.string().regex(/^[a-z0-9][a-z0-9._-]{1,126}$/);
const semver = z.string().regex(/^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$/);
const strict = <T extends z.ZodRawShape>(shape: T) => z.object(shape).strict();

export const CapabilityGapRequest = strict({
  request_id: id,
  user_goal: z.string().min(1).max(4000),
  missing_capability: z.string().min(1).max(1000),
  required_inputs: z.array(z.string()).default([]),
  required_outputs: z.array(z.string()).default([]),
  allowed_side_effects: z.array(z.string()).default([]),
  forbidden_side_effects: z.array(z.string()).default([]),
  evidence_required: z.array(z.string()).default([]),
  preferred_runtime: z.enum(["python", "node", "either"]).default("either"),
});

export const RegistrySearchQuery = strict({
  query_id: id,
  capability: z.string().min(1).max(1000),
  registries: z.array(z.string()).min(1),
  constraints: z.record(z.string()).default({}),
  max_results: z.number().int().min(1).max(50).default(10),
});

export const RegistrySearchResult = strict({
  query_id: z.string(),
  registry: z.string(),
  candidate_id: z.string(),
  name: z.string(),
  version: z.string(),
  description: z.string(),
  provenance_url: z.string().min(1),
  manifest_url: z.string().min(1),
  trust_level: z.enum(["local", "trusted", "unknown", "untrusted"]),
  capabilities: z.array(z.string()),
});

export const CandidateSkillManifest = strict({
  name: z.string().regex(/^[a-z0-9][a-z0-9-]{1,62}$/),
  description: z.string().min(1).max(1000),
  version: semver,
  compatibility: z.string().max(1000).nullable().optional(),
  allowed_tools: z.array(z.string()).default([]),
  provenance: z.string().min(1),
  capabilities: z.array(z.string()).min(1),
  install: z.record(z.string()).default({}),
  security_notes: z.array(z.string()).default([]),
});

export const BenchmarkTask = strict({
  task_id: id,
  prompt: z.string().min(1).max(4000),
  expected_artifacts: z.array(z.string()).default([]),
  deterministic_checks: z.array(z.string()).default([]),
  qualitative_checks: z.array(z.string()).default([]),
  timeout_ms: millis.default(120000),
});

export const BenchmarkTelemetry = strict({
  candidate_id: z.string(),
  task_id: z.string(),
  success_score: score,
  error_rate: score,
  reliability_score: score,
  latency_ms: millis,
  latency_score: score,
  input_tokens: z.number().int().nonnegative(),
  output_tokens: z.number().int().nonnegative(),
  token_efficiency_score: score,
  maintainability_security_score: score,
  evidence: z.array(z.string()).min(1),
});

export const LLMJudgeResult = strict({
  judge_id: z.string(),
  candidate_id: z.string(),
  task_id: z.string(),
  qualitative_score: score,
  rationale: z.string().min(1).max(2000),
  rubric_dimensions: z.record(score),
  evidence_refs: z.array(z.string()).min(1),
});

export const TTESynthesisSpec = strict({
  spec_id: id,
  atomic_contract: z.string().min(1).max(2000),
  runtime: z.enum(["python", "node"]),
  inputs_schema: z.record(z.unknown()),
  outputs_schema: z.record(z.unknown()),
  tests: z.array(BenchmarkTask).min(1),
  sandbox_profile: z.string().min(1),
  max_retries: z.number().int().min(0).max(5).default(3),
});

export const ReusableAtomicToolManifest = strict({
  tool_id: id,
  name: z.string(),
  version: semver,
  runtime: z.enum(["python", "node"]),
  entrypoint: z.string(),
  input_schema: z.record(z.unknown()),
  output_schema: z.record(z.unknown()),
  tests: z.array(z.string()).min(1),
  sandbox_requirements: z.array(z.string()).min(1),
  provenance: z.string(),
});
```
