# Ablation Ladder: Incremental Value of Each Stage

## Purpose

A stage remains in the system only if it provides measurable value for an owner rule that justifies its latency, memory, privacy exposure, maintenance and cost. The ladder is run on the same locked replay corpus and hardware profile. Components are added in this order:

```text
A0 Detector + Tracker + Rules
 -> A1 + Temporal Model
 -> A2 + Anomaly Candidate Generation
 -> A3 + VLM Review
 -> A4 + Sensor Integration
```

The ladder is not a claim that every deployment should contain all stages. It is a controlled way to discover where each stage earns its place.

## Arms

### A0: Detector + Tracker + Rules

- sampled closed-set detector;
- tracker and camera geometry;
- deterministic temporal state and rule engine;
- local evidence and health.

This is the correctness and resource reference.

### A1: Add temporal model

Use only for rules whose visual action or sequence cannot be supported by A0. Candidate arms may include a small temporal classifier, pose/feature TCN, TimeSformer or another selected model. Keep rule logic deterministic after the model emits an action candidate.

### A2: Add anomaly candidate generation

Add AE, CLIP or another novelty signal only as a trigger for review or higher-rate inference. It must not define the violation label. Compare both `candidate-triggered` and `candidate-not-triggered` cases, including permitted unusual behavior.

### A3: Add VLM review

Send only bounded evidence permitted by policy. Require schema validation, frame/timestamp citations, deterministic decoding where feasible and explicit `advisory` status. Compare small and larger candidates only after A3 proves value over A2.

### A4: Add sensor integration

Add gate contacts, access-control, POS, PLC, task or schedule events where available. This arm may replace a visual predicate rather than merely add another signal. Measure whether sensor fusion reduces visual compute, false alerts or identity ambiguity.

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
| A0 | Meets rule observation and policy gates at minimum resource | all critical rules have acceptable rule-event recall and alert latency | always-on baseline |
| A1 | Recovers difficult temporal/action cases without unacceptable FP/cost | improvement is material on rules that need it | selective per-rule |
| A2 | Reduces expensive work or improves recall on hard candidates | candidate precision and compute savings offset false triggers and drift | optional trigger |
| A3 | Improves bounded review accuracy/evidence quality | grounded review value exceeds privacy, cost, latency and license burden | optional advisory |
| A4 | Replaces unreliable visual inference or reduces cost/risk | sensor freshness, availability and integration reliability pass gates | preferred where authoritative |

## Decision record template

```yaml
ablation_run: A0-to-A1
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
