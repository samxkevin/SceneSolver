# CCTV AI Compliance System — Feasibility Report

**Date:** 2026-10-01 (UTC)
**Status:** architecture study and experiment plan; model/hardware selection remains conditional on measurements
**Primary requirement source:** the mission/context document supplied for this study
**Repository baseline:** SceneSolver at the parent directory

> **Executive answer:** The system is technically feasible for a defined set of owner rules. The defensible core is not a single LLM/VLM. It is local or near-local perception plus tracking/state estimation, a typed temporal event representation, deterministic rule evaluation, bounded evidence and an alert workflow. A VLM can be selectively invoked for open-ended visual review or narrative, but it must not be the final executor of policy. SceneSolver is a valuable research/reference baseline and component library, not evidence that the new compliance system is already solved.

## 1. Executive Summary

See [`architecture/executive-summary.md`](architecture/executive-summary.md). The smallest credible system varies by requirement: sensors or classical CV where possible; a small detector/tracker for people/objects; timers and zones deterministically; a specialised temporal model only for genuinely visual actions; VLM last.

## 2. Problem Definition

Input is one or more CCTV streams, usually continuous. The owner supplies rules involving objects, people, zones, temporal persistence, sequences, exceptions, permissions, thresholds and actions. The output is a versioned decision with a condition trace and bounded evidence, not an unexplained “violation detected.” The universe of rules is open-ended at the policy layer, but the perception ontology is finite and must be extended when a rule requires a visual predicate the models cannot observe.

## 3. Functional Requirements

- ingest files/RTSP and detect camera/data-health failures;
- perceive configured people, objects, regions, text, poses, action cues or sensor events;
- maintain camera-local tracks and quality/uncertainty;
- derive spatial transitions, states, intervals, ordered sequences and absence only when observation health permits;
- evaluate versioned owner rules with AND/OR/NOT, windows, duration, exceptions, permissions, multiple entities/cameras and cooldowns;
- capture structured evidence and route alert/review actions;
- support shadow mode, replay, correction and audit.

## 4. Non-Functional Requirements

Privacy minimisation, edge-first operation, resilience to camera/network/storage failures, deterministic replay, explainable condition traces, target-specific latency/concurrency, resource and thermal limits, secure updates/configuration, retention/deletion, model drift monitoring and human review for ambiguous/high-impact decisions. Exact SLOs are open and must be supplied per rule.

## 5. Proposed System Architecture

```text
CCTV -> decode/health -> sampled lightweight perception
     -> detector -> tracker -> optional pose/OCR/action/sensor join
     -> typed observations -> temporal state/intervals
     -> deterministic rule engine -> evidence manifest -> local alert/review
                                                     \-> policy gateway -> optional cloud/VLM
```

The separation and interfaces are specified in [`architecture/prototype-and-production.md`](architecture/prototype-and-production.md), [`temporal_reasoning/design.md`](temporal_reasoning/design.md) and [`rule_engine/design.md`](rule_engine/design.md).

## 6. Alternative Architectures

A single VLM is broad but hard to calibrate, expensive and weak at exact temporal/policy semantics. A specialised pipeline is efficient and auditable for known predicates but cannot solve open-world semantics. A hierarchical pipeline combines the two under a compute/privacy budget. A sensor-assisted architecture is superior wherever a gate contact, access-control, POS, PLC or schedule event can provide the state more reliably than vision. The comparative decision is in [`architecture/candidate-architectures.md`](architecture/candidate-architectures.md).

## 7. AI/CV Pipeline

1. **Ingest:** decode once, source/monotonic timestamps, bounded ring buffer, health.
2. **Sampling:** fixed/adaptive rate, motion/ROI/event-triggered escalation; 30 FPS capture is not 30 FPS AI.
3. **Perception:** smallest detector/pose/OCR/segmentation/action model required by the active rules.
4. **Detection/tracking:** localise and associate; detector intervals and track quality are explicit.
5. **Temporal state:** intervals and transitions, not frame labels alone.
6. **Rules:** deterministic allow-listed DSL and three-valued logic.
7. **Evidence/alert:** condition trace and bounded frames/clip, then workflow.
8. **Optional review:** VLM/LLM sees selected evidence only and produces grounded advisory output.

## 8. Model Families Considered

Object detectors, trackers, pose, action/temporal models, video transformers, CLIP retrieval, segmentation, OCR, audio, classical CV, anomaly models and VLM/LLM assistants are compared in [`models/model-matrix.md`](models/model-matrix.md). The task formulation matters: detection, tracking, sequence classification, temporal action localization, sequence labelling, state estimation and regression are different problems.

## 9. Detailed Model Comparison

