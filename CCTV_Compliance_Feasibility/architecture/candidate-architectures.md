# Candidate Architectures and Comparative Decision

## Evaluation dimensions

Every candidate is judged on routine-event reliability, event latency, privacy exposure, deterministic replay, configurability, interpretability, hardware cost, model update burden, multi-camera scaling and failure containment.

## A - Single multimodal model

```text
video or sampled frames -> VLM/video foundation model -> violation text/JSON -> alert
```

**Solves:** open-ended descriptions, visual question answering, analyst assistance and low-volume retrospective review.
**Consumes:** pixels/video plus a prompt and possibly context.
**Produces:** free text or model-generated structured output unless constrained.
**Training:** zero-shot may work for broad concepts; site-specific reliability usually needs evaluation and possibly adaptation.
**Strengths:** broad vocabulary, quick exploration, useful when the event ontology is unknown.
**Weaknesses:** expensive continuous inference, hallucination/omission, weak temporal precision, poor auditability, uncertain calibration, privacy risk, and no natural guarantee that a rule is evaluated consistently. It cannot infer a badge event or hidden permission without another data source.

**Disposition:** optional review layer; reject as the default compliance authority.

## B - Specialised CV pipeline

```text
detector -> tracker -> optional action/pose/OCR -> deterministic geometry/timers/rules -> evidence
```

**Solves:** fixed object/person/zone/state requirements with low latency and repeatability.
**Strengths:** efficient, quantisable, interpretable intermediate data, easy to replay and test, rules change without retraining.
**Weaknesses:** requires an explicit perception inventory and labelled data for difficult actions; brittle under domain shift; open-ended semantics are out of scope.

**Disposition:** default for routine events and edge-first deployment.

## C - Hierarchical pipeline

```text
always-on cheap stages -> temporal state -> rule engine -> selective expensive stage
```

The expensive stage may be invoked on uncertainty, a candidate event, a new camera, a difficult class, a policy-approved review request or an offline audit sample.

**Strengths:** concentrates compute and privacy exposure; preserves deterministic compliance logic; supports CPU baseline and GPU/cloud upgrade paths.
**Costs:** more orchestration, queueing, observability and calibration work; trigger design can create selection bias.

**Disposition:** leading architecture.

## D - Hybrid deterministic + VLM

Same as C, but the VLM receives a bounded, redacted evidence package and must return a schema-constrained assessment with cited frame/timestamp references. The deterministic rule engine remains authoritative.

**Appropriate for:** “is the required action visibly complete?”, ambiguous object/action labels, report drafting and analyst search.
**Not appropriate for:** final authorization, identity adjudication, continuous timers, or irreversible automated decisions.

## E - Sensor-assisted compliance system

```text
CCTV perception + access control / gate contact / POS / PLC / schedule events
 -> event bus -> rule engine -> evidence
```

This is a fundamentally important alternative. A gate contact sensor may be more reliable and cheaper than a vision gate classifier; a badge reader may be safer than appearance-based identity. CCTV can supply context and evidence rather than infer every state.

**Disposition:** preferred whenever trusted non-video signals exist.

## Decision matrix

| Criterion | A: VLM core | B: specialised | C: hierarchical | D: hybrid | E: sensor-assisted |
|---|---:|---:|---:|---:|---:|
| Routine edge cost | Poor | Good | Good | Good | Excellent where sensors exist |
| Open-world semantics | Good | Poor | Selective | Good selectively | Depends on CCTV branch |
| Rule determinism/replay | Poor | Excellent | Excellent | Excellent if VLM is advisory | Excellent |
| Privacy minimisation | Poor unless heavily redacted | Excellent | Excellent | Good | Excellent |
| New policy without retraining | Prompt-dependent, unsafe | Excellent for supported predicates | Excellent | Good with validation | Excellent |
| Temporal precision | Variable | Good | Good | Good for deterministic branch | Excellent for sensor state |
| Interpretability | Weak | Strong intermediate data | Strong | Mixed | Strong |
| Development complexity | Medium initial / high validation | Medium | High | High | High integration |
| Recommended role | review/search | core baseline | target architecture | selective extension | preferred data source |

## Decision

The descriptive target is **Hierarchical Event Driven Architecture with Sensor Integration and Optional VLM Escalation**. Internally, this maps to C as the hierarchical core, D as optional controlled escalation, and E as a parallel sensor-integration arm where trusted sensors are available. E is not presumed to be an additive final stage. Use B as the specialised CV correctness baseline and A as a research comparison only. Benchmark the primary four operational arms through [`../baseline/empirical-comparison-plan.md`](../baseline/empirical-comparison-plan.md), with sensor integration evaluated separately when applicable.

## Rejected shortcuts

- “Anomaly = violation”: anomaly scores are candidate signals and may detect permitted unusual behaviour or miss routine policy violations.
- “A track ID = identity”: track IDs are camera-local and can switch under occlusion.
- “A VLM JSON response = rule evaluation”: generated JSON needs schema validation but still does not create deterministic temporal semantics.
- “Every camera needs 30 FPS AI”: camera capture rate and inference rate are separate requirements.
