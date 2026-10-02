"""Small P0-only evaluator for synthetic feasibility traces.

This is an experiment harness, not a production rule service. It implements only the
operators needed by the checked-in synthetic cases and keeps true, false and unknown
separate. The event shape follows temporal_reasoning/event.schema.json.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def parse_duration(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value)
    units = (("ms", 0.001), ("s", 1.0), ("m", 60.0), ("h", 3600.0), ("d", 86400.0))
    for suffix, factor in units:
        if value.endswith(suffix):
            return float(value[: -len(suffix)]) * factor
    raise ValueError(f"unsupported duration: {value}")


def iso_seconds(value: str) -> float:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return (parsed - BASE_TIME).total_seconds()


def event_bounds(event: Dict[str, Any]) -> Tuple[float, float]:
    time = event["time"]
    start = iso_seconds(time["start"])
    end_value = time.get("end")
    end = iso_seconds(end_value) if end_value else start
    return start, max(start, end)


def event_quality(event: Dict[str, Any]) -> str:
    return event.get("quality", {}).get("status", "unknown")


def event_overlaps(event: Dict[str, Any], start: float, end: float) -> bool:
    event_start, event_end = event_bounds(event)
    return event_start < end and event_end > start


def value_for_arg(event: Dict[str, Any], key: str) -> Any:
    attrs = event.get("attributes", {})
    if key in attrs:
        return attrs[key]
    if key == "camera":
        return event.get("camera_id")
    if key == "camera_id":
        return event.get("camera_id")
    return event.get(key)


def args_match(event: Dict[str, Any], args: Optional[Dict[str, Any]]) -> bool:
    for key, expected in (args or {}).items():
        if isinstance(expected, str) and expected.startswith("$"):
            continue
        if value_for_arg(event, key) != expected:
            return False
    return True


def event_matches(event: Dict[str, Any], expression: Dict[str, Any]) -> bool:
    if "event" not in expression:
        return False
    return event.get("event_type") == expression["event"] and args_match(event, expression.get("args"))


def matching_events(expression: Dict[str, Any], events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if "event" not in expression:
        return []
    return [event for event in events if event_matches(event, expression)]


def health_status(events: List[Dict[str, Any]], start: float, end: float) -> str:
    health = [
        event
        for event in events
        if event.get("event_type") == "camera.health" and event_overlaps(event, start, end)
    ]
    if not health:
        return "unknown"
    if any(event.get("attributes", {}).get("status") != "healthy" for event in health):
        return "unknown"
    return "healthy"


def status_for_predicate(expression: Dict[str, Any], events: List[Dict[str, Any]]) -> str:
    name = expression.get("predicate")
    args = expression.get("args", {})
    candidates = [
        event
        for event in events
        if event.get("event_type") == name and args_match(event, {k: v for k, v in args.items() if k not in {"equals", "value"}})
    ]
    if not candidates:
        return "unknown"
    if any(event_quality(event) in {"unknown", "degraded", "camera_unhealthy"} for event in candidates):
        return "unknown"
    expected = args.get("equals", args.get("value"))
    if expected is None:
        return "true"
    for event in candidates:
        actual = event.get("attributes", {}).get("value")
        if actual is None:
            actual = event.get("attributes", {}).get(name.split(".")[-1])
        if actual == expected:
            return "true"
    return "false"


def _invert(status: str) -> str:
    return {"true": "false", "false": "true", "unknown": "unknown"}[status]


def evaluate(expression: Dict[str, Any], events: List[Dict[str, Any]]) -> str:
    if "all" in expression:
        statuses = [evaluate(item, events) for item in expression["all"]]
        if "false" in statuses:
            return "false"
        if "unknown" in statuses:
            return "unknown"
        return "true"
    if "any" in expression:
        statuses = [evaluate(item, events) for item in expression["any"]]
        if "true" in statuses:
            return "true"
        if "unknown" in statuses:
            return "unknown"
        return "false"
    if "not" in expression:
        return _invert(evaluate(expression["not"], events))
    if "event" in expression:
        matches = matching_events(expression, events)
        if any(event_quality(event) == "observed" for event in matches):
            return "true"
        if any(event_quality(event) in {"unknown", "degraded", "camera_unhealthy"} for event in matches):
            return "unknown"
        return "false"
    if "predicate" in expression:
        status = status_for_predicate(expression, events)
        if expression.get("negate"):
            return _invert(status)
        return status
    if "temporal" in expression:
        temporal = expression["temporal"]
        subject = temporal["subject"]
        needed = parse_duration(temporal.get("duration", "0s"))
        max_gap = parse_duration(temporal.get("max_gap", "0s"))
        candidates = matching_events(subject, events)
        if not candidates:
            return "unknown" if evaluate(subject, events) == "unknown" else "false"
        if any(event_quality(event) in {"unknown", "degraded", "camera_unhealthy"} for event in candidates):
            return "unknown"
        for event in candidates:
            start, end = event_bounds(event)
            if end - start >= needed:
                health = health_status(events, start, end)
                if health == "healthy" or not any(e.get("event_type") == "camera.health" for e in events):
                    return "true"
                return "unknown"
        # A sequence of short observed events can satisfy a duration when gaps are allowed.
        ordered = sorted((event_bounds(event) for event in candidates), key=lambda item: item[0])
        if ordered:
            covered = 0.0
            start = ordered[0][0]
            previous_end = ordered[0][1]
            covered = previous_end - start
            for current_start, current_end in ordered[1:]:
                if current_start - previous_end <= max_gap:
                    covered += max(0.0, current_end - previous_end)
                    previous_end = max(previous_end, current_end)
                else:
                    start, previous_end, covered = current_start, current_end, current_end - current_start
                if covered >= needed:
                    return "true" if health_status(events, start, previous_end) == "healthy" else "unknown"
        return "false"
    if "sequence" in expression:
        sequence = expression["sequence"]
        within = parse_duration(expression.get("within", "365d"))
        lists = [matching_events(item, events) for item in sequence]
        if any(not items for items in lists):
            if any(evaluate(item, events) == "unknown" for item in sequence):
                return "unknown"
            return "false"
        for first in sorted(lists[0], key=lambda event: event_bounds(event)[0]):
            previous_end = event_bounds(first)[1]
            for items in lists[1:]:
                later = [item for item in items if event_bounds(item)[0] >= previous_end]
                if not later:
                    break
                chosen = min(later, key=lambda item: event_bounds(item)[0])
                previous_end = event_bounds(chosen)[1]
            else:
                if previous_end - event_bounds(first)[0] <= within:
                    return "true"
        return "false"
    if "absence" in expression:
        absence = expression["absence"]
        window = absence["window"]
        start = float(window.get("start_s", 0.0))
        end = float(window.get("end_s", start))
        subject = absence["event"]
        matches = [event for event in matching_events(subject, events) if event_overlaps(event, start, end)]
        if any(event_quality(event) == "observed" for event in matches):
            return "false"
        if any(event_quality(event) in {"unknown", "degraded", "camera_unhealthy"} for event in matches):
            return "unknown"
        if absence.get("require_healthy_observation") and health_status(events, start, end) != "healthy":
            return "unknown"
        return "true"
    raise ValueError(f"unsupported expression: {expression}")


def candidate_times(expression: Dict[str, Any], events: List[Dict[str, Any]]) -> List[float]:
    """Return qualifying start times for the small cooldown demonstration."""
    if "temporal" not in expression:
        return []
    temporal = expression["temporal"]
    needed = parse_duration(temporal.get("duration", "0s"))
    result = []
    for event in matching_events(temporal["subject"], events):
        start, end = event_bounds(event)
        if event_quality(event) == "observed" and end - start >= needed:
            result.append(start)
    return sorted(result)


def evaluate_rule(rule: Dict[str, Any], events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluate selected fixture expressions; configured unknown_policy actions are not executed."""
    raw_status = evaluate(rule["when"], events)
    exception_statuses = [evaluate(item, events) for item in rule.get("exceptions", [])]
    suppressed = "true" in exception_statuses
    if suppressed:
        decision = "suppressed_by_exception"
    elif raw_status == "true":
        decision = "confirmed"
    elif raw_status == "unknown":
        decision = "unknown"
    else:
        decision = "not_triggered"
    candidates = candidate_times(rule["when"], events)
    cooldown = parse_duration(rule.get("then", {}).get("cooldown", "0s"))
    emitted = []
    for candidate in candidates:
        if not emitted or candidate - emitted[-1] >= cooldown:
            emitted.append(candidate)
    qualified = emitted if decision == "confirmed" else []
    return {
        "raw_status": raw_status,
        "decision": decision,
        "exception_statuses": exception_statuses,
        "qualifying_interval_start_s": candidates,
        "cooldown_s": cooldown,
        "cooldown_qualified_interval_start_s": qualified,
        "cooldown_qualified_interval_count": len(qualified),
        "online_alert_latency_ms": "not_available",
    }


def validate_event(event: Dict[str, Any]) -> List[str]:
    required = {"event_id", "event_type", "camera_id", "time", "provenance", "quality"}
    errors = [f"missing:{key}" for key in sorted(required - set(event))]
    if "time" in event and not {"start", "end", "clock_domain"}.issubset(event["time"]):
        errors.append("time_missing_required_field")
    if "quality" in event and event["quality"].get("status") not in {"observed", "unknown", "degraded", "camera_unhealthy"}:
        errors.append("quality_status_invalid")
    if "provenance" in event and not {"source_type", "source_id", "model_version"}.issubset(event["provenance"]):
        errors.append("provenance_missing_required_field")
    return errors


def validate_rule(rule: Dict[str, Any]) -> List[str]:
    required = {"id", "version", "when", "then"}
    errors = [f"missing:{key}" for key in sorted(required - set(rule))]
    if "then" in rule and not {"event_type", "action"}.issubset(rule["then"]):
        errors.append("then_missing_required_field")
    return errors
