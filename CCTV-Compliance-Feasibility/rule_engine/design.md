# Owner-Configurable Rule Engine

## Core contract

Perception never emits `violation` directly. It emits observations with source, time bounds, entities, attributes, confidence/quality and provenance. The rule engine evaluates a versioned policy over observations and produces a decision with the conditions that were satisfied.

```text
observation stream + reference data + rule version
    -> temporal state / joins
    -> typed predicate evaluation
    -> violation candidate or no-decision
```

Use three-valued logic where appropriate:

- `true`: evidence satisfies the predicate;
- `false`: evidence contradicts it;
- `unknown`: input missing, stale, occluded, camera unhealthy or identity unresolved.

`unknown` must not silently become `false` or `unauthorized`. Rule authors choose whether unknown suppresses, delays, escalates or creates an “unable to verify” workflow.

## Predicate vocabulary

### Entity and attribute predicates

`entity.type`, `entity.track_id`, `entity.attributes`, `object.class`, `pose.state`, `ocr.token`, `sensor.value`, `authorization.role`, `authorization.status`, `observation.quality`.

### Spatial predicates

`inside(entity, zone)`, `crossed(entity, line, direction)`, `distance(entity, object)`, `overlap(object, zone)`. Zone configuration is versioned with camera calibration.

### Temporal operators

- `for >= duration`: state must persist for a duration, with an allowed gap policy.
- `within duration`: related events must occur in a bounded interval.
- `before` / `after`: ordered events; define whether equality is allowed.
- `sequence`: finite state transitions, optionally with overlap or reset.
- `until`: condition remains active until a terminating event.
- `absence`: expected event did not occur by a deadline, only if the observation window is known healthy.
- `count`: cardinality over an interval, with entity distinctness explicitly declared.
- `cooldown`: suppress repeated alerts after a decision for a duration.
- `debounce`: require persistence or multiple observations before a transition.

### Policy predicates

`role_in`, `credential_valid_at`, `schedule_active`, `exception_match`, `camera_scope`, `confidence_at_least`, `quality_at_least`, and human-review requirements.

## Natural-language authoring

A natural-language interface is useful only as a **drafting assistant**:

1. Parse the owner's description into candidate objects, zones, events, duration, schedule, exceptions and action.
2. Ask for missing semantics: “does 30 seconds allow a 2-second occlusion?”, “what does unauthorized mean?”, “does one badge event authorize one person or a zone?”
3. Resolve names against a controlled ontology and camera registry; do not invent detector classes.
4. Emit schema-validated DSL/YAML plus a human-readable preview.
5. Run static checks: unsupported predicate, contradictory time window, missing zone/calibration, identity ambiguity, absence rule without camera health, dangerous action without human approval.
6. Owner approves a signed rule version; only that version is executable.
7. Test against synthetic traces and labelled replay before activation.

The LLM may propose a rule. It must not execute free text or bypass validation.

## Examples

### Restricted-zone dwell with authorization

```yaml
id: restricted_counter_access
version: 1
scope: {cameras: [counter-01]}
when:
  all:
    - event: person.entered_zone
      args: {zone: counter_zone}
      bind: {subject: person}
    - predicate: authorization.status
      args: {subject: "$subject", equals: authorized}
      negate: true
    - temporal:
        operator: for_at_least
        subject: {event: person.inside_zone, args: {zone: counter_zone, person: "$subject"}}
        duration: 10s
        max_gap: 2s
then:
  event_type: compliance.violation
  severity: high
  action: [local_alert, human_review]
  cooldown: 5m
```

### Gate left open, with a sensor preferred

```yaml
id: gate_left_open
version: 1
scope: {cameras: [gate-01]}
when:
  all:
    - any:
        - event: sensor.gate_state
          args: {gate: gate_a, state: open}
        - event: vision.gate_state
          args: {gate: gate_a, state: open}
    - temporal:
        operator: for_at_least
        subject: {state: gate_a.open}
        duration: 20s
        max_gap: 1s
    - predicate: camera.health
      args: {camera: gate-01, equals: healthy}
then:
  event_type: gate.open_too_long
  severity: medium
  action: [local_alert, evidence_capture]
```

### Required action completed before deadline

```yaml
id: closeout_not_completed
version: 1
when:
  sequence:
    - event: task.started
      bind: {task_id: task}
    - event: person.assigned
      args: {task_id: "$task", role: operator}
    - event: task.deadline_reached
      args: {task_id: "$task"}
    - absence:
        event: task.completed
        args: {task_id: "$task"}
        window: {start: "$task.started", end: "$task.deadline_reached"}
        require_healthy_observation: true
then:
  event_type: task.incomplete
  severity: high
  action: [human_review]
```

## Multi-entity and cross-camera semantics

Each variable binding has a scope: `same_track`, `same_camera`, `same_person_token`, `same_object`, or `any`. A camera-local track must not be silently joined to a different camera. Cross-camera joins require an explicit signal (badge token, access event, time/route constraint or approved appearance matching) and must carry `join_quality` and privacy classification.

## Rule evaluation and alert lifecycle

```text
candidate -> pending/debounce -> confirmed -> alerted -> acknowledged
                                      \-> expired/retracted
```

A retraction must not delete the original decision; it appends a correction with reason and operator/model provenance. Cooldowns suppress duplicate alerts but preserve supporting observations.

## Static and runtime safeguards

- schema validation and allow-listed operators;
- no arbitrary code in a rule;
- limits on window length, cardinality and cross-camera fan-out;
- explicit `unknown` handling;
- minimum evidence quality and camera-health preconditions;
- policy version, timezone and DST behavior recorded;
- dry-run/shadow mode before activation;
- rule change review and rollback;
- per-rule metrics: candidate count, confirmed count, review outcome, FP/FN estimates, unknown rate.
