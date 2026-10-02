# P0 Evidence Summary

**Status:** Feasibility study with empirical evaluation protocol; measurements pending where target data/hardware are unavailable.

This summary reports only the focused P0 pass. It separates measured outputs, existing repository evidence, published context, engineering interpretation and open work.

## MEASURED

| Evidence | Result | What it establishes | Limitation |
|---|---|---|---|
| Rule engine replay | 11/11 synthetic rule cases passed; 2/2 malformed-input fixtures were rejected as expected; all deterministic replay checks passed | Zone entry/dwell, gate duration false case, required action before deadline, absence, unknown camera gap, cooldown/debounce, authorization/exception and sequence ordering preserve true/false/unknown behavior | Synthetic traces only; evaluator covers only P0 operators |
| Model-neutral replay | 13 structured frames decoded by the adapter, 7 sampled, 6 skipped, 0 dropped; 7 observations, 3 events, 1 track, confirmed rule decision and bounded metadata evidence manifest | The proposed decode-to-evidence contract can be exercised without coupling rule logic to a model | Structured frames and precomputed detections replaced video decode and perception |
| Specialised CV reference path | 13 detector-adapter records, 1 track, 5.0 second zone dwell, 3.0 second rule threshold, confirmed decision; measured harness runtime 0.186 ms | Learned-perception output can be separated from tracking/trajectory, deterministic zone duration and policy evaluation | No learned detector ran; no visual accuracy or deployment throughput |
| SceneSolver artifact inspection | Existing `analysis.json` parsed in 0.341 ms; metadata records 3366 frames at 30 FPS, 320x240, 112.2 seconds; 44 anomaly records and 55 packaged JPEG files | The committed repository artifact and its outputs can be inspected and retained as baseline evidence | This is artifact inspection, not SceneSolver inference runtime or new accuracy measurement |

### Rule result details

- `confirmed`: zone dwell, required action absent before deadline, healthy-window absence, authorization without exception and correct sequence ordering.
- `not_triggered`: gate below duration, action completed before deadline and reversed sequence ordering.
- `unknown`: camera/data gap during a required healthy observation window.
- `suppressed_by_exception`: an otherwise true unauthorized-zone condition with an active exception.
- Cooldown/debounce case: a one-second open interval did not qualify; two qualifying candidates at 3 and 8 seconds emitted one alert under a 10 second cooldown.

## REPOSITORY EVIDENCE

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

The P0 evidence supports a **feasible architecture**, not a proven deployment. The first prototype should remain small: model-neutral event and rule contracts, deterministic replay, one lightweight perception adapter, bounded evidence and explicit unknown/degraded handling. Target-site accuracy, camera capacity, quantisation benefit, VLM value, sensor value, cost and legal or governance approval remain experimental or organisational work.
