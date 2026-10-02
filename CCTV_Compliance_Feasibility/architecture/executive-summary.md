# Submission-Ready Executive Architecture Summary

**Study status:** Feasibility study with empirical evaluation protocol; measurements pending where target data/hardware are unavailable.

## Recommendation

Use a **Hierarchical Event Driven Architecture with Sensor Integration and Optional VLM Escalation**. The recommended Core CV path is:

```text
CCTV -> decode and health -> sampled perception -> tracker and trajectory
     -> typed observations/events -> temporal state -> deterministic owner rules
     -> bounded evidence -> alert and human review
```

Evaluate optional capabilities as parallel branches around Core CV:

```text
Core CV
├── + Temporal
├── + Anomaly
├── + VLM review
└── + Sensor integration
```

Sensor integration may replace a visual predicate, corroborate it or expose a different failure mode. It is not presumed to be an additive final stage. The internal A/B/C/D/E labels remain comparison shorthand, not the architecture name.

Deterministic policy evaluation is authoritative. VLM output is advisory, bounded by evidence and unable to override the event ledger or final rule result. Unknown and degraded states remain explicit.

## Direct answers to the supervisor questions

| Question | Feasibility answer | Evidence status |
|---|---|---|
| What architecture should be used? | Hierarchical event and rule architecture with a small Core CV path, optional temporal/anomaly/VLM branches and a parallel sensor arm where justified | Architecture is specified; P0 contract replay measured |
| Which AI capabilities are actually required? | A detector or other observation source, a tracker/trajectory state, and only the temporal/action model needed by a specific rule. Anomaly and VLM are optional candidates. | P0 used precomputed detections; visual model accuracy remains open |
| What can plausibly run on CPU? | Decode, sampling, health, small sampled detector after measurement, simple tracking, geometry, timers, deterministic rules and bounded evidence | Architectural feasibility; target CPU capacity pending |
| What needs GPU acceleration? | Training, larger video transformers, dense models and most continuous VLM use. A small exported detector may or may not need GPU depending on target workload | No target-device GPU result produced |
| Where does quantisation help? | It can reduce model memory and bandwidth and may reduce latency when kernels are supported. It does not prove CPU suitability or preserve event quality automatically | FP32/FP16/INT8 comparison pending |
| What should stay on edge? | Raw streams, routine perception, tracker/state, deterministic rules, health, ring buffer and routine evidence by default | Privacy architecture; site deployment pending |
| What can move to cloud? | Approved training, batch analytics and selective redacted evidence review where policy, residency, cost and egress permit | No cloud run; policy boundary specified |
| How is privacy preserved? | Minimise raw retention, keep raw video and keys local by default, send only approved metadata or redacted evidence, restrict access and audit egress | Design and synthetic metadata evidence path measured; governance approval pending |
| How are owner-defined rules represented? | Versioned schema-validated expressions over typed events with temporal operators, exceptions, authorization, schedules, cooldowns and human-review actions | Selected synthetic rule fixtures measured for conformance |
| How are temporal events represented? | Source and monotonic-derived time bounds, transitions, intervals, provenance, quality and explicit unknown/degraded state | P0 replay emitted typed events and an open interval up to stream end |
| How is a violation verified? | Reproduce the event trace, evaluate deterministic conditions, confirm health/quality and attach bounded evidence. Human review applies for ambiguous or high-impact policy actions | P0 confirmed a selected synthetic policy fixture and produced an evidence hash |
| What evidence is produced? | Event IDs, rule/version, timestamps, source frame IDs, condition trace, model/config provenance, hashes, privacy classification and reviewer state | P0 produced a bounded metadata manifest; visual evidence quality pending |
| How are false positives and false negatives handled? | Use rule-level precision/recall, false alerts and misses per camera-hour, unknown rate, hard negatives, calibration, error review and correction/retraction | Selected synthetic behavior checks exist; site rates pending |
| What is already demonstrated? | 11/11 checked synthetic rule fixtures, 2/2 malformed-input checks, deterministic replay, model-neutral stage flow, bounded evidence hash, one-track zone dwell path and inspection of an existing SceneSolver artifact | Measured in `experiments/p0/`; not complete rule correctness or deployment performance |
| What remains to be experimentally validated? | Real detector accuracy, target-camera generalisation, tracking quality, hardware latency/memory/power, quantisation, VLM value, sensor value, cost and camera capacity | Open |
| What should the first prototype contain? | One camera or replay source, one lightweight perception adapter, one tracker/trajectory path, typed events, deterministic rules, bounded evidence, replay tests and health/degraded handling | P0 demonstrates the contract; customer/site data still required |

## P0 evidence boundary

The P0 pass is intentionally small. It does not retrain SceneSolver, implement a production detector, build a dashboard, create multi-camera infrastructure, deploy to cloud or add VLM infrastructure.

Measured P0 artifacts:

- selected rule-fixture conformance over synthetic traces;
- model-neutral structured replay from sampling through evidence, including an open interval at stream end;
- a specialised CV contract path using precomputed detections;
- inspection of the existing SceneSolver report artifact and its reproducibility blockers.

The P0 results support **feasible architecture**, not **proven deployment performance**. Existing SceneSolver accuracy figures remain repository evidence with their support, split and task limitations. Quantisation and VLM review remain pending because an exact model/runtime/hardware or readily available lightweight model was not present.

## SceneSolver disposition

SceneSolver remains a reference baseline and candidate component library. Its committed report artifact records 3366 frames at 30 FPS, 320x240 resolution and 112.2 seconds, with 44 anomaly records. P0 measured artifact parsing, but did not claim inference runtime, stage timing, memory, target hardware capacity or owner-rule accuracy. The source video and complete inference prerequisites are not available in this checkout.

## First prototype boundary

The first real-data prototype should be an offline replay or one-camera edge experiment:

1. use an approved site-like clip or structured observation source;
2. run one small detector or observation adapter and one simple tracker;
3. emit typed observations and temporal intervals;
4. evaluate two or three owner-approved rules deterministically;
5. capture bounded evidence and health/degraded state;
6. measure rule quality, latency, memory, storage and failure cases;
7. evaluate temporal, anomaly, VLM and sensor branches independently only when a rule justifies them.

This is a feasibility measurement package, not a production service. No camera count, FPS, cost, legal-compliance result or deployment SLO is claimed without target data and hardware.
