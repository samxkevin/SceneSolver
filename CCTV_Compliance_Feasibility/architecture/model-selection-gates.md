# Model Selection Gates

A candidate model is promoted only when it passes all applicable gates; no one metric is sufficient.

## Gate 1 — task fit

- Does the model output the observation the rule actually requires?
- Is the output frame-, interval-, track- or scene-level at the needed temporal resolution?
- Are negatives and ambiguity represented rather than forced into a class?

## Gate 2 — data fit

- Is there target-site labelled data with hard negatives and condition coverage?
- Are train/calibration/test splits leakage-controlled by camera/session/person/time?
- Are annotation agreement and boundary uncertainty recorded?

## Gate 3 — reliability fit

- Does the candidate meet owner-set rule-event recall and false-alert budget?
- Is calibration stable across cameras/conditions?
- Are unknowns and data gaps surfaced?

## Gate 4 — systems fit

- Does it meet p95 alert latency and camera concurrency on target hardware?
- Is peak memory within budget, including decoder/tracker/evidence?
- Does it remain stable after a thermal soak and under network/storage failure?

## Gate 5 — privacy/security fit

- Can inference stay local or use a documented minimal export?
- Does the model introduce face/appearance/audio/embedding risk not necessary for the rule?
- Are model license, supply chain, update and rollback controls acceptable?

## Gate 6 — operations fit

- Can operators diagnose why an alert fired?
- Can thresholds/config/model versions be rolled back?
- Can rule replay and evidence retrieval reproduce the result?

If a model fails only because the requirement is underspecified, resolve the requirement rather than adding a larger model.
