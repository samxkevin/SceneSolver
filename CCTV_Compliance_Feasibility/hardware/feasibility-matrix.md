# Hardware Feasibility Matrix

These are capability hypotheses and deployment boundaries, not claimed FPS. Measure with the protocol in `../experiments/experiment-matrix.md`.

## Tiers

| Tier | What it can plausibly host | What is not assumed | Recommended use |
|---|---|---|---|
| CPU-only laptop | decode, sampled small detector, tracker, geometry, state/rules, local evidence; perhaps tiny pose/OCR/action model | full TimeSformer/VideoMAE/VLM continuously; multi-camera capacity | P0/P1 correctness and minimum viable edge baseline |
| Laptop integrated GPU/NPU | small detector/pose/OCR with supported export; CPU rules/tracking; selective small temporal model | NPU availability/operator coverage, shared-memory contention, VLM throughput | low-power single/few-camera edge after target measurement |
| Consumer GPU workstation | training/fine-tuning, high-rate detector/tracker, temporal models, selective VLM | production thermal/cost/availability equivalence | development, evaluation and small on-prem deployment |
| Dedicated edge GPU | multi-stream decode plus optimised detectors/trackers and selective temporal models | exact camera count without scene/codec/thermal test | production on-prem when CPU tier fails capacity gate |
| Cloud GPU | central training, batch/near-real-time analysis, large VLM/video foundation model, fleet analytics | privacy permission, predictable egress/latency/cost | cloud-permitted hybrid escalation or cloud-only deployment |

## Workload placement

| Workload | CPU laptop | Integrated GPU/NPU | Edge GPU | Cloud GPU |
|---|---|---|---|---|
| Decode/health/timestamps | yes | yes | yes | yes, but network becomes dependency |
| Small detector every N frames | measure; likely first target | measure | yes | yes |
| Tracker and polygon rules | yes | yes | yes | yes |
| Long-duration timers/absence/sequence | yes | yes | yes | yes |
| Pose/OCR | low rate / small model | likely | yes | yes |
| TimeSformer/video transformer | selective/offline candidate | not assumed | selective candidate | feasible candidate; still latency/cost test |
| VLM narrative | not default | not default | optional quantised/triggered | strongest option if data policy allows |
| Training/fine-tuning | not recommended except tiny models | not recommended | possible for small models | preferred for larger models |
| PDF/HTML rendering | yes, local | yes | yes | yes; avoid blocking inference |

## Measurement protocol

For each hardware tier, record:

- exact device/SKU, OS, kernel/driver, runtime and model commit;
- CPU/GPU/NPU frequency/power mode and thermal state;
- camera source, codec, resolution, encoded FPS and duration;
- decoded frames, inference sample rate, input size, ROI, batch size and concurrency;
- preprocessing, model, postprocessing, tracking, rules and evidence time separately;
- p50/p95/p99 per-stage latency, end-to-end alert latency, throughput and dropped frames;
- RSS, peak RAM, VRAM/shared memory, model load/startup time;
- power at idle and steady state where a trustworthy meter is available;
- accuracy/calibration and rule-level FP/FN under the same run;
- queue depth and thermal throttling over at least the agreed soak period.

## Capacity equation (for planning, not a result)

For camera `c`, define:

```text
compute_demand_c = sampled_fps_c * (detector_ms + postprocess_ms + optional_stage_ms)
```

Then include decode, tracker, rule, evidence, safety margin and concurrent workloads. A detector's single-stream FPS does not equal the number of production cameras. The capacity test must include worst-case scene density, evidence capture and model warm-up.

## Hardware facts used as context

- OpenVINO documentation lists CPU, integrated/discrete Intel GPU and NPU support classes, subject to drivers and operator support.
- NVIDIA's Jetson Orin Nano Super guide lists up to 67 INT8 TOPS, 8GB memory and configurable 7–25W; these are hardware ceilings/context, not a CCTV throughput promise.
- Intel product briefs advertise “up to” platform TOPS for selected Core Ultra SKUs; SKU, thermal and runtime matter.

See [`../research/sources.md`](../research/sources.md) for official links and conditions.

## Acceptance gates (to be set with owners)

The experiment plan uses placeholders until owners provide service levels. A gate must specify, per rule and hardware tier:

- maximum p95 alert latency;
- minimum observation recall and rule-event recall;
- maximum false alerts per camera-hour;
- maximum dropped/late frame interval;
- maximum RAM/VRAM/power/thermal envelope;
- maximum concurrent cameras at specified resolution/sample rate;
- restart/recovery time and offline behavior.
