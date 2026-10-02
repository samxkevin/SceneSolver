# P0 Evidence Package

**Scope:** smallest evidence pass for the feasibility study. This is not a production service, frontend, multi-camera platform or model-training project.

## What was run

| Artifact | Command | Result |
|---|---|---|
| Rule engine | `python run_rule_tests.py` | 11 checked synthetic fixtures passed, 2 malformed-input fixtures passed, deterministic replay checks passed |
| Replay contract | `python replay_harness.py` | structured frame replay passed through decode adapter, sampling, observation, event, temporal state, rule and evidence stages; final dwell interval is open at stream end |
| Specialised CV reference | `python specialised_cv_reference.py` | precomputed-detection adapter passed detector seam, single-track trajectory, zone dwell and rule path |
| SceneSolver baseline | `python scenesolver_baseline_inspection.py` | existing report artifact inspected; no retraining or inference performed |
| Quantisation | not run | exact model, runtime and target hardware unavailable |
| VLM review | not run | no lightweight model was readily available; advisory architecture remains documented |

## Files

- `rule_engine_cases.json`: compact synthetic fixtures adapted into the existing temporal event schema.
- `rule_engine_results.json`: machine-readable expected versus actual rule decisions, true/false/unknown behavior, replay checks and validation failures.
- `replay_input.json`: small structured frame manifest for the contract replay.
- `replay_harness.py`: model-neutral replay adapter.
- `replay_results.json`: stage counts, stage timing, decision and bounded evidence hash.
- `specialised_cv_reference.py`: deliberately small precomputed-detection reference path.
- `specialised_cv_results.json`: trajectory and dwell result with limitations.
- `scenesolver_baseline_inspection.py`: repository artifact and prerequisite inspection.
- `scenesolver_baseline_results.json`: measured repository evidence and reasons full inference was not run.
- `p0_common.py`: limited evaluator used only by the checked-in synthetic fixtures.

## Interpretation boundary

The rule and replay results demonstrate selected implementation conformance and deterministic contract behavior on synthetic inputs. The specialised CV result demonstrates separation of detection output, tracking/trajectory state and deterministic policy logic. The replay's open interval records observed duration up to stream end and does not fabricate an exit. They do not establish visual accuracy, customer-site generalisation, camera capacity, deployment throughput, power, memory envelope or legal compliance.

The evaluator is intentionally incomplete. It does not establish continuous health coverage across an entire temporal interval, unknown propagation in every sequence case, complete unknown handling for missing simple events, alert candidate extraction for every nested expression or complete JSON Schema validation. It also does not execute the configured `unknown_policy` actions (`suppress`, `delay`, `escalate_review`, `treat_as_false`). These are P0 limitations, not production-engine implementation goals.

The SceneSolver result is repository evidence plus artifact inspection. It is not a new SceneSolver accuracy result. Existing SceneSolver production and research directories were not modified.

## Re-run

Run from the repository root:

```bash
python CCTV-Compliance-Feasibility/experiments/p0/run_rule_tests.py
python CCTV-Compliance-Feasibility/experiments/p0/replay_harness.py
python CCTV-Compliance-Feasibility/experiments/p0/specialised_cv_reference.py
python CCTV-Compliance-Feasibility/experiments/p0/scenesolver_baseline_inspection.py
```

The scripts use only the Python standard library. Wall-time values are measurements of this small synthetic contract harness or artifact inspection. They are not CCTV inference latency, camera throughput, deployment FPS or real-time system performance.
