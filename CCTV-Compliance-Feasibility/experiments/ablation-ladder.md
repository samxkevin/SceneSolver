# Ablation Ladder: Incremental Value of Each Stage

## Purpose

A stage remains in the system only if it provides measurable value for an owner rule that justifies its latency, memory, privacy exposure, maintenance and cost. Each branch is evaluated against the same Core CV reference on the same locked replay corpus and hardware profile. The branches are parallel experiments, not a required additive sequence:

```text
Core CV: Detector + Tracker + Rules
├── + Temporal Model
├── + Anomaly Candidate Generation
├── + VLM Review
└── + Sensor Integration
```

The ladder is not a claim that every deployment should contain all stages. It is a controlled way to discover where each stage earns its place.

## Arms

### Core CV: Detector + Tracker + Rules

- sampled closed-set detector;
- tracker and camera geometry;
- deterministic temporal state and rule engine;
- local evidence and health.

This is the correctness and resource reference.

### Temporal branch: Add temporal model

Use only for rules whose visual action or sequence cannot be supported by Core CV. Candidate arms may include a small temporal classifier, pose/feature TCN, TimeSformer or another selected model. Keep rule logic deterministic after the model emits an action candidate.

### Anomaly branch: Candidate generation

Add AE, CLIP or another novelty signal only as a trigger for review or higher-rate inference. It must not define the violation label. Compare both candidate-triggered and candidate-not-triggered cases, including permitted unusual behavior.

### VLM branch: Advisory review

Send only bounded evidence permitted by policy. Require schema validation, frame/timestamp citations, deterministic decoding where feasible and explicit advisory status. It cannot create or override an authoritative policy decision.

### Sensor branch: Sensor integration

Add gate contacts, access-control, POS, PLC, task or schedule events only where available and approved. This branch may replace a visual predicate, corroborate it or expose a different failure mode. It is not automatically placed after the other branches and is not required for every deployment.

## Required measurements for every step

| Dimension | Measurement |
|---|---|
| Incremental quality | delta observation recall, delta rule-event recall, delta precision/F1, delta false alerts per camera-hour, delta misses per camera-hour, delta unknown rate |
| Temporal quality | delta time-to-detect, boundary error, persistence confirmation and duplicate-alert rate |
| Runtime | added p50/p95/p99 stage and end-to-end alert latency, frames processed and queue age |
| Resources | added peak RAM/VRAM/shared memory, model load/startup, power and thermal effect |
| Evidence | evidence usability, condition citation coverage, report generation time and storage/event |
| Privacy | new data classes, raw-frame exposure, embeddings/appearance/audio use, egress volume and retention |
| Operations | configuration burden, failure cases, recovery, model/config update effort and monitoring complexity |
| Cost | amortised hardware, cloud inference, bandwidth/egress, storage and maintenance delta |
| Licensing | new code/weight/dependency restrictions and attribution burden |

## Incremental-value table

| Stage | Incremental value required to retain it | Retain only if | Default disposition |
|---|---|---|---|
| Core CV | Meets rule observation and policy gates at minimum resource | all critical rules have acceptable rule-event recall and alert latency | reference path |
| Temporal | Recovers difficult temporal/action cases without unacceptable FP/cost | improvement is material on rules that need it | selective per-rule |
| Anomaly | Reduces expensive work or improves recall on hard candidates | candidate precision and compute savings offset false triggers and drift | optional trigger |
| VLM | Improves bounded review accuracy/evidence quality | grounded review value exceeds privacy, cost, latency and license burden | optional advisory |
| Sensor integration | Replaces unreliable visual inference or reduces cost/risk | sensor freshness, availability and integration reliability pass gates | parallel optional arm |

## Decision record template

```yaml
ablation_run: Core-CV-vs-branch
rule_id: exact-rule
hardware: exact-device
base_commit: hash
added_component: exact-model-or-sensor
quality_delta:
  rule_event_recall: null
  false_alerts_per_camera_hour: null
  misses_per_camera_hour: null
  unknown_rate: null
resource_delta:
  p95_alert_latency_ms: null
  peak_ram_mb: null
  peak_vram_mb: null
  watts: null
privacy_delta:
  new_data_classes: []
  egress_bytes: null
cost_delta:
  cost_per_camera_hour: null
license_status: pending
reliability_gate: pass|fail|unknown
retained: true|false|pending
reason: ""
```

## Stop rule

If a component has no measurable incremental value, fails a reliability or license gate, or cannot justify its privacy and operational cost, remove it from the candidate production architecture even if it is technically impressive.
