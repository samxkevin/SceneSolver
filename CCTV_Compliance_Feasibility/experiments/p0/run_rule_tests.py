#!/usr/bin/env python3
"""Run the compact P0 rule fixtures and write rule_engine_results.json."""
from __future__ import annotations

import json
import sys
import time
from datetime import timedelta
from pathlib import Path

from p0_common import BASE_TIME, evaluate_rule, validate_event, validate_rule

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "rule_engine_cases.json"
OUTPUT = ROOT / "rule_engine_results.json"


def to_iso(seconds: float) -> str:
    return (BASE_TIME + timedelta(seconds=float(seconds))).isoformat().replace("+00:00", "Z")


def normalize_event(spec: dict, index: int) -> dict:
    if "time" in spec:
        return spec
    return {
        "event_id": spec["event_id"],
        "event_type": spec["event_type"],
        "camera_id": spec.get("camera_id", "cam-p0"),
        "time": {
            "start": to_iso(spec.get("start_s", 0)),
            "end": to_iso(spec.get("end_s", spec.get("start_s", 0))),
            "clock_domain": "monotonic-derived",
            "complete": True,
        },
        "attributes": spec.get("attributes", {}),
        "quality": {"status": spec.get("quality", "observed")},
        "provenance": {
            "source_type": spec.get("source_type", "detector"),
            "source_id": spec.get("source_id", "p0-synthetic"),
            "model_version": spec.get("model_version"),
        },
    }


def main() -> int:
    started = time.perf_counter()
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    results = []
    all_passed = True

    for case in source["cases"]:
        events = [normalize_event(item, index) for index, item in enumerate(case["events"])]
        event_errors = [error for event in events for error in validate_event(event)]
        rule_errors = validate_rule(case["rule"])
        actual_first = evaluate_rule(case["rule"], events) if not event_errors and not rule_errors else None
        actual_second = evaluate_rule(case["rule"], events) if not event_errors and not rule_errors else None
        checks = {
            "schema_adapter_valid": not event_errors and not rule_errors,
            "expected_decision": actual_first is not None and actual_first["decision"] == case["expected_decision"],
            "expected_raw_status": actual_first is not None and actual_first["raw_status"] == case["expected_raw_status"],
            "deterministic_replay": actual_first == actual_second,
        }
        if "expected_cooldown_qualified_interval_count" in case:
            checks["expected_cooldown_qualified_interval_count"] = actual_first is not None and actual_first["cooldown_qualified_interval_count"] == case["expected_cooldown_qualified_interval_count"]
        passed = all(checks.values())
        all_passed = all_passed and passed
        results.append({
            "id": case["id"],
            "status": "passed" if passed else "failed",
            "expected": {key: case[key] for key in ("expected_decision", "expected_raw_status", "expected_cooldown_qualified_interval_count") if key in case},
            "actual": actual_first,
            "checks": checks,
            "event_count": len(events),
            "validation_errors": event_errors + rule_errors,
        })

    failure_results = []
    for fixture in source["failure_fixtures"]:
        if "event" in fixture:
            errors = validate_event(fixture["event"])
        else:
            errors = validate_rule(fixture["rule"])
        passed = fixture["expected_error"] in errors
        all_passed = all_passed and passed
        failure_results.append({
            "id": fixture["id"],
            "status": "passed" if passed else "failed",
            "expected_error": fixture["expected_error"],
            "actual_errors": errors,
        })

    output = {
        "artifact": "P0 rule engine validation",
        "status": "measured_pass" if all_passed else "measured_failure",
        "implementation_scope": "synthetic evaluator for checked-in fixtures; not production rule service",
        "input": str(INPUT.relative_to(ROOT.parent.parent.parent)),
        "event_contract": "temporal_reasoning/event.schema.json via compact fixture adapter",
        "rule_contract": "rule_engine/rule.schema.yaml required fields and allow-listed P0 operators",
        "test_count": len(results),
        "failure_fixture_count": len(failure_results),
        "passed_count": sum(item["status"] == "passed" for item in results),
        "failure_fixture_passed_count": sum(item["status"] == "passed" for item in failure_results),
        "wall_time_ms": round((time.perf_counter() - started) * 1000, 3),
        "tests": results,
        "failure_fixtures": failure_results,
        "limitations": [
            "Synthetic traces only; no customer/site data.",
            "The evaluator intentionally implements only operators exercised by these fixtures.",
            "Configured unknown_policy actions (suppress, delay, escalate_review, treat_as_false) are not executed by this P0 evaluator.",
            "No perception accuracy, camera capacity or deployment SLO is inferred.",
        ],
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "tests": len(results), "wall_time_ms": output["wall_time_ms"]}, indent=2))
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
