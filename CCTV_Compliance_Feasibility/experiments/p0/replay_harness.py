#!/usr/bin/env python3
"""Lightweight model-neutral P0 replay harness.

It uses structured synthetic frames instead of a video decoder. The observation
records are precomputed detections, so this measures the contract and deterministic
state/rule/evidence flow, not visual detector accuracy or video throughput.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import timedelta
from pathlib import Path

from p0_common import BASE_TIME, evaluate_rule, validate_event, validate_rule

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "replay_input.json"
OUTPUT = ROOT / "replay_results.json"


def iso(seconds: float) -> str:
    return (BASE_TIME + timedelta(seconds=float(seconds))).isoformat().replace("+00:00", "Z")


def make_event(event_id: str, event_type: str, start: float, end: float, attributes: dict, source_type: str = "rule", complete: bool = True) -> dict:
    return {
        "event_id": event_id,
        "event_type": event_type,
        "camera_id": "cam-p0",
        "time": {"start": iso(start), "end": iso(end), "clock_domain": "monotonic-derived", "complete": complete},
        "attributes": attributes,
        "quality": {"status": "observed", "track_quality": 1.0},
        "provenance": {"source_type": source_type, "source_id": "p0-replay", "model_version": None},
        "privacy": {"classification": "metadata", "egress_allowed": False},
    }


def center(bbox):
    return ((bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0)


def main() -> int:
    overall_start = time.perf_counter()
    raw = json.loads(INPUT.read_text(encoding="utf-8"))
    stage_ms = {}

    t = time.perf_counter()
    frames = raw["frames"]
    stage_ms["decode"] = round((time.perf_counter() - t) * 1000, 3)

    t = time.perf_counter()
    step = int(raw.get("sample_every_n_frames", 1))
    sampled = frames[::step]
    stage_ms["sampling"] = round((time.perf_counter() - t) * 1000, 3)

    t = time.perf_counter()
    zone = raw["zone"]
    observations = []
    for frame in sampled:
        for detection in frame.get("detections", []):
            x, y = center(detection["bbox"])
            inside = zone["x_min"] <= x <= zone["x_max"] and zone["y_min"] <= y <= zone["y_max"]
            observations.append({
                "frame_id": frame["frame_id"],
                "timestamp_s": frame["timestamp_s"],
                "track_hint": detection["track_hint"],
                "class": detection["class"],
                "bbox": detection["bbox"],
                "inside_zone": inside,
            })
    stage_ms["observation"] = round((time.perf_counter() - t) * 1000, 3)

    t = time.perf_counter()
    stream_end = raw["frames"][-1]["timestamp_s"]
    inside = [item for item in observations if item["inside_zone"] and item["track_hint"] == "p1"]
    entered = inside[0]["timestamp_s"] if inside else None
    exit_candidate = next((item["timestamp_s"] for item in observations if item["timestamp_s"] > (entered or -1) and not item["inside_zone"]), None)
    exit_observed = exit_candidate is not None and exit_candidate < stream_end
    observed_end = exit_candidate if exit_observed else stream_end
    interval_status = "complete" if exit_observed else "open"
    if entered is not None:
        interval_attributes = {
            "zone": zone["id"],
            "subject": "p1",
            "interval_status": interval_status,
            "observed_duration_s": observed_end - entered,
            "exit_observed": exit_observed,
            "end_reason": "observed_exit" if exit_observed else "stream_end",
        }
        events = [
            make_event("r-entry-p1", "person.entered_zone", entered, entered, {"zone": zone["id"], "subject": "p1"}, "tracker"),
            make_event("r-inside-p1", "person.inside_zone", entered, observed_end, interval_attributes, "tracker", complete=exit_observed),
            make_event("r-health", "camera.health", 0.0, stream_end, {"status": raw["camera_health"]}, "sensor"),
        ]
    else:
        events = [make_event("r-health", "camera.health", 0.0, stream_end, {"status": raw["camera_health"]}, "sensor")]
    stage_ms["event"] = round((time.perf_counter() - t) * 1000, 3)

    t = time.perf_counter()
    temporal_state = {
        "tracks": [{"track_id": "p1", "observed_frames": len(observations), "inside_zone": bool(inside)}],
        "intervals": [{
            "event_id": "r-inside-p1",
            "start_s": entered,
            "observed_end_s": observed_end,
            "observed_duration_s": observed_end - entered,
            "status": interval_status,
            "exit_observed": exit_observed,
            "end_reason": "observed_exit" if exit_observed else "stream_end",
        }] if entered is not None else [],
    }
    stage_ms["temporal_state"] = round((time.perf_counter() - t) * 1000, 3)

    t = time.perf_counter()
    schema_errors = [error for event in events for error in validate_event(event)]
    schema_errors.extend(validate_rule(raw["rule"]))
    decision = evaluate_rule(raw["rule"], events) if not schema_errors else None
    stage_ms["rule"] = round((time.perf_counter() - t) * 1000, 3)

    t = time.perf_counter()
    evidence = None
    if decision and decision["decision"] == "confirmed":
        evidence_body = {
            "camera_id": raw["camera_id"],
            "rule_id": raw["rule"]["id"],
            "event_ids": [event["event_id"] for event in events if event["event_type"] != "camera.health"],
            "source_frame_ids": [frame["frame_id"] for frame in sampled],
            "privacy": "metadata_only",
            "interval_status": interval_status,
            "observed_duration_s": observed_end - entered if entered is not None else None,
            "exit_observed": exit_observed,
            "evidence_scope": "up_to_stream_end" if not exit_observed else "through_observed_exit",
        }
        digest = hashlib.sha256(json.dumps(evidence_body, sort_keys=True).encode()).hexdigest()
        evidence = {"manifest": evidence_body, "sha256": digest, "bounded": True}
    stage_ms["evidence"] = round((time.perf_counter() - t) * 1000, 3)

    output = {
        "artifact": "P0 model-neutral replay harness",
        "status": "measured_contract_replay" if decision and decision["decision"] == "confirmed" and not schema_errors else "measured_failure",
        "input_type": "structured_frame_replay",
        "video_decode": "not_available; structured frames substituted",
        "pipeline": ["decode", "sampling", "observation", "event", "temporal_state", "rule", "evidence"],
        "stage_wall_time_ms": stage_ms,
        "total_wall_time_ms": round((time.perf_counter() - overall_start) * 1000, 3),
        "stream": {"camera_id": raw["camera_id"], "source_fps": raw["source_fps"], "frames_decoded": len(frames), "frames_processed": len(sampled), "frames_skipped": len(frames) - len(sampled), "frames_dropped": 0},
        "outputs": {"observations": len(observations), "events": len(events), "event_trace": events, "temporal_state": temporal_state, "temporal_tracks": len(temporal_state["tracks"]), "rule_decision": decision, "evidence": evidence},
        "semantic_checks": {
            "interval_is_open_when_stream_ends_inside": interval_status == "open" and not exit_observed,
            "exit_event_fabricated": any(event["event_type"] == "person.exited_zone" for event in events),
            "observed_duration_distinguished_from_completed_interval": interval_status == "open" and evidence is not None and evidence["manifest"]["evidence_scope"] == "up_to_stream_end",
        },
        "schema_errors": schema_errors,
        "limitations": [
            "No video decoder or visual detector was run; input detections are synthetic precomputed observations.",
            "The tracker is a single-track adapter using track_hint, not a MOT evaluation.",
            "The final frame leaves the interval open: observed duration reaches stream end and no exit event is fabricated.",
            "Runtime values measure this synthetic contract replay only and are not CCTV inference latency, camera throughput, deployment FPS or real-time system performance.",
        ],
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "frames_processed": len(sampled), "rule_decision": decision["decision"] if decision else None, "total_wall_time_ms": output["total_wall_time_ms"]}, indent=2))
    return 0 if output["status"] == "measured_contract_replay" else 1


if __name__ == "__main__":
    sys.exit(main())