No family is ranked globally. Small CNN detector + simple tracker is the default baseline; RT-DETR is a measured detector challenger; ByteTrack/SORT and BoT-SORT/DeepSORT are tracking arms; pose/OCR/segmentation are incremental options; TimeSformer/VideoMAE are temporal research arms; CLIP/anomaly/VLM are candidate/review arms. Published results retain their conditions in [`research/published-benchmarks.md`](research/published-benchmarks.md).

## 10. CPU-Only Feasibility

A CPU-only laptop can plausibly host a sampled detector, tracking, camera geometry, timers, rules, local evidence and health logic after measurement. It should not be assumed to run the complete SceneSolver stack continuously. Heavy video transformers, large VLMs, dense segmentation and training are selective/offline candidates. The experiment must report p95 latency, dropped frames, memory, thermals and rule-level quality, not just model FPS.

## 11. GPU/Edge Device Feasibility

An integrated GPU/NPU may accelerate small exported models, but exact operator support, driver and shared-memory contention must be tested. A consumer GPU workstation is the practical development/benchmark tier. A dedicated edge GPU is the likely on-prem path for multiple streams when CPU capacity fails. The hardware matrix is [`hardware/feasibility-matrix.md`](hardware/feasibility-matrix.md). NVIDIA/Intel TOPS values in the sources are hardware context, not camera capacity.

## 12. Cloud Feasibility

Cloud GPUs make large temporal models, VLM review, training, fleet analytics and cross-camera searches possible, subject to consent/policy, data residency, cost, egress, WAN reliability and provider terms. Cloud resources should not force raw continuous video off-site.

## 13. Edge vs Cloud vs Hybrid Comparison

| Mode | Strength | Main risk | Recommended role |
|---|---|---|---|
| Edge-only | minimum egress and local continuity | hardware/updates/capacity | default for privacy-constrained routine rules |
| Cloud-only | central scale and powerful models | continuous sensitive data movement and WAN dependency | only where explicitly approved |
| Hybrid | local routine decisions, selective cloud value | boundary/configuration complexity | leading deployment for optional heavy review |

Details and data classes are in [`privacy/deployment-and-boundary.md`](privacy/deployment-and-boundary.md).

## 14. Quantization and Optimisation Strategy

Use FP32 as a correctness reference, then FP16/INT8 and only justified INT4/QAT/pruning/distillation. Quantisation may reduce memory/bandwidth but does not guarantee CPU friendliness or speed; unsupported operators can fall back. System optimisations—sampling, ROI, asynchronous stages, hardware decode, tracker updates and selective escalation—often matter more. See [`hardware/optimisation.md`](hardware/optimisation.md).

## 15. Rule Engine Architecture

Rules are versioned data. The schema supports typed events, predicates, boolean composition, temporal operators, sequence, absence, scopes, exceptions, thresholds, authorization and actions. Natural language may draft a rule, but controlled ontology resolution, static validation, synthetic tests and owner approval are mandatory. Free-text LLM output never executes directly.

## 16. Owner-Configurable Rule Examples

The design includes restricted-zone dwell, gate-open duration, required-action absence, schedules, multiple entities and cross-camera joins. A rule is only as general as the observation vocabulary. For example, “smoking” requires a validated action/object/pose observation; “for 30 seconds” is deterministic once `inside_zone` is reliable.

## 17. Temporal Reasoning Architecture

The event seam has raw observations, derived state, transitions, intervals and rule decisions. It tracks source/monotonic time, gaps, open/complete intervals, unknown state, entity binding, provenance and calibration. A 30-second duration is elapsed time under an allowed-gap policy—not 30 frames. A missing camera interval cannot satisfy an absence rule.

## 18. Evidence Generation Architecture

At trigger time, a local encrypted ring buffer supplies bounded pre/trigger/post evidence. The manifest contains camera/rule/version/time, conditions satisfied, entity/zone refs, event lineage, model/calibration versions, hashes, redaction/export status and reviewer actions. Evidence quality is measured by reviewer sufficiency, citation coverage, timestamp error, redaction error, storage and capture latency. See [`evidence/design.md`](evidence/design.md).

## 19. Privacy Architecture

Raw video, frames, clips, metadata, track IDs, embeddings, reports and audio have different risks. Embeddings are not automatically anonymous. Default boundary: raw streams and keys stay local; only policy-approved metadata/redacted evidence crosses a gateway. Minimise retention, encrypt, restrict access, audit egress, protect models/configs and test deletion.

## 20. Security Considerations

Threat model camera credentials, edge devices, model supply chain, rule tampering, VLM prompt injection, evidence replacement, cloud processor access, insider access and denial-of-service. Use signed artifacts/configuration, least privilege, TLS/mTLS, encrypted storage, key rotation, append-only audit, secure update/rollback, queue limits and incident response.

## 21. Compliance Considerations

