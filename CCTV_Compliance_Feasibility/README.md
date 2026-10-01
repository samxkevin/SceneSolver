# CCTV Compliance Feasibility Study

**Status:** research baseline and architecture proposal; not a production implementation
**Study date:** 2026-10-01 (UTC)
**Scope:** continuous or near-real-time CCTV event recognition under edge, hybrid, and cloud deployment constraints
**Repository rule:** this directory is isolated exploratory material. Existing SceneSolver code and artifacts are not modified by this study.

## Start here

Read the consolidated [`REPORT.md`](REPORT.md) or begin with the shorter [`architecture/executive-summary.md`](architecture/executive-summary.md). The modular artifacts below preserve the evidence, interfaces and experiment details.

## Why this exists

The objective is not to choose a fashionable model. It is to establish, experimentally and architecturally, the **smallest, simplest system that can reliably satisfy each owner-defined CCTV requirement** while preserving a defensible privacy boundary. The system should make a narrow claim such as “rule R was satisfied between times T1 and T2 on camera C,” not silently turn a generic anomaly score into a compliance decision.

## Current engineering position (provisional)

1. **Architecture C/D is the leading candidate:** lightweight perception, tracking and state estimation feed a typed temporal event stream; a deterministic rule engine evaluates owner policy; evidence and alerts are generated from the same event trace. A VLM is an optional escalation or analyst-assistance component, never the sole compliance authority.
2. **SceneSolver is a useful baseline/reference, not yet a production foundation.** It demonstrates a staged offline forensic workflow and has repository-level metrics, but its main task is UCF-Crime-style anomaly/incident analysis. It does not yet demonstrate generic owner-defined rules, multi-camera identity/authorization, continuous service operation, calibrated alert rates, or target-hardware latency.
3. **CPU-only operation is plausible for a restricted subset:** video decode, motion/ROI logic, small detector, simple tracker, geometry, timers, rule evaluation, and compact evidence capture. It is not established that the full TimeSformer + AE + RL + LLaVA stack is suitable for a normal laptop.
4. **Rules should be configuration, not model classes.** The perception contract must expose observations such as `person`, `gate_state`, `zone_occupancy`, `action_candidate`, and `credential_match`; temporal persistence, ordering, exceptions, permissions and cooldowns belong in deterministic evaluation.
5. **No benchmark number in this study is invented.** Numbers from SceneSolver are labelled as repository evidence and numbers from papers/vendor documentation retain their benchmark conditions. All deployment FPS, latency, power, and alert-quality gates remain experiments.

## Source-of-truth labels

| Label | Meaning |
|---|---|
| `REPO FACT` | Directly observed in tracked SceneSolver files or generated artifacts. |
| `PUBLISHED` | Claimed by a cited paper or official documentation under its stated conditions. |
| `INFERENCE` | Engineering interpretation of facts; useful but not a measurement. |
| `HYPOTHESIS` | A testable proposal, not a conclusion. |
| `OPEN` | Unknown until data, policy, or an experiment resolves it. |

## Deliverables

| Requirement | Artifact |
|---|---|
| Executive summary | [`architecture/executive-summary.md`](architecture/executive-summary.md) |
| Candidate architectures and decision | [`architecture/candidate-architectures.md`](architecture/candidate-architectures.md) |
| Prototype and production target | [`architecture/prototype-and-production.md`](architecture/prototype-and-production.md) |
| AI/CV model matrix | [`models/model-matrix.md`](models/model-matrix.md) |
| Hardware feasibility matrix | [`hardware/feasibility-matrix.md`](hardware/feasibility-matrix.md) |
| Optimisation and quantisation | [`hardware/optimisation.md`](hardware/optimisation.md) |
| Edge/cloud/hybrid and privacy boundary | [`privacy/deployment-and-boundary.md`](privacy/deployment-and-boundary.md) |
| Rule language and examples | [`rule_engine/design.md`](rule_engine/design.md), [`rule_engine/rule.schema.yaml`](rule_engine/rule.schema.yaml) |
| Temporal event model | [`temporal_reasoning/design.md`](temporal_reasoning/design.md), [`temporal_reasoning/event.schema.json`](temporal_reasoning/event.schema.json) |
| Evidence architecture | [`evidence/design.md`](evidence/design.md) |
| SceneSolver analysis | [`baseline/scenesolver-analysis.md`](baseline/scenesolver-analysis.md) |
| Experiment matrix and protocol | [`experiments/experiment-matrix.md`](experiments/experiment-matrix.md), [`experiments/benchmark-config.example.yaml`](experiments/benchmark-config.example.yaml) |
| Failure modes | [`architecture/failure-modes.md`](architecture/failure-modes.md) |
| Privacy/security/compliance review points | [`privacy/governance-checklist.md`](privacy/governance-checklist.md) |
| Sources and conditions | [`research/sources.md`](research/sources.md) |
| Decisions and changed assumptions | [`decisions/decision-log.md`](decisions/decision-log.md) |
| Open questions | [`decisions/open-questions.md`](decisions/open-questions.md) |

## Navigation for the next agent

Read in this order:

1. This file and `architecture/executive-summary.md`.
2. `baseline/scenesolver-analysis.md` before reusing any existing component.
3. `architecture/candidate-architectures.md` and the typed contracts in `rule_engine/` and `temporal_reasoning/`.
4. `experiments/experiment-matrix.md`; do not promote a model based only on the matrix's qualitative assessment.
5. `decisions/decision-log.md` and `decisions/open-questions.md`; append changed assumptions rather than rewriting history.

## Non-goals and cautions

- This is technical feasibility work, not legal advice or a determination that any deployment is lawful.
- “Confidence” is a model score unless calibrated against a labelled operating point; it is not probability of a violation.
- A track ID is a temporary camera-local association, not a person identity.
- Embeddings, cropped frames, appearance features and audio may remain personal or sensitive data; sending less data is not the same as sending anonymous data.
- The word “real time” must be replaced by a measurable alert-latency and camera-concurrency target.
