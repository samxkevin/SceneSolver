# P0 Evidence Summary

**Status:** Feasibility study with empirical evaluation protocol; measurements pending where target data/hardware are unavailable.

This summary reports only the focused P0 pass. It separates measured outputs, existing repository evidence, published context, engineering interpretation and open work. The four-arm comparison protocol has not been executed; the P0 results below are not comparative benchmark results.

## MEASURED

| Evidence | Result | What it establishes | Limitation |
|---|---|---|---|
| Rule engine replay | 11/11 checked synthetic rule fixtures passed; 2/2 malformed-input fixtures were rejected as expected; all deterministic replay checks passed | Selected implementation conformance for true, false, unknown, cooldown, exception and sequence cases | Expected outputs are encoded in checked-in fixtures; synthetic cases are not independent validation of business semantics |
| Model-neutral replay | 2 FPS source timing, 13 structured frames processed by the adapter, 7 sampled, 6 skipped, 0 dropped; 7 observations, 3 events, 1 track, confirmed rule decision and bounded metadata evidence manifest; the dwell interval remains open with 5.0 seconds observed up to stream end | The proposed event-to-evidence contract can be exercised without coupling rule logic to a model, and incomplete intervals are not treated as completed exits | Structured frames and precomputed detections replaced video decode and perception |
| Specialised CV reference path | 13 detector-adapter records, 1 track, 5.0 second observed zone dwell open at stream end, 3.0 second rule threshold and confirmed decision | Learned-perception output can be separated from tracking/trajectory, deterministic zone duration and policy evaluation | No learned detector ran; no visual accuracy or deployment throughput |
| SceneSolver artifact inspection | Existing `analysis.json` parsed; metadata records 3366 frames at 30 FPS, 320x240, 112.2 seconds; 44 anomaly records and 55 packaged JPEG files | The committed repository artifact and its outputs can be inspected and retained as baseline evidence | This is artifact inspection, not SceneSolver inference runtime or new accuracy measurement |

Wall-time values are retained in the machine-readable JSON artifacts for reproducibility of the small scripts. They are **synthetic contract replay runtime** or artifact inspection time, not CCTV inference latency, camera throughput, deployment FPS or real-time system performance.

### Rule result details

- `confirmed`: zone dwell, required action absent before deadline, healthy-window absence, authorization without exception and correct sequence ordering.
- `not_triggered`: gate below duration, action completed before deadline and reversed sequence ordering.
- `unknown`: camera/data gap during a required healthy observation window.
- `suppressed_by_exception`: an otherwise true unauthorized-zone condition with an active exception.
- Cooldown/debounce case: a one-second open interval did not qualify; two qualifying interval candidates at 3 and 8 seconds yielded one cooldown-qualified interval start anchor under a 10 second cooldown. P0 does not measure online alert latency or execute an alert scheduler.

### P0 semantic limitations

The evaluator is intentionally incomplete and does not establish full production rule semantics. It currently does not establish:

1. continuous health coverage across an entire temporal interval;
2. unknown propagation in every sequence case;
3. complete unknown handling for missing simple events;
4. alert candidate extraction for every possible nested rule expression;
5. complete JSON Schema validation;
6. the configured `unknown_policy` action semantics (`suppress`, `delay`, `escalate_review`, `treat_as_false`).

These are transparency limits for the focused P0 pass, not a request to implement a production rule engine in this study.

## REPOSITORY EVIDENCE: HISTORICAL SCENESOLVER METRICS, NOT CCTV COMPLIANCE VALIDATION

The existing SceneSolver repository artifacts report:

- binary TimeSformer test accuracy 0.9667 on support 30;
- seven-class report accuracy 0.842857, macro F1 0.823514, weighted F1 0.839174, support 140;
- a report-generation artifact with 3366 source frames, 30 FPS, 112.2 seconds, 320x240 and 44 generated anomaly records;
- staged AE, TimeSformer, conditional YOLO, audio, tracking/behaviour, fusion, experimental RL and LLaVA/report concepts.

P0 did not retrain or rerun these models. The full inference path was not reproducible in this checkout because the source video, exact model configuration and required runtime dependencies were unavailable. See `p0/scenesolver_baseline_results.json` and `p0/failure-inventory.md`.

## PUBLISHED

No new deployment measurement was produced from a published benchmark. Existing published model and runtime values remain contextual evidence in `research/published-benchmarks.md` and `research/sources.md`. They are not substituted for site accuracy, camera capacity, latency, memory, power or cost.

## INFERENCE

- A deterministic rule layer can be tested independently of the learned perception component.
- A model-neutral event seam makes it possible to compare SceneSolver outputs, specialised CV outputs and future temporal/VLM/sensor adapters under the same policy evaluator.
- The P0 pass supports architectural feasibility of the separation. It does not prove production performance.
- Sensor integration remains a parallel experimental arm alongside temporal, anomaly and VLM additions. It is not assumed to be an additive final stage.

## OPEN

| Evidence | Status | What remains |
|---|---|---|
| Rule engine replay | measured on synthetic traces | Validate against owner-approved rule semantics and site-like replay data |
| SceneSolver baseline | measured repository artifact plus inspection | Re-run inference only when source video, checkpoints, dependencies and target hardware are available |
| Specialised CV path | measured contract path | Run an actual lightweight detector on representative video and measure accuracy, latency and resources |
| Quantisation | pending | FP32/FP16/INT8 comparison on one exact model/runtime/hardware combination |
| VLM review | pending | Small advisory experiment only if a model is already approved and readily available |
| Sensor integration | pending parallel arm | Compare sensor substitution/join against core CV on a rule where a trusted sensor exists |
| Deployment feasibility | pending | Site data, target hardware, power, storage, bandwidth, egress, maintenance and owner thresholds |

## Submission conclusion

The P0 evidence supports a **credible architectural direction**, not a proven deployment. The first prototype should remain small: model-neutral event and rule contracts, deterministic replay, one lightweight perception adapter, bounded evidence and explicit unknown/degraded handling. Target-site accuracy, camera capacity, quantisation benefit, VLM value, sensor value, cost and legal or governance approval remain experimental or organisational work.
