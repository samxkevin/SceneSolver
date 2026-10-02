# P0 Failure and Missing-Input Inventory

## Measured failures and limitations

### Rule engine

- The synthetic evaluator accepts the checked-in fixtures and rejects a fixture missing `quality` and a rule missing `then`.
- It is intentionally limited to the operators exercised by the P0 fixtures. It is not a production rule service or a complete JSON Schema implementation.

### Replay harness

- Video decode was not run. The replay input is a structured frame manifest with precomputed synthetic detections.
- Observation output is therefore an adapter contract demonstration, not detector accuracy.
- The tracker uses one supplied `track_hint`; no multi-object tracking benchmark was attempted.
- Runtime values are local Python contract timings and must not be interpreted as camera throughput.

### Specialised CV reference

- No pretrained detector ran. The path uses synthetic bounding boxes as detector output.
- The result demonstrates detector output to tracker/trajectory to zone/duration to rule separation only.
- Accuracy, false alerts, misses, RAM, VRAM and power are not available from this run.

## SceneSolver reproduction blockers

The cheapest reproducible action was inspection of the committed report artifact. A full SceneSolver run was not executed because:

1. The source video is not present in the checkout.
2. The committed `analysis.json` references Google Drive frame paths that are not present at those absolute paths.
3. `torch`, `cv2`, `numpy`, `ultralytics`, `psutil` and `jupyter` are unavailable in this execution environment.
4. Only `SpectrogramAnalysis/checkpoints/checkpoint_epoch_35.pth` was found by the checkpoint scan. This does not establish a runnable TimeSformer or YOLO configuration.
5. Relevant notebooks use external data, checkpoints or Drive paths and do not provide a deterministic command-line inference entry point.
6. The committed artifact contains no stage timing, report-generation time, memory or VRAM measurements.

The measured artifact inspection remains useful: metadata records 3366 frames, 30 FPS, 320x240 resolution and 112.2 seconds; the artifact contains 44 anomaly records and 55 packaged JPEG files. The 44 absolute frame references in the records are not present at their recorded paths in this checkout.

## Quantisation

Not run. There is no exact model plus runtime plus target hardware combination already available for a cheap FP32/FP16/INT8 comparison. The report retains quantisation as a pending experiment and makes no CPU-feasibility claim from precision labels.

## VLM review

Not run. No lightweight VLM was readily available without adding model infrastructure. The report therefore retains only the architectural evidence: bounded evidence input, advisory output, deterministic rule authority and no silent event-ledger override.

## Customer/site evidence

No customer video, camera geometry, owner policy thresholds, target hardware, power meter, cloud quote, site labels or privacy approval were available. No site accuracy, camera count, FPS, cost or production SLO is claimed.
