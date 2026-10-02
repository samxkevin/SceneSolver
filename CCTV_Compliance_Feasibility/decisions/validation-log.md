# Validation Log

## 2026-10-01

- `git diff --check`: passed after removing trailing whitespace from study artifacts.
- JSON parse: passed for `temporal_reasoning/event.schema.json`, `experiments/test-trace-format.json`.
- YAML parse: passed with the repository's existing `WebApp/Breakthrough 2/node_modules/js-yaml` for `rule_engine/rule.schema.yaml` and `experiments/benchmark-config.example.yaml`.
- Existing `DatasetTools` pytest suite: not run successfully because `pytest` is not installed in the execution environment (`/usr/bin/python: No module named pytest`). No existing source files were changed to work around this.
- Model/hardware runtime benchmarks: intentionally not run. The repository does not contain the target CCTV streams, external checkpoints or a declared target hardware matrix; the experiment plan records the missing inputs rather than fabricating numbers.

## 2026-10-02 refinement checks

- Relative Markdown links: passed for all study Markdown files.
- JSON/YAML parse: passed for all study `.json` and `.yaml` files with the repository's existing `js-yaml` dependency.
- `git diff --cached --check`: passed after staging the dedicated study folder.
- Trailing whitespace: removed and rechecked with no remaining lines.
- Em dash and en dash scan: passed with zero remaining U+2014 or U+2013 characters in the study folder.
- External research links: official model and licensing pages were checked during research lookup; the sandbox's direct `curl` path does not provide reliable HTTP results for all external hosts, so URL reachability is not treated as proof of source validity.
- Deployment benchmarks, camera capacity, power and cost: intentionally not run because target streams, exact checkpoints, target hardware, region and owner thresholds remain open.
- P0 rule fixtures: passed 11/11 semantic cases and 2/2 expected validation failures with deterministic replay checks.
- P0 structured replay: passed with 13 input frames, 7 sampled frames, 3 typed events, 1 track and a bounded evidence hash.
- P0 specialised CV contract path: passed with 13 precomputed detections, 1 track and a 5.0 second dwell against a 3.0 second rule threshold; no learned detector ran.
- P0 SceneSolver inspection: parsed the committed artifact, recorded 3366 source frames and 44 anomaly records, and did not run inference.

## Interpretation

The study artifacts are syntactically checked where tooling was available. Syntax validation does not validate rule semantics, model accuracy, privacy compliance or production readiness. Those require the experiments and organisational reviews described in the report.
