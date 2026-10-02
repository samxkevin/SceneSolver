# Empirical SceneSolver Baseline Comparison Plan

## Purpose

This plan turns SceneSolver from a repository inventory into a reproducible comparison arm. It does not modify the existing SceneSolver pipeline. The comparison uses one common replay harness, one locked input manifest, one normalized output contract, and one evaluation protocol for four primary systems plus an optional parallel sensor arm:

1. **S0: SceneSolver reference pipeline**
2. **S1: Specialised CV baseline**
3. **S2: Hierarchical Event Driven Architecture core path**
4. **S3: S2 plus optional VLM escalation**
5. **S4: S2 plus sensor integration, evaluated as a parallel arm where a trusted sensor exists**

The point is not to make every system identical. The point is to measure the cost and incremental value of the architecture choices under the same input clips, event labels, rule definitions and reporting requirements. S4 is a parallel comparison arm, not an instruction to add sensors to every deployment or to place it after the VLM arm.

## Common replay corpus

Create and freeze a manifest containing:

- source clip hash, camera/site/session ID, capture time bucket and privacy classification;
- encoded resolution, FPS, codec, duration, audio presence and known camera failures;
- event annotations with start/end uncertainty, object boxes/classes, track IDs where available, zones, action labels, permission/sensor records and ambiguity labels;
- normal negative intervals, permitted unusual intervals and hard negatives;
- camera condition tags: day/night, lighting, blur, compression, crowd, occlusion, camera movement and weather;
- rule version and expected decision trace;
- train/calibration/validation/test partition determined by camera/session/time, not random frames.

The locked test manifest must not be used for prompt selection, threshold tuning, quantisation calibration or VLM few-shot examples.

## Systems under test

### S0: SceneSolver reference pipeline

Use the closest reproducible version of the existing staged pipeline available in the repository, with external checkpoints and paths pinned in a run manifest:

```text
AE anomaly signal
-> TimeSformer binary
-> TimeSformer multiclass
-> conditional YOLO/object stage
-> audio features where present
-> existing tracking/behaviour stage
-> fusion/reasoning
-> optional RL3033
-> optional LLaVA narrative
-> existing report generation
```

Run two declared variants if resources allow:

- `S0-core`: AE, TimeSformer, conditional object/audio/fusion/report stages, experimental stages disabled.
- `S0-full`: the same with RL3033 and LLaVA enabled, each marked experimental.

This avoids hiding the cost of optional stages behind one number.

### S1: Specialised CV baseline

```text
sampled frames
-> small closed-set detector
-> ByteTrack or equivalent simple tracker
-> camera zones/lines
-> deterministic state and rule engine
-> bounded evidence manifest
```

Use no anomaly model, video transformer or VLM. This is the smallest correctness and CPU reference.

### S2: Hierarchical core

```text
S1
+ adaptive sampling and ROI scheduling
+ optional pose/OCR/segmentation/action adapter only for rules that require it
+ typed observation/event stream
+ health-aware temporal state
+ deterministic rule engine
+ evidence and alert lifecycle
```

The detector/tracker weights may be identical to S1 for the first run. This isolates the value of the event and rule architecture from the value of a newer model.

### S3: Hierarchical plus optional VLM

```text
S2
+ bounded, policy-approved evidence package
+ selected VLM review/narrative
+ schema/citation validation
```

VLM invocation is triggered by candidate uncertainty or a review policy. The VLM cannot create an authoritative violation or override a deterministic rule result. Measure both `S3-triggered` and `S3-always-on` only as an explicit cost control, not as a recommended deployment.

### S4: Hierarchical core plus sensor integration

```text
S2
+ one approved sensor or authorization signal
+ explicit freshness, join quality and failure state
+ deterministic comparison against the equivalent visual predicate
```

Run S4 only when a trusted sensor is available. It may replace a visual predicate, corroborate it, or expose a different failure mode. Do not interpret S4 as a mandatory additive stage.

## Fairness and reproducibility controls

- Same decoded frames and audio samples where the systems support them.
- Same wall-clock replay speed and a separate offline maximum-throughput run.
- Same camera ROI and zone geometry, versioned and hashed.
- Same rule definitions, schedules, permissions and cooldowns.
- Same test partition and annotation adjudication.
- Warm and cold startup runs separated.
- Hardware pinned per comparison batch; no cross-hardware ranking without a re-run.
- Model, code, runtime, driver, precision, batch size, thread count and quantisation calibration manifest recorded.
- Optional stages are reported separately, not averaged away.
- Every failure, timeout, dropped frame and unknown interval is retained in the output ledger.

## Normalized output contract

Each system emits:

```text
run_id
system_id and variant
camera_id and source_clip_hash
decoded_frames, processed_frames, skipped_frames, dropped_frames
observations and tracks
rule candidates, confirmed alerts, suppressed alerts, unknown decisions
false-positive/false-negative adjudication references
evidence manifest IDs and report paths
stage timing and resource samples
failure events and recovery state
```

If S0 cannot produce a typed field, record it as `not_available`, not as zero.

## Runtime and resource measurements

| Category | Required measurements |
|---|---|
| Runtime | total wall time, startup/model-load time, steady-state throughput, replay speed |
| Stage latency | decode, sampling, AE, TimeSformer binary, multiclass, YOLO/object, audio, tracker, rule engine, VLM, evidence, report generation; p50/p95/p99 where sample size permits |
| Memory | peak and steady RSS, RAM, VRAM/shared memory, model artifact size, temporary evidence storage |
| Stream work | source FPS, processed FPS, frames skipped by design, frames dropped by overload, queue age, decoded duration covered |
| Outputs | normal/anomaly/incident labels, detections, tracks, events, rule decisions, evidence artifacts, report files and narrative outputs |
| Quality | rule precision/recall/F1, false alerts per camera-hour, misses per camera-hour, unknown rate, duplicate alerts, boundary error, evidence usability |
| Failure | model load errors, decoder failures, missing audio, OOM, timeout, queue overflow, camera/data gaps, report failure and graceful degradation |

Resource numbers must include the full process and report generation, not only the neural network call. Power and thermal measurements are required when the hardware makes them measurable.

## Comparison report template

| System | Variant | Hardware | Clips/camera-hours | Frames decoded/processed/skipped/dropped | p95 alert latency | Peak RAM/VRAM | Report time | FP/camera-hour | FN/camera-hour | Unknown rate | Failure cases | Evidence usable rate |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|---|---:|
| S0 | core/full | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| S1 | CV | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| S2 | hierarchical core | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| S3 | hierarchical + VLM | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |

## Interpretation rules

- Do not compare S0's anomaly accuracy directly to S1/S2 rule-event recall. They solve different tasks. Report task-specific metrics and then compare the end-to-end owner-rule outcome.
- A lower false-alert rate with many unknown intervals is not automatically better.
- A VLM improvement is only useful if it survives grounded-review accuracy, latency, resource, privacy and cost gates.
- Report generation time is part of operational cost if a report is required for every alert. It is asynchronous only if alert delivery does not wait for it.
- If S0 cannot be reproduced because external checkpoints or data are unavailable, record the reason and run a trace-compatible dry comparison. Do not silently substitute a different pipeline.

## Minimum execution order

1. Build the normalized manifest and synthetic rule traces.
2. Run S1 first to validate the harness and labels.
3. Run S2 with the same detector/tracker to isolate architecture value.
4. Run S0 with declared optional stages and capture missing-field limitations.
5. Run S3 only on the bounded review subset and then on the locked test set.
6. Publish raw traces, aggregate results, failure inventory and a decision record.
