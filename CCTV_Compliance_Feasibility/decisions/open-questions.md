# Open Technical Questions

These questions block a final model or deployment choice.

## Product and ontology

- Which first three owner rules are safety/compliance critical, and what is an unambiguous positive/negative example for each?
- Are there trusted access-control, gate-contact, POS, PLC, schedule or badge events that should replace visual inference?
- Is audio in scope, and is it necessary for any rule?
- What alert latency and maximum tolerated missed-event interval apply per rule?
- Is a track-local pseudonym sufficient, or is cross-camera identity genuinely required?

## Data and evaluation

- What cameras, codecs, resolutions, viewpoints, lighting and camera-hour volumes are representative?
- How are event start/end times and ambiguous intervals annotated? Who adjudicates disagreements?
- What is the acceptable false-alert budget per camera-hour/day for each rule?
- Can a site-held, access-controlled evaluation set be made available without moving raw video?
- What split prevents people, locations, scenes and near-duplicate clips leaking across train/test?

## Model and runtime

- Which detector classes and custom labels are needed at target resolution? What small model meets observation recall?
- Does tracking between detector calls preserve zone/duration accuracy under the actual camera view?
- Do pose, OCR, segmentation or a state classifier improve the first rules enough to justify cost?
- What is the smallest action model that distinguishes smoking or required-action completion at the target camera angle?
- Which runtime/export (OpenVINO, ONNX Runtime, TensorRT or other) supports the exact operators and target hardware?
- What is the measured FP32/FP16/INT8/INT4 accuracy and latency trade-off on every target tier?
- Can an NPU accelerate the selected operators without fallback that erases the benefit?

## Privacy/security/governance

- What exact fields can leave the site, to which processor, for what retention period and under whose key?
- Are redacted frames sufficient for review, and can redaction fail under occlusion?
- What access roles can view raw evidence vs metadata vs aggregate analytics?
- What human review and appeal workflow is required before a high-impact action?
- What model/configuration signing, audit and rollback controls are needed?

## Exit criteria

Do not close a question with a qualitative model recommendation. Close it with an owner-approved specification, a measured experiment, or an explicitly accepted risk.
