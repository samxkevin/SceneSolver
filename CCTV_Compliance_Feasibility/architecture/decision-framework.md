# Component Retention Decision Framework

## Required sequence

Every model, stage, sensor integration and runtime must pass this sequence:

```text
measurement
  -> incremental value
  -> resource cost
  -> privacy review
  -> licensing review
  -> reliability gate
  -> operational approval
```

Failure at any mandatory gate blocks production retention. A component can remain a research arm without being placed in the target architecture.

## Gate definitions

### 1. Measurement

Run the component on locked, representative data and exact target hardware. Record accuracy, calibration, latency, memory, power, thermals, failures, evidence quality and camera concurrency. Published numbers are context only.

### 2. Incremental value

Compare against the immediately simpler arm using the same inputs and labels. A component must improve a declared owner outcome, reduce resource use, replace a riskier signal, or materially improve evidence/review. Aggregate benchmark gains alone do not qualify.

### 3. Resource cost

Include model load, decoder, preprocessing, postprocessing, tracker, queues, evidence, report generation, storage and maintenance. Evaluate p95 and worst-case behavior, not only average throughput.

### 4. Privacy review

List new raw frames, crops, audio, embeddings, identity joins, cloud egress, retention and linkage risks. Minimise or reject data that is not needed for the owner rule.

### 5. Licensing review

Complete the model/dependency manifest. Verify code, weights, adapters, text encoders, runtime, datasets, attribution, redistribution, commercial restrictions and deployment compatibility.

### 6. Reliability gate

Meet per-rule observation/event recall, false-alert budget, unknown handling, drift monitoring, failure recovery and evidence sufficiency. High-impact actions require human review as determined by policy.

### 7. Operational approval

Document update/rollback, observability, owner sign-off, security threat model, support burden, retention and incident response.

## Decision outcomes

| Outcome | Meaning |
|---|---|
| `retain-core` | Required for an approved rule and all gates pass |
| `retain-selective` | Valuable only on triggers, rules, cameras or review queues |
| `retain-advisory` | Useful to humans, cannot create or execute policy decisions |
| `research-only` | Interesting or measurable, but at least one production gate is open or failed |
| `reject` | No incremental value, blocked license/privacy, or unacceptable reliability/cost |

## Conservative defaults

- S0 SceneSolver remains a reference baseline.
- Deterministic policy evaluation remains authoritative.
- VLMs remain optional and advisory.
- Unknown/degraded states remain explicit.
- Sensor evidence is preferred over inferred state when trustworthy.
- No hardware, camera-count, FPS, cost or accuracy number is promoted without a traceable measurement.
