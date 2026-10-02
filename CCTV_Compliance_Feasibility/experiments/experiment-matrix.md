# Empirical Experiment Matrix

## Ground rules

Do not invent acceptance thresholds. Owners must set them per rule based on harm/cost. Every run stores dataset manifest hash, code/model/runtime commits, hardware, camera conditions, precision, input dimensions, sample rate, concurrency and raw predictions.

## Dataset plan

Create three data sources:

1. **Synthetic traces:** generated detections/events to test rule truth tables, durations, order, absence, gaps, exceptions and cooldowns.
2. **Controlled staged scenes:** labelled site-like camera views with consent/approval, repeatable positive and hard-negative actions, lighting/occlusion/crowd variants.
3. **Naturalistic holdout:** time-separated and camera-separated real footage, including normal operations and drift conditions. Keep a locked test set.

Split by camera/site/time/person/session where possible; never let near-duplicate frames or duplicated paths cross splits. UCF-Crime/SceneSolver can be used as a research comparison for generic anomaly/incident classification, but not as a substitute for owner-rule data.

## Matrix

| ID | Question | Dataset/labels | Hardware/conditions | Metric | Output / acceptance |
|---|---|---|---|---|---|
| E-01 | Can detector expose required objects? | boxes/classes per camera condition | CPU, iGPU/NPU, workstation, edge GPU; target resolution | precision/recall/mAP, small-object recall, calibration | compare smallest candidate vs stronger candidate; owner sets minimum observation recall |
| E-02 | Does sampling lose events? | event start/end and short duration cases | sampled 1/2/5/10 FPS; detector intervals | event recall, boundary error, alert latency | choose minimum sampled rate satisfying each rule |
| E-03 | Is tracking adequate for zones/dwell? | track IDs and entry/exit/dwell truth | ByteTrack/SORT/BoT-SORT, detector gaps and crowd/occlusion | HOTA, IDF1, ID switches, zone-event recall, dwell error | promote based on rule metrics, not MOT alone |
| E-04 | Does pose/OCR/segmentation add value? | action/reading/region labels | same camera/hardware with and without stage | incremental event recall, FP/camera-hour, latency | keep only if gain exceeds cost and privacy review |
| E-05 | Which action formulation works? | smoking/required-action temporal labels with hard negatives | tiny feature model vs TCN/GRU vs video transformer/VLM | segment F1, event recall, boundary error, calibration | no generic action claim; per-rule result |
| E-06 | Does anomaly detection help? | normal + labelled unusual/permitted events | AE/CLIP baseline, sampled stream | AUROC/AUPRC only as candidate, alert workload, novelty-to-violation precision | use only for candidate generation if value is proven |
| E-07 | Does quantisation preserve behavior? | fixed held-out clips including rare cases | FP32/FP16/INT8/INT4 where supported | delta event recall, calibration, p95 latency, memory | reject any unacceptable rare-rule regression or fallback |
| E-08 | CPU feasibility | representative 30-60 min per camera | exact laptop, cold/warm, long soak | FPS, p95 per stage, CPU/RAM/temp/power, drop rate | owner-defined cameras and latency gate |
| E-09 | iGPU/NPU feasibility | same as E-08 | exact integrated device/provider/driver | same; include CPU fallback detection | prove benefit over CPU, not just device support |
| E-10 | edge GPU capacity | multi-camera replay | exact device, 1..N cameras, thermal steady state | concurrency, p95 alert latency, VRAM/power, drops | maximum safe camera count with margin |
| E-11 | cloud/VLM value | selected bounded evidence with blinded labels | exact cloud model/region/batch | review accuracy, grounded citation rate, latency, cost, egress volume | use only if incremental value justifies privacy/cost |
| E-12 | end-to-end alert | labelled trigger streams and outage injections | all target tiers | capture-to-alert p50/p95/p99, evidence completeness | alert SLO plus degraded mode behavior |
| E-13 | rule correctness | synthetic event traces + replay logs | no model required | precision/recall against expected truth, determinism hash | 100% schema/semantic unit tests before live test |
| E-14 | evidence quality | reviewer study on blinded cases | local and hybrid export modes | condition citation coverage, reviewer agreement, timestamp error, storage/event | owner/security approval |
| E-15 | robustness | night, blur, rain, crowd, occlusion, camera motion, codec, network loss | stratified target hardware | per-condition event metrics, unknown rate, recovery time | no aggregate-only approval |
| E-16 | drift monitoring | rolling post-pilot sample + labels | production shadow | score/feature drift, alert rate, review correction, calibration | trigger retraining/recalibration/rollback policy |

## E-17: Same-input architecture comparison

Run four arms on the same frozen replay manifest and rule definitions:

| Arm | Definition | Required measurements |
|---|---|---|
| S0 | SceneSolver reference pipeline, core and optional stages reported separately | total and stage latency, RAM/VRAM, frames, outputs, false alerts, misses, report time, failure cases |
| S1 | specialised detector + tracker + geometry + deterministic rules | same measurements plus rule-event quality |
| S2 | hierarchical typed event/state core with deterministic rules and bounded evidence | same measurements plus queue/unknown/degraded state |
| S3 | S2 plus bounded optional VLM review | same measurements plus VLM grounded review accuracy, citations, privacy export and per-call cost |

The harness records unavailable fields as `not_available`, not zero. It keeps cold/warm startup separate and never silently substitutes a different SceneSolver checkpoint or data path. Full protocol: [`../baseline/empirical-comparison-plan.md`](../baseline/empirical-comparison-plan.md).

## E-18: Ablation retention ladder

Add components in order: detector/tracker/rules, temporal model, anomaly candidate generation, VLM review, sensor integration. For each addition measure incremental rule recall, false alerts, misses, unknown rate, latency, RAM/VRAM, frames processed, power, privacy exposure, storage, cloud/egress cost, licensing and failure recovery. Retain only after measurement, incremental-value, resource, privacy and reliability gates pass. Full protocol: [`ablation-ladder.md`](ablation-ladder.md).

## Latency decomposition

Measure from source timestamp and separately:

```text
decode -> sample queue -> inference -> postprocess/tracker -> state/rule
       -> evidence capture -> alert transport -> human UI
```

The required result is alert latency distribution and dropped/unknown intervals, not only model FPS.

## Accuracy and reliability metrics

- **Detection:** precision/recall, mAP where appropriate, per-class and small-object recall, calibration error.
- **Tracking:** HOTA, IDF1, MOTA, ID switches, fragmentation, zone-entry/exit/dwell error.
- **Temporal:** segment/event precision/recall/F1, boundary error, time-to-detect, late/missed intervals.
- **Rules:** precision, recall, F1, false alerts per camera-hour, false negatives per camera-hour, unknown rate, duplicate-alert rate, cooldown correctness.
- **System:** p50/p95/p99 latency, queue age, dropped frames, restart/recovery, storage/event and egress volume.
- **Human/evidence:** reviewer agreement, evidence sufficiency, correction/retraction, time to verify.

## Acceptance procedure

1. Freeze candidate and configs.
2. Run on calibration/validation only; tune thresholds.
3. Lock test manifest.
4. Run each precision/hardware/concurrency condition twice or more as appropriate, recording variance.
5. Stratify by camera and condition; inspect worst cases.
6. Report confidence intervals/uncertainty when sample size permits.
7. Do an error review with owners; update ontology, not just threshold, when labels are ambiguous.
8. Record decision in `decisions/decision-log.md` and preserve rejected candidates.
