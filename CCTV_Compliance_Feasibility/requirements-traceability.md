# Mission Requirements Traceability Matrix

This matrix traces the major requirements in the supplied original context document to the consolidated report and supporting artifacts. Source headings are quoted or shortened from that document so another engineer can audit the mapping without rereading the conversation. A requirement is marked `covered`, `partially covered`, or `open` when it still needs owner input or measurement.

| ID | Original context source | Requirement traced | REPORT.md section | Supporting artifact | Status |
|---|---|---|---|---|---|
| T-01 | `TASK`, `FINAL OBJECTIVE` | Feasibility study, not a one-line model recommendation | Executive Summary, Final Engineering Conclusions | `architecture/executive-summary.md`, `decisions/decision-log.md` | covered |
| T-02 | `CONTEXT` | Continuous or near-real-time CCTV input | Problem Definition, AI/CV Pipeline | `architecture/prototype-and-production.md`, `experiments/experiment-matrix.md` | partially covered, target SLO open |
| T-03 | `CONTEXT` | Owner-defined rules rather than hard-coded model classes | Rule Engine Architecture, Owner-Configurable Rule Examples | `rule_engine/design.md`, `rule_engine/rule.schema.yaml` | covered |
| T-04 | `CONTEXT` | Separate perception, detection, tracking, temporal reasoning, rule evaluation, evidence and alerting | Proposed System Architecture, AI/CV Pipeline | `architecture/requirements-and-task-map.md`, `temporal_reasoning/design.md` | covered |
| T-05 | `PRIVACY AND DEPLOYMENT REQUIREMENTS` | Edge-only, cloud-only and hybrid deployment comparison | CPU, GPU/Edge, Cloud, Edge vs Cloud vs Hybrid, Privacy Architecture | `privacy/deployment-and-boundary.md`, `privacy/governance-checklist.md` | covered |
| T-06 | `PRIVACY AND DEPLOYMENT REQUIREMENTS` | CPU-only laptop must be considered seriously | CPU-Only Feasibility | `hardware/feasibility-matrix.md`, `experiments/experiment-matrix.md` | covered, capacity open |
| T-07 | `MODEL EVALUATION` | Compare detectors, trackers, pose, re-identification, transformers, VLMs, anomaly, segmentation, OCR, temporal and classical CV | Model Families, Detailed Model Comparison | `models/model-matrix.md`, `models/2026-landscape.md` | covered |
| T-08 | `IMPORTANT SYSTEM DESIGN QUESTION` | Compare single large model, specialised pipeline and hierarchical architecture | Alternative Architectures | `architecture/candidate-architectures.md` | covered |
| T-09 | `OWNER DEFINED RULES` | Events, objects, attributes, zones, windows, sequences, exceptions, thresholds, permissions and actions | Rule Engine Architecture, Examples | `rule_engine/design.md`, `rule_engine/rule.schema.yaml` | covered |
| T-10 | `OWNER DEFINED RULES` | Natural language may draft rules, but final execution must be structured and validated | Rule Engine Architecture | `rule_engine/design.md` | covered |
| T-11 | `QUANTIZATION AND MODEL OPTIMIZATION` | FP32, FP16, INT8, INT4, PTQ, QAT, pruning, distillation, sampling, ROI and acceleration | Quantization and Optimisation | `hardware/optimisation.md`, `experiments/ablation-ladder.md` | covered |
| T-12 | `REAL TIME REQUIREMENTS` | Separate camera FPS from AI FPS; assess sampling, triggers, ROI, asynchronous inference and buffering | AI/CV Pipeline, CPU/Edge Feasibility | `architecture/prototype-and-production.md`, `hardware/feasibility-matrix.md` | covered |
| T-13 | `PRIVACY AND SECURITY` | Minimise raw video, frames, clips, metadata, embeddings and reports; do not assume embeddings are safe | Privacy Architecture, Security Considerations | `privacy/deployment-and-boundary.md`, `evidence/design.md` | covered |
| T-14 | `COMPLIANCE` | Identify legal, privacy, security, HR and governance review areas without giving legal advice | Compliance Considerations | `privacy/governance-checklist.md` | covered |
| T-15 | `RELIABILITY` | False positives and false negatives, occlusion, lighting, night, crowds, weather, compression, failures, drift and adversarial behavior | Failure Modes and Metrics | `architecture/failure-modes.md`, `experiments/experiment-matrix.md` | covered |
| T-16 | `EVIDENCE` | Camera, timestamp, event, rule, conditions, confidence, IDs, zones, frames, clips, metadata, sequence and explanation | Evidence Generation Architecture | `evidence/design.md`, `temporal_reasoning/event.schema.json` | covered |
| T-17 | `ARCHITECTURAL PRINCIPLE` | Ask for smallest and simplest AI system per requirement | Executive Summary, Final Engineering Conclusions | `architecture/model-selection-gates.md`, `decisions/decision-log.md` | covered |
| T-18 | `FINAL OBJECTIVE` | Identify which events can be detected, required models, CPU/GPU needs and quantisation value | Final Engineering Conclusions | `models/model-matrix.md`, `hardware/feasibility-matrix.md` | covered conditionally |
| T-19 | `FINAL OBJECTIVE` | Define edge/cloud boundary and privacy design | Edge vs Cloud vs Hybrid, Privacy Architecture | `privacy/deployment-and-boundary.md` | covered |
| T-20 | `FINAL OBJECTIVE` | Represent temporal events and verify violations | Temporal Reasoning, Evidence Generation | `temporal_reasoning/design.md`, `rule_engine/design.md` | covered |
| T-21 | `FINAL OBJECTIVE` | Evaluate false positives/negatives and evidence quality | Metrics, Evaluation Methodology | `experiments/experiment-matrix.md`, `baseline/empirical-comparison-plan.md` | covered, thresholds open |
| T-22 | `FINAL OBJECTIVE` | Define the first working prototype and production evolution | Prototype Architecture, MVP, Production Architecture | `architecture/prototype-and-production.md` | covered |
| T-23 | `RESEARCH REQUIREMENT` | Prefer official docs, original papers and benchmark conditions; do not fabricate numbers | Model Comparison, Evaluation Methodology | `research/sources.md`, `research/published-benchmarks.md` | covered |
| T-24 | `SceneSolver Baseline Investigation` | Determine what exists, evidence, datasets, metrics, cost, reuse and gaps | Model Comparison, Final Conclusions | `baseline/scenesolver-analysis.md`, `baseline/repository-inventory.json` | covered |
| T-25 | `SceneSolver Baseline Investigation` | Define a reproducible comparison against new architectures | Recommended Experiment Matrix, Final Conclusions | `baseline/empirical-comparison-plan.md` | covered |
| T-26 | `MODEL COMPARISON TABLE` | Include purpose, accuracy, CPU/GPU, latency, memory, size, real time, edge, quantisation, fine tuning, complexity and role | Detailed Model Comparison | `models/model-matrix.md`, `models/2026-landscape.md` | covered |
| T-27 | `EXPERIMENT PLAN` | Measure detection, tracking, actions, temporal events, CPU/GPU latency, memory, power, quantisation, FP/FN and alert latency | Recommended Experiment Matrix | `experiments/experiment-matrix.md`, `experiments/benchmark-config.example.yaml` | covered |
| T-28 | `AUDIENCE`, `QUALITY CRITERIA` | Make study usable by engineers, architects, supervisors and privacy/security stakeholders | Entire report | `README.md`, `REPORT.md`, `privacy/governance-checklist.md` | covered |
| T-29 | `NEW EXPLORATION AREA` | Keep SceneSolver intact and store modular shared memory in a dedicated folder | Repository and all sections | `CCTV_Compliance_Feasibility/` | covered |
| T-30 | `COLLABORATION REQUIREMENT` | Record changed assumptions and leave persistent artifacts for another agent | Decisions, Sources, Validation | `decisions/decision-log.md`, `decisions/validation-log.md` | covered |
| T-31 | `COMPLIANCE TERMINOLOGY` | Define compliance as adherence to owner operational policy, separate from legal/regulatory/privacy/employment compliance | Problem Definition, Compliance Considerations | `architecture/requirements-and-task-map.md`, `privacy/governance-checklist.md` | covered by refinement |
| T-32 | `COST AND DEPLOYMENT IMPLICATIONS` | Compare total cost, hardware amortisation, power, storage, bandwidth, cloud and maintenance | GPU/Edge Feasibility, Cloud Feasibility | `hardware/feasibility-matrix.md` | covered as measurement framework, actual prices open |
| T-33 | `CURRENT MODEL LANDSCAPE` | Consider YOLO26/YOLOE-26 and Qwen3-VL/SmolVLM2 as candidates without assuming they win | Model Families, Final Conclusions | `models/2026-landscape.md`, `models/licensing-matrix.md` | covered by refinement |
| T-34 | `LICENSING` | Treat code/weights license, commercial restrictions, attribution, redistribution and deployment compatibility as selection gates | Detailed Model Comparison, Final Conclusions | `models/licensing-matrix.md`, `architecture/model-selection-gates.md` | covered by refinement |
| T-35 | `ABLATION AND INCREMENTAL VALUE` | Measure Detector+Tracker+Rules, then temporal, anomaly, VLM and sensor additions | Recommended Experiment Matrix | `experiments/ablation-ladder.md` | covered by refinement |

## Traceability interpretation

`Covered` means the report explicitly addresses the requirement and points to a persistent artifact. It does not mean the engineering question has been measured. `Partially covered` means the architecture and protocol exist, but target owner thresholds, hardware, data or policy information is still open.

## Gap rule

If a future change adds or removes a requirement, append a row with a new ID and update the decision log. Do not rely on a prose conclusion alone.