This report is not legal advice. Legal/privacy/security/compliance/HR teams must review notice/consent or lawful basis, employee monitoring, biometric/facial recognition, audio, retention, residency/cross-border transfer, automated decisions, human review, accuracy/discrimination risk, auditability and evidence policy. Use technical privacy frameworks as risk-management references, not legal substitutes.

## 22. Failure Modes and Mitigations

The major classes are occlusion/ID switch, lighting/night/weather, camera movement, data gaps, compression, crowding, domain shift, action ambiguity, stale authorization, storage/network failures, VLM hallucination, score miscalibration and adversarial obstruction. The system must expose unknown/degraded state, use temporal confirmation and multiple signals, monitor drift, preserve evidence and avoid converting silence to compliance. See [`architecture/failure-modes.md`](architecture/failure-modes.md).

## 23. Dataset and Training Requirements

Start with an event ontology and annotation guide. Collect target-camera normal footage, positives, hard negatives, ambiguity, night/occlusion/crowd/weather/compression and system-failure intervals. Label boxes/tracks/zones and event boundaries where needed. Split by camera/site/time/person/session to avoid leakage. UCF-Crime is a useful research reference but not an owner-rule acceptance set.

## 24. Evaluation Methodology

Use synthetic event traces for rule semantics, controlled staged scenes for repeatability and naturalistic time-separated/site-separated holdout for deployment validity. Tune thresholds on calibration data, lock test data, stratify by condition, inspect worst cases and retain raw predictions/config hashes. Detailed protocol: [`experiments/experiment-matrix.md`](experiments/experiment-matrix.md).

## 25. Metrics

Detection: precision/recall/mAP/small-object recall/calibration. Tracking: HOTA, IDF1, MOTA, ID switches and rule-specific zone/dwell error. Temporal: segment/event F1, boundary error, time-to-detect. Rules: precision/recall/F1, false alerts and misses per camera-hour, unknown/duplicate rate. System: p50/p95/p99 alert latency, drops, queue age, memory, VRAM, power, thermal, startup/recovery. Evidence: citation coverage, reviewer agreement, correction rate, bytes/event.

## 26. Prototype Architecture

P0 is offline local replay with fake adapters and deterministic rules. P1 is one live edge camera with a small detector/tracker, zones, timers, local evidence and health. P2 adds multi-camera event bus, durable ledger, sensor joins and policy-controlled export. Do not add a VLM to the critical path before the core is measurable.

## 27. Minimum Viable Prototype

Select 2–3 rules spanning one spatial/duration rule, one sensor/vision state rule and one difficult temporal action. Implement one camera, two detector variants, one tracker baseline, typed events, rule schema/validator, replay tests, local ring buffer, evidence manifest, local alert and benchmark logging. Include negative/unknown/failure scenarios. Success is a measurement package, not a demo video.

## 28. Production Architecture

Camera adapters and health -> edge inference workers -> typed observation stream -> tracker/state store -> rule service -> immutable event ledger -> evidence/alert workflow -> policy gateway -> optional cloud analytics/review. Include idempotence, backpressure, configuration/model versions, rollback, multi-tenant isolation, monitoring, retention and operator review.

## 29. Recommended Experiment Matrix

E-01–E-16 cover detector/tracker/action/temporal/rule quality, CPU/iGPU/edge/cloud latency, quantisation, power/memory, end-to-end alert latency, evidence, robustness and drift. No acceptance number is fabricated; owners fill the blank gates in [`experiments/benchmark-config.example.yaml`](experiments/benchmark-config.example.yaml).

## 30. Open Technical Questions

The largest blockers are the first rule ontology, trusted sensor/access-control availability, camera conditions, per-rule false-alert budget, identity requirement, audio necessity, target hardware, precision/SLO and cloud/export policy. See [`decisions/open-questions.md`](decisions/open-questions.md).

## 31. Final Engineering Conclusions

1. Build the core as **AI perception + structured events + deterministic temporal/rule engine + evidence**, not an LLM/VLM.
2. Use the smallest detector/tracker and classical geometry that meet observation and rule-event gates.
3. Treat anomaly detection, CLIP, TimeSformer/VideoMAE, RL and VLM as candidate selective stages; prove incremental value.
4. Keep continuous raw CCTV and routine policy evaluation at the edge where privacy requires; export only controlled, minimised data.
5. Use sensors for authoritative state/authorization whenever available.
6. Do not claim CPU, NPU, GPU or cloud capacity until it is measured with the complete pipeline and target conditions.
7. Do not treat SceneSolver's small recorded test metrics as production compliance evidence; use it as a research/reference baseline and comparison arm.
8. The next engineering action is P0: implement model-neutral event/rule/evidence contracts and run the controlled experiment matrix before choosing a final model.
