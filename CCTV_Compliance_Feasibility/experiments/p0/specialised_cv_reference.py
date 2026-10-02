#!/usr/bin/env python3
"""Minimal specialised-CV contract reference using precomputed synthetic detections.

This is deliberately not a detector implementation. It demonstrates the adapter seam:
detector output -> single-track association -> zone interval -> deterministic rule.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "replay_input.json"
OUTPUT = ROOT / "specialised_cv_results.json"


def center(bbox):
    return ((bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0)


def main() -> int:
    started = time.perf_counter()
    raw = json.loads(INPUT.read_text(encoding="utf-8"))
    zone = raw["zone"]
    stage_ms = {}

    t = time.perf_counter()
    # Adapter input represents the output of a detector. No learned detector runs here.
    detections = []
    for frame in raw["frames"]:
        for detection in frame.get("detections", []):
            x, y = center(detection["bbox"])
            detections.append({
                "frame_id": frame["frame_id"],
                "timestamp_s": frame["timestamp_s"],
                "class": detection["class"],
                "track_hint": detection["track_hint"],
                "bbox": detection["bbox"],
                "inside_zone": zone["x_min"] <= x <= zone["x_max"] and zone["y_min"] <= y <= zone["y_max"],
            })
    stage_ms["detector_adapter"] = round((time.perf_counter() - t) * 1000, 3)

    t = time.perf_counter()
    tracks = {}
    for detection in detections:
        track = tracks.setdefault(detection["track_hint"], {"track_id": detection["track_hint"], "observations": []})
        track["observations"].append(detection)
    stage_ms["tracker"] = round((time.perf_counter() - t) * 1000, 3)

    t = time.perf_counter()
    trajectories = []
    stream_end = raw["frames"][-1]["timestamp_s"]
    for track_id, track in tracks.items():
        ordered = sorted(track["observations"], key=lambda item: item["timestamp_s"])
        inside = [item for item in ordered if item["inside_zone"]]
        if inside:
            start_s = inside[0]["timestamp_s"]
            exit_candidate = next((item["timestamp_s"] for item in ordered if item["timestamp_s"] > start_s and not item["inside_zone"]), None)
            exit_observed = exit_candidate is not None and exit_candidate < stream_end
            observed_end = exit_candidate if exit_observed else stream_end
            trajectories.append({
                "track_id": track_id,
                "zone": zone["id"],
                "observed_start_s": start_s,
                "observed_end_s": observed_end,
                "observed_duration_s": observed_end - start_s,
                "interval_status": "complete" if exit_observed else "open",
                "exit_observed": exit_observed,
                "end_reason": "observed_exit" if exit_observed else "stream_end",
            })
    stage_ms["trajectory_zone_state"] = round((time.perf_counter() - t) * 1000, 3)

    t = time.perf_counter()
    threshold_s = 3.0
    decisions = [{"track_id": item["track_id"], "rule_id": "p0_zone_dwell", "decision": "confirmed" if item["observed_duration_s"] >= threshold_s else "not_triggered", "observed_duration_s": item["observed_duration_s"], "threshold_s": threshold_s, "interval_status": item["interval_status"]} for item in trajectories]
    stage_ms["deterministic_rule"] = round((time.perf_counter() - t) * 1000, 3)

    output = {
        "artifact": "P0 specialised CV reference path",
        "status": "measured_contract_path",
        "path": ["detector_adapter", "tracker", "trajectory_zone_state", "deterministic_rule"],
        "detector": {"implementation": "precomputed synthetic detection adapter", "learned_model_run": False, "accuracy": "not_available"},
        "stage_wall_time_ms": stage_ms,
        "total_wall_time_ms": round((time.perf_counter() - started) * 1000, 3),
        "inputs": {"frames": len(raw["frames"]), "detections": len(detections), "camera_id": raw["camera_id"]},
        "outputs": {"tracks": len(tracks), "trajectories": trajectories, "decisions": decisions},
        "memory_mb": "not_available; psutil and model runtime were not used",
        "limitations": [
            "No pretrained detector or video decoder was available in the execution environment.",
            "Synthetic bounding boxes and track hints demonstrate the interface only.",
            "The final frame leaves the trajectory interval open; observed duration is not presented as a completed exit.",
            "The result establishes architecture path execution, not visual accuracy or production performance.",
        ],
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "tracks": len(tracks), "decisions": decisions, "total_wall_time_ms": output["total_wall_time_ms"]}, indent=2))
    return 0 if all(item["decision"] == "confirmed" for item in decisions) else 1


if __name__ == "__main__":
    sys.exit(main())
