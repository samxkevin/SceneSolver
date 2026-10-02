# Quantisation and Runtime Optimisation Plan

## Precision choices

| Mode | Likely benefit | Risks / caveats | Validation |
|---|---|---|---|
| FP32 | reference accuracy and portability | highest weight/activation memory and bandwidth | retain as accuracy baseline |
| FP16/BF16 | GPU throughput/memory reduction | CPU/NPU support varies; numerical changes | compare logits, event recall and latency |
| INT8 PTQ | lower memory/bandwidth, accelerator-friendly | calibration/domain shift, operator fallback, confidence recalibration | representative calibration set + held-out site test |
| INT8 QAT | can recover accuracy for sensitive models | training complexity and deployment graph constraints | compare QAT/PTQ to FP32 on rare/ambiguous cases |
| INT4 weight-only | substantial weight memory reduction for some transformers | activation/KV cache and kernel support; may not accelerate detector; quality loss | target runtime/provider test, not file-size-only |
| Pruning | may reduce compute if structured and supported | unstructured zeros may not speed inference; accuracy loss | measure actual kernel/runtime speed |
| Distillation | smaller student and lower runtime cost | rare-event recall and calibration can degrade | event-level stratified comparison |

ONNX Runtime documents static/dynamic quantisation and QDQ/QOperator formats; its general guidance differentiates CNN and transformer use. OpenVINO documents calibration and target-device options. These are implementation starting points, not guarantees for every exported graph.

## Order of operations

1. Freeze a correctness reference: exact model, preprocessing, postprocessing, tracker, thresholds and data hash.
2. Export without optimisation and verify output equivalence on a fixed clip.
3. Benchmark FP32/FP16 on the target provider.
4. Calibrate INT8 on representative *deployment* frames, including lighting/occlusion/background and negative examples; never use the test set for calibration.
5. Validate graph/provider coverage and detect silent CPU/FP32 fallback.
6. Compare class/observation recall, track continuity, rule-event recall, FP per camera-hour, calibration, latency, memory and power.
7. Only then test QAT, INT4, pruning or distillation for the bottleneck stage.

## System-level optimisation before model compression

The largest practical gains may come from:

- decode once and share frames among consumers;
- process detector every N frames and tracker between calls;
- trigger higher-rate/large-model work only on motion, zone occupancy, uncertainty or a rule candidate;
- crop ROI while retaining a context frame for evidence;
- lower resolution only after measuring small-object recall;
- use adaptive sampling for static scenes and alert candidates;
- asynchronously write evidence/report artifacts;
- cache text embeddings and static camera calibration;
- batch across cameras only when it does not violate alert latency;
- use hardware decode and zero-copy paths where stable;
- drop optional VLM work under queue pressure while keeping core rules alive.

## Quantisation-specific pitfalls

- A smaller model file is not proof of lower latency; memory may be shared, dequantisation may dominate, and unsupported operators may fall back.
- Quantisation changes scores; thresholds must be re-tuned/calibrated and versioned.
- An accuracy average can conceal a catastrophic rare-rule regression; evaluate by camera condition and event type.
- VLM INT4 may make weights fit but leave vision encoder, activations, KV cache or prompt/video token processing expensive.
- LoRA reduces adaptation cost, not necessarily deployment memory/latency. Merge/prune/compile only if the runtime preserves behavior.

## Deliverable for each candidate model

```yaml
model_id: exact-name-and-commit
input: {resolution: null, frames: null, roi: null}
reference_precision: FP32
candidate_precisions: [FP16, INT8]
runtime: exact-runtime-and-provider
calibration_set: manifest-hash
metrics:
  observation_recall: null
  rule_event_recall: null
  false_alerts_per_camera_hour: null
  p95_alert_latency_ms: null
  peak_ram_mb: null
  peak_vram_mb: null
  watts: null
status: pending
```
