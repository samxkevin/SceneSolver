# Prototype Architecture and Production Evolution

## Prototype P0: offline, privacy-preserving replay

**Goal:** prove contracts and rule semantics before model selection.

```text
video file -> deterministic sampler -> detector adapter (recorded or live)
          -> tracker -> zone mapper -> event normalizer
          -> rule evaluator -> evidence manifest -> HTML/JSON report
```

Properties:

- One camera; local files only; no cloud dependency.
- A small detector and ByteTrack/SORT-compatible adapter are interchangeable.
- Polygon zones and object classes are configuration.
- A ring-buffer-like pre/post evidence extractor operates on a local file.
- Rule engine has a replay mode: same event log + same rule version = same verdict.
- Synthetic event streams test temporal rules without any model.
- Every observation includes quality, source, model version, frame/time bounds and provenance.

**P0 success:** rules for zone entry + authorization, duration, gate state duration, object placement, ordered sequence, absence and cooldown pass unit/replay tests; model-independent rule tests exist.

## Prototype P1: live single-camera edge

Components:

1. RTSP/file input and bounded frame buffer.
2. Decode/health monitor with timestamps from source and monotonic processing clock.
3. Sampled small person/object detector; detector interval and ROI are configurable.
4. Camera-local tracker; confidence and track age are exposed.
5. Geometry service for zones/lines and calibration version.
6. Optional tiny state/action model only when a rule requires it.
7. Rule engine, evidence writer and local alert sink.
8. Prometheus/OpenTelemetry-like metrics or equivalent local counters.

No VLM in the critical path. VLM adapter may consume a manually selected local evidence package.

## Prototype P2: multi-camera edge/hybrid

Add:

- Camera registry and per-camera configuration versions.
- Local event bus and durable event ledger.
- Cross-camera correlation by explicit encounter windows and non-biometric identifiers where possible.
- Policy-controlled cloud export of event metadata and redacted evidence.
- Queue budgets and backpressure: dropping optional VLM work must not stop deterministic rule evaluation.

## Production target

```text
Camera adapters -> edge ingest/health -> inference workers
       -> typed observations -> tracker/state store -> rule service
       -> immutable event ledger -> evidence service -> alert/workflow
       -> policy gateway -> optional cloud analytics/review
```

### Reliability requirements

- At-least-once observation delivery with idempotent event IDs.
- Monotonic timestamps and source-clock diagnostics.
- Explicit `unknown` state; missing data must not silently become `false`.
- Model/config/calibration version attached to every derived observation.
- Graceful degradation: camera down, detector unavailable, tracker lost, storage full, network unavailable, VLM timeout.
- Backfill/replay from retained local evidence where policy permits.
- Signed or hashed evidence manifest and append-only audit record.
- Tenant/camera isolation; least-privilege service identities.

### Scaling rule

Scale by measuring `camera × sampled FPS × detector cost`, not by the camera's encoded FPS alone. A tracker can update between detector calls, but its drift and re-identification failure rates must be measured. Heavy models should run from bounded queues with a per-camera and global budget.

## Model-neutral interfaces

```text
Detector.detect(frame, roi, deadline) -> Detection[]
Tracker.update(detections, timestamp) -> Track[]
StateEstimator.update(tracks, auxiliary_events) -> Observation[]
RuleEngine.evaluate(observation_batch, policy_version) -> RuleDecision[]
EvidenceStore.capture(trigger, source_buffer) -> EvidenceManifest
```

The first prototype should implement fake adapters for all interfaces. This prevents an early detector choice from becoming the architecture.

## Promotion path

| Stage | Must be true before promotion |
|---|---|
| P0 -> P1 | deterministic rule tests, timestamps, evidence references, basic detector/tracker replay |
| P1 -> P2 | live latency and camera-health SLOs, per-rule precision/recall, stress tests, local retention controls |
| P2 -> production | site acceptance dataset, security/privacy review, fail-safe behavior, incident response, model/config rollback, operator workflow, measured capacity |
