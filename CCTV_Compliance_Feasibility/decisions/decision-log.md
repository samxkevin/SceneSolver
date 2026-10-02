# Decision Log

Append entries; do not erase prior assumptions. Dates are UTC.

## D-001 - 2026-10-01 - Separate perception from policy

- **Previous assumption:** A strong anomaly/incident classifier could be the core of generic CCTV compliance.
- **New evidence:** Owner requirements include duration, permissions, zones, ordering, exceptions, absence, cooldowns and cross-camera joins. These are policy/state semantics rather than a single visual class. SceneSolver itself stages evidence and reasoning but its reported task is anomaly/incident analysis.
- **Why it changed:** A classifier label cannot by itself provide deterministic temporal replay, authorization joins or auditable condition satisfaction.
- **New conclusion:** The target contract is typed observations -> temporal state -> deterministic rule evaluation -> evidence. Learned models supply only the observations that cannot be obtained deterministically.
- **Uncertainty:** The minimum model for hard actions such as smoking or required-action completion is still open.

## D-002 - 2026-10-01 - SceneSolver is a baseline/reference, not the target system

- **Previous assumption:** Extend the existing pipeline directly.
- **New evidence:** It contains a staged TimeSformer/AE/YOLO/audio/tracking/fusion/RL/LLaVA/report design and useful data tooling, but the tracked evidence lacks target-site camera-hour metrics, production latency, and generic rule evaluation. Its multi-class result is seven classes while the README also describes 13-14 UCF-Crime categories.
- **Why it changed:** The task has a different target ontology and operational boundary.
- **New conclusion:** Preserve SceneSolver and evaluate selected components behind adapters; build an isolated feasibility prototype first.
- **Uncertainty:** Whether its TimeSformer or AE can add measurable value after the new benchmark is run.

## D-003 - 2026-10-01 - VLM is optional, not authoritative

- **Previous assumption:** LLaVA/VLM should explain and potentially decide the event.
- **New evidence:** VLMs are broad but expensive, probabilistic and difficult to calibrate for exact timestamps and policy semantics. SceneSolver marks its LLaVA stage experimental and uses it for narrative.
- **Why it changed:** Routine zone/duration/sequence rules are more reproducible as deterministic evaluation over structured events.
- **New conclusion:** VLM may review bounded evidence or draft a narrative with frame citations; it cannot execute the final rule.
- **Uncertainty:** A small locally hosted VLM may be useful for a defined action predicate; measure it against a specialized classifier.

## D-004 - 2026-10-01 - CPU feasibility is subset-specific

- **Previous assumption:** “Edge” might imply the complete AI stack runs on a laptop.
- **New evidence:** SceneSolver notebooks train/use TimeSformer, A100/T4-oriented AE/RL work and optional LLaVA; official deployment runtimes provide CPU/OpenVINO/ONNX paths for smaller detector-style models, but no repository measurement establishes end-to-end laptop capacity.
- **New conclusion:** Benchmark a CPU-first detector/tracker/rule path; treat heavy temporal/VLM stages as selective/offline until measured.
- **Uncertainty:** exact camera capacity depends on CPU, resolution, codec, detector export and scene density.

## D-005 - 2026-10-02 - Use a descriptive architecture name

- **Previous assumption:** The internal C + E comparison shorthand could serve as the final architecture name.
- **New evidence:** C describes hierarchical escalation and E describes trusted sensor integration, while D describes optional VLM review. These are dimensions of one architecture, not a clear product description.
- **New conclusion:** Use **Hierarchical Event Driven Architecture with Sensor Integration and Optional VLM Escalation** as the descriptive name. Preserve A/B/C/D/E as an internal comparison mapping.
- **Uncertainty:** The exact set of retained stages remains measurement-dependent.

## D-006 - 2026-10-02 - Licensing is a first-class gate

- **Previous assumption:** A technically strong open-weight candidate could be selected first and licensed later.
- **New evidence:** Ultralytics documents AGPL-3.0 and Enterprise paths; TimeSformer and VideoMAE repositories identify non-commercial terms; Qwen3-VL and SmolVLM2 publish permissive candidate terms but exact checkpoints and dependencies still require manifests.
- **New conclusion:** Code, weights, model cards, dependencies, commercial use, redistribution, attribution and deployment compatibility must pass before production retention.
- **Uncertainty:** Legal review and exact checkpoint provenance are still open.

## D-007 - 2026-10-02 - Retain stages only through ablation

- **Previous assumption:** Anomaly, VLM and sensor stages should be included because they broaden capability.
- **New evidence:** Added stages also add latency, memory, privacy exposure, failure modes, license obligations and operating cost.
- **New conclusion:** Use the ablation ladder and retain a component only after measurement, incremental value, resource cost, privacy review and reliability approval.
- **Uncertainty:** The incremental value of each stage is unmeasured until the locked replay experiment runs.

## D-008 - 2026-10-02 - Treat sensor integration as a parallel arm

- **Previous assumption:** Sensor integration could be described as the final additive stage after temporal, anomaly and VLM components.
- **New evidence:** A sensor can replace a visual predicate, corroborate it or fail independently. Forcing it into a linear ladder would overstate the target architecture.
- **New conclusion:** Evaluate sensor integration as a parallel branch against Core CV, only where a trusted sensor is available and approved.
- **Uncertainty:** Sensor freshness, join quality, availability, privacy and operational value remain site-specific.

## D-009 - 2026-10-02 - P0 evidence is intentionally bounded

- **Previous assumption:** Feasibility evidence might require implementing the full perception and deployment stack.
- **New evidence:** The rule contract, replay seam and existing SceneSolver artifacts can demonstrate important feasibility claims without customer video, target hardware or external model downloads.
- **New conclusion:** Submit the measured synthetic rule pass, model-neutral replay, specialised CV contract path and repository artifact inspection as P0 evidence. Keep visual accuracy, quantisation, VLM and deployment capacity explicitly pending.
- **Uncertainty:** Site-like replay and one target hardware profile are still required for performance claims.
