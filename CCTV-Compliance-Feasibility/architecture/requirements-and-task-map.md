# Requirements and Task Map

## Functional layers

| Layer | Responsibility | Learned AI required? | Contract |
|---|---|---|---|
| Ingest/health | receive RTSP/files, decode, timestamps, detect gaps/freeze | no, except optional quality model | frames + health intervals |
| Perception | infer visible classes, keypoints, text, state/action cues | often | typed observations with score/quality |
| Detection | localize instances/regions | usually | boxes/masks/classes |
| Tracking | associate observations over time | base algorithm deterministic; optional appearance model | camera-local track state |
| Temporal reasoning | intervals, transitions, sequence, absence, deadlines | no for explicit policy; optional learned action model for hard cues | events/state with bounds/gaps |
| Rule evaluation | owner policy and exceptions | no | deterministic decision + condition trace |
| Evidence | select bounded frames/clips, hashes, manifest | no | evidence package |
| Alerting | route/queue/acknowledge/escalate | no | alert lifecycle + audit |
| Review/explanation | summarize evidence or find ambiguous content | optional VLM/LLM | constrained narrative, never silently edits decision |

## Event classes

- **Object/state:** `person.detected`, `gate.open`, `object.present`.
- **Spatial:** `person.entered_zone`, `person.exited_zone`, `object.overlaps_zone`.
- **Action candidate:** `person.smoking_candidate`, `person.lifting_candidate`, `task.completed_candidate`.
- **Identity/permission:** `badge.present`, `authorization.joined`, `authorization.unknown`.
- **System:** `camera.unhealthy`, `observation_gap`, `model.loaded`, `evidence.stored`.
- **Rule:** `rule.candidate`, `compliance.violation`, `review.completed`, `decision.corrected`.

## Requirements by capability

| Owner requirement shape | Minimum inputs | Expected difficulty |
|---|---|---|
| presence in zone | person detection, tracker, polygon | low/medium; depends on view/occlusion |
| dwell > X | same + stable time/track + camera health | medium; gaps/ID switches matter |
| gate open too long | sensor preferred; otherwise state detector/segmentation | low with sensor, medium/high with vision |
| unauthorized access | event identity/permission join + zone/track | policy/integration high; appearance identity risky |
| smoking | person/object/pose/action over time | high/ambiguous; requires site labels and hard negatives |
| object left | object detector + owner zone + dwell/motion state | medium/high for object class and occlusion |
| required action absent | expected task event + healthy observation window + sequence | medium for event source, deterministic after |
| cross-camera journey | reliable join key + synchronized clocks + route graph | high; avoid by default |
| open-ended unusual behavior | anomaly/retrieval/VLM candidate | high; cannot be turned into a precise compliance promise without ontology |
