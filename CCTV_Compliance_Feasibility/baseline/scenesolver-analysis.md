# SceneSolver Baseline Analysis

## Scope and method

This analysis reads tracked README/Insights/notebooks and committed output artifacts. It distinguishes repository evidence from claims in documentation. It does not treat notebooks that expect external Drive data/checkpoints as a reproducible benchmark.

## What SceneSolver already solves or attempts

| Capability | Repository evidence | Status for baseline |
|---|---|---|
| deterministic frame/scene ordering | `DatasetTools/` module, tests and README; numeric/temporal parsing, validation, reversible non-destructive preparation | strongest reusable component; directly useful for temporal evaluation |
| unsupervised visual anomaly signal | AE notebooks, training logs and inference artifacts | experimental research signal; threshold/domain behavior not established |
| binary anomaly/normal video classification | `facebook/timesformer-base-finetuned-k400` fine-tuning notebook and `timesformer_binary_reslts.txt` | empirical repository result, but only support 30 in recorded test and incomplete conditions |
| multiclass incident classification | seven-class notebook and `classification_report_TFM.json` | empirical result: accuracy 0.842857, macro F1 0.823514, weighted F1 0.839174, support 140; not generic compliance |
| conditional object detection | README/orchestrator describes YOLOv8 weapon/object detection only after anomaly/keyframe gating | pipeline idea reusable; target object recall and latency absent |
| CLIP keyframe/prompt scoring | Insights and committed JSON/plots | useful candidate selection/retrieval experiment; not calibrated event recognition |
| audio features and spectrogram AE | README, notebook and `training_history.json` | optional corroboration/novelty signal; no event-level accuracy or privacy case |
| tracking/behaviour | orchestrator stage and report fields | implementation/intent evidence; no MOT or rule-level measurements found |
| fusion/reasoning | orchestrator and report generation | pipeline integration idea; deterministic rule semantics not equivalent to owner DSL |
| RL temporal reasoning | RL+AE notebook explicitly labels RL3033 experimental; A100/T4-oriented cells | experimental, expensive and not needed for simple timers/sequence rules until proven |
| LLaVA explanation | LLaVA manifests/notebook and README explicitly marks stage experimental | narrative/review candidate; not authoritative policy evaluator |
| evidence/reporting | PDF/HTML/report artifacts; `analysis.json` has 320x240, 30 FPS, 3,366 frames, 112.2 sec and 44 generated anomaly records | useful evidence/report baseline; no reviewer or ground-truth quality metric |
| graceful optional dependencies | README says missing RL/librosa/liquid-audio degrades | operational idea reusable; full runtime still expects external models/checkpoints |

## What it does not establish

1. **Generic owner-defined events:** its trained labels are anomaly/normal and a seven-class incident set, not arbitrary zones, permissions, sequences, exceptions or deadlines.
2. **Open-ended perception contract:** no stable versioned observation/event schema is the central API.
3. **Authorization:** no demonstrated badge/access-control join or reliable non-biometric personnel identity.
4. **Production continuous operation:** no target-camera concurrency, dropped-frame, backpressure, restart, thermal, power or end-to-end alert benchmark.
5. **Tracking quality:** no HOTA/IDF1/MOTA, ID-switch, zone-entry or dwell accuracy result found in tracked artifacts.
6. **Calibration and alert workload:** score thresholds exist in code/report paths, but no reliability diagrams or false-alerts-per-camera-hour result.
7. **Site domain shift:** UCF-Crime-style internet surveillance footage is not evidence for a particular owner's camera angles, lighting, staff, zones or policy.
8. **Privacy boundary:** local/cloud behavior is not a documented deployment control plane; reports and optional external services may expose data.
9. **Reproducibility:** full notebooks use external Drive paths, downloads and checkpoints not tracked in the repository; hardware/run manifests are incomplete.

## Important internal inconsistencies or risks

- The README says the multiclass head covers 13–14 crime categories, while the final training notebook defines seven classes and the committed report contains seven classes. The baseline report must use the measured seven-class artifact, not the broader prose claim.
- The binary report records accuracy on 30 samples; this is too small to infer production generalisation and has no camera/site/time split in the artifact.
- The multiclass notebook balances classes by duplicating paths before train/validation/test splitting. Unless the external data and split code prove otherwise, identical videos may cross partitions, creating potential leakage. This must be audited before treating 0.842857 as a clean estimate.
- The report-generation sample emits many repeated captions/labels over a 112.2-second 320x240 file, but no ground truth or reviewer assessment proves that “44 anomalies” are true violations.
- AE/CLIP scores are useful continuous signals but the examples do not establish calibrated probabilities or owner-rule precision/recall.
- A stage being implemented is not the same as a stage being empirically demonstrated; RL3033, LLaVA, YOLO weapon detection and tracking are explicitly or effectively experimental in the tracked documentation.

## What should be reused

**Reuse unchanged behind adapters:**

- DatasetTools ordering/validation and non-destructive manifests.
- Evidence lineage/report layout concepts, after replacing narrative-first logic with event/rule manifests.
- Conditional/triggered expensive inference as an optimisation hypothesis.
- Frame/keyframe sampling utilities after event recall tests.
- SceneSolver artifacts as a comparison arm in experiment E-06/E-11.

**Reuse as candidates, not defaults:**

- TimeSformer binary/multiclass weights and temporal sampling.
- AE anomaly signal.
- CLIP prompt scoring.
- YOLO detector variant.
- audio anomaly features.
- RL temporal model and LLaVA narrative.

**Do not carry into the compliance core without evidence:**

- anomaly-gated incident taxonomy as the event ontology;
- RL as the timer/sequence engine;
- VLM prose as the decision;
- face/appearance identity as the default authorization mechanism;
- any report's threshold as a production operating point.

## Baseline experiment definition

Run three arms on the same labelled, site-like clips:

- **A0:** sampled small detector + tracker + geometry + deterministic rules;
- **A1:** A0 + SceneSolver AE/CLIP candidate signal;
- **A2:** A0 + selected TimeSformer/VideoMAE action model or VLM review.

Compare rule-event recall, false alerts/camera-hour, boundary error, alert latency, resource use, evidence sufficiency and privacy export volume. This tests whether SceneSolver adds value rather than assuming that all stages should be retained.

## Final baseline conclusion

SceneSolver can defensibly serve as an **established research/reference baseline** and component library for the feasibility study. It cannot currently be claimed as the compliance architecture or as evidence that a complete system runs on a laptop or in continuous real time. The new prototype should be independently structured around typed observations, temporal state, deterministic rules and bounded evidence, with SceneSolver components plugged in only when an experiment shows incremental value.
