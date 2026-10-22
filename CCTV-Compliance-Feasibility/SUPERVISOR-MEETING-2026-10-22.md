# Supervisor meeting — 2026-10-22 (decision review, not implementation approval)

**Status:** draft briefing. No candidate has been selected or P1 CCTV run performed. Based on the existing feasibility scaffold, synthetic P0 results and current model seed audit. The accompanying 10-slide PPTX is prepared as a separate deliverable.

## Meeting objective

Show what exists; explain the current SceneSolver **reference** versus **proposed CCTV future state**; ask the supervisor which candidate families to retain, eliminate or investigate and what P1 conditions may be approved.

## Presentation order and speaker cues

1. **Purpose and decisions.** We seek direction, not a declaration of a winning model.
2. **Owner-defined problem.** Restricted-zone dwell is a policy and temporal question, not a whole-clip anomaly label.
3. **Current SceneSolver Reference vs Proposed CCTV Future State.** Do not call the seven-class classifier the CCTV baseline or an approved benchmark. Ask whether a formal benchmark should be defined.
4. **Architecture.** Perception -> tracking -> temporal state -> deterministic rules -> evidence. VLM may advise on bounded evidence; trusted sensors are a parallel input where suitable. Arena is only controlled development-time evaluation.
5. **P0 evidence.** 11/11 synthetic rule fixtures, 2/2 invalid input checks, deterministic replay; 13 structured frames, 7 sampled, 3 events, 1 track, 3-second dwell decision; no video detector or end-to-end performance proved.
6. **Model roles.** Grounding DINO and OWLv2 = text-grounded detection; DINOv3 and NV-DINOv2 = representation; SAM3 = promptable segmentation; TAPNext = point trajectories, not semantic detection; NVILA/CuMo/Qwen/InternVL = advisory multimodal analysis; geometry and world models only where rule-fit warrants.
7. **Trade-offs.** Model/task compatibility, rare-rule recall, false alerts/camera-hour, timestamps, p95 latency, concurrency, RAM/VRAM, privacy, exact weights and dependency rights. Released NVILA and CuMo weights are CC BY-NC 4.0; NVIDIA NV-DINOv2 is a conditional hardware/runtime path, not automatic deployment clearance.
8. **Arena/control.** Hold the clip manifest, prompts, camera geometry, hardware, precision and thresholds fixed; published results stay separately labeled.
9. **Open issues.** Candidate names Florence 3 and DINOv2.5 remain unresolved; no invented identities. No field-reliability gate has been agreed.
10. **Supervisor decisions.** Which rule? Which test corpus and permission? Which target device and camera concurrency? Which rule-level acceptance thresholds? Which model families retained / eliminated / investigated? Which defined benchmark? Approval to start P1 only after these are agreed.

## P1 proposed controlled evaluation (NOT production implementation)

- Freeze an approved consent/privacy-classified clip manifest with hashes, camera, resolution/FPS/codec/duration, conditions, zone geometry and ground-truth entry/dwell intervals. Lock test partition.
- Use one person perception model with the established downstream observation/track/event/rule/evidence contracts unchanged. Introduce one challenger only after the first fair run.
- Report observation precision/recall, small-person recall, false/missed zone entries, dwell timing error, false alerts/camera-hour, unknown/degraded time, cold load, p50/p95 end-to-end latency, RAM/VRAM, throughput, skipped/dropped frames and full reproducibility metadata.
- No retraining, VLM, entire SceneSolver rebuild or production implementation in this phase. Do not make real-time claims without measured end-to-end alert latency and concurrency.

## Evidence legend

- **REPO FACT:** directly confirmed in branch or P0 artifacts.
- **PUBLISHED:** official model/vendor/paper statement under its actual conditions, never an Arena run.
- **INFERENCE:** possible fit to a rule, not site-proven.
- **HYPOTHESIS:** a controlled proposed comparison.
- **OPEN:** missing checkpoint/license/runtime/actual site measurement or supervisor decision.

## Repository anchor files

[README](../README.md), [executive summary](architecture/executive-summary.md), [model matrix](models/model-matrix.md), [supervisor seed survey](models/supervisor-non-ultralytics-survey.md), [licensing matrix](models/licensing-matrix.md), [P0 summary](experiments/p0-summary.md), [experiment matrix](experiments/experiment-matrix.md), [sources](research/sources.md).

**Branch policy:** do not merge into main without approval. Research documentation only until P1 is explicitly authorized.
