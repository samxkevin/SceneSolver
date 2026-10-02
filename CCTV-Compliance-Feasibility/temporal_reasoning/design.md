# Temporal Event Representation and Reasoning

## Why event representation is the seam

Models operate on frames or clips; owners reason about entities and intervals. A typed, append-only observation/event layer makes the system model-neutral and allows deterministic replay, synthetic tests, evidence linking and rule changes without retraining.

## Layers

1. **Raw observation:** detector/tracker/pose/OCR/sensor output at a source timestamp.
2. **Derived state:** entity inside zone, gate open, action candidate, authorization join, camera health.
3. **Transition event:** entered/exited, opened/closed, task started/completed, track lost.
4. **Interval event:** presence/action/state persisted over `[start, end]` with gaps and quality.
5. **Rule decision:** conditions and exceptions evaluated under a policy version.

## Required semantics

- Use source timestamp and monotonic receive/processing timestamp; never infer elapsed time from frame index alone when frames can drop.
- Store `start_time`, `end_time`, `first_seen`, `last_seen`, `max_gap`, and an explicit `complete`/`open` state.
- Model `unknown` and `data_gap` separately from a negative observation.
- Bind entity references and state whether the binding is camera-local or cross-camera.
- Preserve all contributing observation IDs and evidence frame IDs.
- Store calibration/zone and model versions.
- Allow overlapping events; do not force unrelated tracks into one global sequence.

## State machine example: zone dwell

```text
ABSENT --confirmed entry--> PRESENT
PRESENT --continuous/allowed gaps--> DWELLING
DWELLING --duration >= threshold--> VIOLATION_CANDIDATE
PRESENT/DWELLING --confirmed exit--> EXITED
any --track lost--> UNKNOWN (until timeout policy resolves)
```

A “30 seconds” rule is not “30 frames.” It is elapsed time while the camera and track evidence satisfy the rule's gap/quality conditions.

## Sequence and absence

An absence rule is only evaluable if the observation window is healthy. If the camera was offline, the task was not visible, or the tracker was lost, emit `unknown`/`not_observed` rather than “not completed.” Sequence matching must specify whether events from different entities may satisfy the sequence; default is same-bound binding.

## Temporal recognition model choices

| Choice | Use when | Output | Risk |
|---|---|---|---|
| State machine + timers | zone, gate, dwell, deadlines | interval/transition | depends on reliable observations |
| Feature TCN/GRU | short, repeated action patterns | window/sequence score | labels and boundaries required |
| Video transformer | complex spatial-temporal interaction | clip/segment class | cost, domain shift and boundary resolution |
| Anomaly model | unknown/novel candidate generation | deviation score | novelty is not violation |
| VLM | semantic review of bounded evidence | explanation/candidate | hallucination and cost; not deterministic |

## Late and out-of-order data

Events carry a source time and ingest sequence. The evaluator uses a bounded watermark/allowed lateness policy. A late observation may produce an amended decision, never silently mutate history. Evidence and rule outputs need immutable versions for audit.

## Cross-camera reasoning

Cross-camera logic requires an explicit join key and policy:

- trusted badge/access event (preferred);
- scheduled route/time window;
- approved appearance matching, with privacy review;
- manual operator link.

A camera-local track ID cannot be reused as a person identifier. If no join is reliable, report camera-local facts separately.
