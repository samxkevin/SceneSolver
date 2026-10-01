# Decision Log

Append entries; do not erase prior assumptions. Dates are UTC.

## D-001 — 2026-10-01 — Separate perception from policy

- **Previous assumption:** A strong anomaly/incident classifier could be the core of generic CCTV compliance.
- **New evidence:** Owner requirements include duration, permissions, zones, ordering, exceptions, absence, cooldowns and cross-camera joins. These are policy/state semantics rather than a single visual class. SceneSolver itself stages evidence and reasoning but its reported task is anomaly/incident analysis.
- **Why it changed:** A classifier label cannot by itself provide deterministic temporal replay, authorization joins or auditable condition satisfaction.
- **New conclusion:** The target contract is typed observations -> temporal state -> deterministic rule evaluation -> evidence. Learned models supply only the observations that cannot be obtained deterministically.
- **Uncertainty:** The minimum model for hard actions such as smoking or required-action completion is still open.

## D-002 — 2026-10-01 — SceneSolver is a baseline/reference, not the target system

- **Previous assumption:** Extend the existing pipeline directly.
- **New evidence:** It contains a staged TimeSformer/AE/YOLO/audio/tracking/fusion/RL/LLaVA/report design and useful data tooling, but the tracked evidence lacks target-site camera-hour metrics, production latency, and generic rule evaluation. Its multi-class result is seven classes while the README also describes 13–14 UCF-Crime categories.
- **Why it changed:** The task has a different target ontology and operational boundary.
- **New conclusion:** Preserve SceneSolver and evaluate selected components behind adapters; build an isolated feasibility prototype first.
- **Uncertainty:** Whether its TimeSformer or AE can add measurable value after the new benchmark is run.

## D-003 — 2026-10-01 — VLM is optional, not authoritative

- **Previous assumption:** LLaVA/VLM should explain and potentially decide the event.
- **New evidence:** VLMs are broad but expensive, probabilistic and difficult to calibrate for exact timestamps and policy semantics. SceneSolver marks its LLaVA stage experimental and uses it for narrative.
- **Why it changed:** Routine zone/duration/sequence rules are more reproducible as deterministic evaluation over structured events.
- **New conclusion:** VLM may review bounded evidence or draft a narrative with frame citations; it cannot execute the final rule.
- **Uncertainty:** A small locally hosted VLM may be useful for a defined action predicate; measure it against a specialized classifier.

## D-004 — 2026-10-01 — CPU feasibility is subset-specific

- **Previous assumption:** “Edge” might imply the complete AI stack runs on a laptop.
- **New evidence:** SceneSolver notebooks train/use TimeSformer, A100/T4-oriented AE/RL work and optional LLaVA; official deployment runtimes provide CPU/OpenVINO/ONNX paths for smaller detector-style models, but no repository measurement establishes end-to-end laptop capacity.
- **New conclusion:** Benchmark a CPU-first detector/tracker/rule path; treat heavy temporal/VLM stages as selective/offline until measured.
- **Uncertainty:** exact camera capacity depends on CPU, resolution, codec, detector export and scene density.
