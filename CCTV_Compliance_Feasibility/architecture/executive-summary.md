# Executive Architecture Summary

## Decision under study

The leading architecture is a **hierarchical, event-driven hybrid**:

```text
CCTV / RTSP
  -> decode, health and bounded ring buffer
  -> sampled lightweight perception
  -> detector + tracker + optional pose/OCR/state classifiers
  -> camera-local observations and quality signals
  -> temporal state estimator
  -> deterministic rule engine
  -> structured evidence package
  -> local alert / optional controlled synchronisation
                         \
                          -> selective VLM or cloud review
```

The VLM branch consumes a selected evidence package and returns an explicitly non-authoritative narrative or a typed review suggestion. It does not mutate the event ledger or execute policy. A human may review high-impact cases before action.

## Why not one large model?

A single VLM can be useful for open-world description, but it does not remove the need for stable identity across frames, camera geometry, timers, permissions, absence conditions, audit logs, deterministic replay and evidence integrity. It also adds cost, latency, privacy exposure and hard-to-calibrate failure modes. It is therefore a poor default for routine “inside zone for more than 30 seconds” or “gate open for more than 20 seconds” decisions.

## What the smallest system looks like

| Requirement shape | Smallest credible mechanism | Learned component? |
|---|---|---|
| Person/object present | Small detector, possibly class-specific | Yes, unless sensor/PLC provides it |
| Enter/leave a polygon | Detector + camera calibration/geometry + tracker | Detector/tracker only |
| Presence duration | Track state + monotonic timer | No additional model |
| Gate open/closed | Fixed camera geometry/classifier or contact sensor | Maybe; deterministic if a trusted sensor exists |
| Access permission | Badge/access-control event or roster lookup | No; identity perception may be separate |
| “Smoking” | Action/object/pose cue over a window | Usually yes; needs site data |
| Required sequence completed | Typed events + finite-state/temporal rule | No, once events exist |
| “Something unusual” | Anomaly model or open-vocabulary/VLM review | Yes; policy must not equate unusual with violation |
| Explain a completed decision | VLM/LLM constrained to evidence | Optional; not a source of truth |

## Feasibility by hardware tier

- **CPU-only laptop:** feasible for one/few streams at reduced sampling only after measurement; target detector, decode, tracking, geometry, timers and rules first. Heavy video transformers, generative VLMs and dense segmentation are offline/selective candidates.
- **Integrated GPU/NPU laptop:** same architecture with accelerated small detector/pose/OCR where the runtime supports the exact operators. NPU support and throughput must be measured on the actual device; TOPS is not FPS.
- **Consumer GPU workstation:** practical development and multi-camera evaluation platform; can host temporal models and a selective VLM, subject to VRAM and concurrency.
- **Dedicated edge GPU:** preferred for on-prem multi-camera service when CPU-only capacity is insufficient; local video remains local.
- **Cloud GPU:** useful for fleet analytics, training, difficult review and cross-camera searches where policy permits. It is not a reason to transmit continuous raw video by default.

## SceneSolver disposition

`SceneSolver = established research/reference baseline + reusable components`, not a ready-made compliance engine. Keep its deterministic DatasetTools, staged orchestration ideas, evidence/reporting concepts and candidate temporal models as comparison points. Do not extend the production/research pipeline until the isolated prototype proves a contract and measurements.

The repository evidence is meaningful but narrow: a binary TimeSformer test report on 30 samples, a seven-class report on 140 samples, anomaly/keyframe artifacts, audio autoencoder history, and a sample report. Missing are target-site labelled streams, leakage-controlled splits, calibration, MOT/tracking metrics, end-to-end latency, concurrency, power, and rule evaluation.

## Acceptance gates before a production choice

1. A labelled site-specific test set exists with camera/time split and a written event ontology.
2. Detector/tracker outputs meet per-rule observation recall under occlusion and night conditions.
3. Rule replay is deterministic and unit-tested, including negative/absence cases and exceptions.
4. Alert quality is measured per camera-hour, not only aggregate accuracy.
5. The edge service survives camera/network/model failures and records health state.
6. Quantised exports are compared to a floating baseline on the same clips and target hardware.
7. Evidence is sufficient for a reviewer while retention and cloud transfer remain policy-approved.
8. A human-review path exists for ambiguous or high-impact cases.

## Claims not yet established

- Exact cameras-per-device capacity.
- CPU/NPU/edge-GPU FPS or power.
- Generalisation of any UCF-Crime result to owner-defined compliance.
- Accuracy of smoking, authorization, “required action not completed,” or cross-camera identity.
- Whether audio is necessary, permitted, or useful for a particular deployment.

These are tracked in [`../decisions/open-questions.md`](../decisions/open-questions.md) and must not be replaced with assumptions.
