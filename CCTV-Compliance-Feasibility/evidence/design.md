# Evidence Architecture

## Evidence is a bounded, structured product

A violation result should be reviewable without retaining all continuous CCTV forever. The evidence service consumes a rule trigger and a local ring buffer, then creates a versioned package with exact provenance.

```text
local ring buffer (short, encrypted)
   + event lineage + rule conditions + selected frames
   -> evidence manifest
   -> local encrypted store
   -> optional redacted/approved export
```

## Evidence manifest fields

```json
{
  "evidence_id": "ev-20261001-camera01-000123",
  "camera_id": "camera-01",
  "rule_id": "restricted_counter_access",
  "rule_version": 1,
  "decision": "confirmed",
  "severity": "high",
  "event_interval": {"start": "...", "end": "..."},
  "source_clock": {"clock_domain": "source", "sync_status": "known"},
  "subjects": [{"ref": "camera-01/track-17", "identity_status": "not_identified"}],
  "zone_id": "counter_zone",
  "conditions": [
    {"id": "c1", "predicate": "person.entered_zone", "status": "satisfied", "event_ids": ["..."]},
    {"id": "c2", "predicate": "authorization.status != authorized", "status": "unknown", "event_ids": ["..."]},
    {"id": "c3", "predicate": "dwell >= 10s", "status": "satisfied", "event_ids": ["..."]}
  ],
  "frames": [
    {"role": "before", "timestamp": "...", "sha256": "...", "path": "local://..."},
    {"role": "trigger", "timestamp": "...", "sha256": "...", "path": "local://..."},
    {"role": "after", "timestamp": "...", "sha256": "...", "path": "local://..."}
  ],
  "clip": {"present": true, "start": "...", "end": "...", "sha256": "..."},
  "provenance": {"model_versions": [], "calibration_version": "...", "event_ids": []},
  "privacy": {"classification": "restricted-image", "egress_allowed": false},
  "integrity": {"manifest_sha256": "...", "created_at": "..."}
}
```

The example deliberately preserves `unknown` authorization rather than manufacturing “unauthorized.” Whether a rule can alert with unknown is an owner/policy decision.

## Capture strategy

- Maintain a short, encrypted, access-controlled per-camera ring buffer.
- At candidate trigger, copy a configurable pre-roll and post-roll only if policy allows.
- Prefer event-specific keyframes plus bounding boxes/zone geometry when a clip is unnecessary.
- Redact unrelated faces, plates, screens or other sensitive regions only after testing that redaction does not remove the fact needed for review.
- Do not put raw images or embeddings in routine logs.
- Generate a hash at capture, store timestamps and chain manifest references; use authenticated encryption at rest and TLS/mTLS for transfer.
- Apply per-class retention and deletion workflows; evidence retention must be policy-approved.

## Reviewer view

The UI should show:

1. event interval and camera;
2. rule version and plain-language conditions;
3. a timeline of source events and data gaps;
4. before/trigger/after frames or clip;
5. detector/tracker overlays and confidence/quality, clearly labelled;
6. identity/authorization source and freshness, if any;
7. model/config/calibration versions;
8. reviewer actions, corrections and comments;
9. an explicit disclaimer that a generated narrative is not independent evidence.

## Integrity and chain of custody

This is an engineering design, not a forensic/legal certification. Preserve original hashes, signed manifests, access logs, time source, export history and immutable correction records. The organisation's security/legal/forensics teams must define the required standard.

## Evidence quality metrics

- reviewer can locate the relevant interval;
- condition-to-frame citation coverage;
- timestamp error and pre/post-roll completeness;
- percentage of alerts with usable evidence;
- redaction error rate;
- evidence generation latency and storage per event;
- reviewer agreement and correction rate;
- retrieval/access audit completeness.
