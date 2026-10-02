# Failure Mode Analysis

| Failure | Layer | Impact | Detection/monitoring | Mitigation / policy |
|---|---|---|---|---|
| Camera offline or frozen | ingest | missed events | heartbeat, frame hash, source timestamps | health alert; never report compliant from silence; retain outage interval |
| Clock drift / bad timestamps | ingest | wrong duration/order | compare source, host and monotonic clocks | use monotonic durations; record uncertainty; synchronize clocks |
| Decode drop/backpressure | ingest | invisible interval | decode/drop counters, queue depth | bounded queues, adaptive sampling, alert on data loss |
| Lighting/night/weather | perception | FN/FP | quality score, illumination/weather tags | low-light training/evaluation, alternate sensor, human review |
| Occlusion/crowding | detection/tracking | ID switches, duration errors | track age, confidence, occlusion flags, HOTA/IDF1 | temporal confirmation, camera placement, multi-camera/sensor fusion |
| Camera moved/zoomed | geometry | wrong zone decisions | calibration hash and scene-change check | disable affected zone rules until recalibrated |
| Detector domain shift | perception | broad recall loss | drift dashboards and sampled review | retrain/calibrate; shadow candidate model; rollback |
| Action ambiguity | action | harmful false alert | action confidence and disagreement | require persistence/multi-signal; VLM/human review; no automatic sanction |
| Track ID switch | tracking | wrong attribution | association diagnostics, short track continuity | do not carry authorization across uncertain identity; use badge/sensor |
| Badge absent or delayed | identity integration | unknown authorization | event freshness and join status | `unknown` is not unauthorized; policy-specific escalation |
| Object left vs parked temporarily | temporal rules | false positive | dwell timer and movement history | grace period, exit/re-entry semantics, exception rules |
| VLM hallucination | optional review | false explanation | citation validator, schema validation, reviewer comparison | VLM cannot create authoritative predicate; show uncertainty |
| Model score miscalibration | perception | threshold instability | reliability diagram, calibration drift | calibrate per camera/rule; threshold by cost, not default 0.5 |
| Adversarial/obscuring behavior | all | missed or misleading evidence | anomaly/quality signals | layered signals, operator workflow, secure evidence, do not overclaim |
| Storage full / tampered evidence | evidence | no proof / integrity risk | capacity, hashes, append-only audit | retention quotas, secure storage, fail alert, time-limited local buffer |
| Network/cloud unavailable | hybrid | delayed sync | queue age, delivery status | local alert/rule continuity; retry; never block edge |
| Privacy boundary misconfiguration | security | unauthorized disclosure | policy tests, egress audit, DLP | deny-by-default gateway; redaction; key rotation; access review |
| Class imbalance / leakage | evaluation | inflated metrics | split lineage and duplicate checks | group by source/camera/time; holdout sites; audit manifests |

## Reliability principles

1. A missing observation is an `unknown`, not a negative observation.
2. A single frame is rarely enough for a temporal compliance decision.
3. A model confidence is not a calibrated violation probability.
4. Rule-level false-positive rate should be expressed per camera-hour/day as well as per event.
5. High-impact outcomes require human review and organisational policy; technical confidence alone is insufficient.
