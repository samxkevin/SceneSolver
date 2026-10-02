#!/usr/bin/env python3
"""Inspect reproducible SceneSolver artifacts without retraining or inference."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ARTIFACT = REPO / "ReportGeneration/InferenceResults/results/cctv_analysis_results/analysis.json"
FRAMES = ARTIFACT.parent / "frames"
OUTPUT = Path(__file__).resolve().parent / "scenesolver_baseline_results.json"


def dependency_status(names):
    return {name: bool(importlib.util.find_spec(name)) for name in names}


def main() -> int:
    started = time.perf_counter()
    artifact_bytes = ARTIFACT.stat().st_size if ARTIFACT.exists() else None
    parsed = json.loads(ARTIFACT.read_text(encoding="utf-8")) if ARTIFACT.exists() else None
    parse_ms = round((time.perf_counter() - started) * 1000, 3)

    frame_files = sorted(FRAMES.glob("*.jpg")) if FRAMES.exists() else []
    referenced_paths = [item.get("path") for item in (parsed or {}).get("anomalies", []) if item.get("path")]
    missing_referenced_paths = sum(1 for value in referenced_paths if value and not Path(value).exists())

    relevant_files = []
    external_drive_refs = []
    pretrained_calls = []
    for path in REPO.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "CCTV_Compliance_Feasibility" in path.parts:
            continue
        if path.suffix not in {".py", ".ipynb", ".md", ".json", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "/content/drive" in text or "MyDrive" in text:
            external_drive_refs.append(str(path.relative_to(REPO)))
        if "from_pretrained" in text or "torch.load" in text or ".pth" in text or ".pt" in text:
            relevant_files.append(str(path.relative_to(REPO)))
        if "from_pretrained" in text:
            pretrained_calls.append(str(path.relative_to(REPO)))

    checkpoint_paths = []
    for suffix in ("*.pt", "*.pth", "*.onnx", "*.ckpt"):
        checkpoint_paths.extend(str(path.relative_to(REPO)) for path in REPO.rglob(suffix) if "CCTV_Compliance_Feasibility" not in path.parts)

    dependencies = dependency_status(["torch", "cv2", "numpy", "ultralytics", "psutil", "jupyter"])
    artifact_hash = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest() if ARTIFACT.exists() else None
    output = {
        "artifact": "P0 SceneSolver baseline evidence inspection",
        "status": "measured_repository_artifact",
        "measurement_scope": "existing committed report artifact and repository prerequisite inspection; no retraining or inference",
        "source_artifact": str(ARTIFACT.relative_to(REPO)),
        "artifact_sha256": artifact_hash,
        "artifact_size_bytes": artifact_bytes,
        "artifact_inspection_parse_ms": parse_ms,
        "repository_output": {
            "metadata": (parsed or {}).get("metadata"),
            "summary": (parsed or {}).get("summary"),
            "anomaly_records": len((parsed or {}).get("anomalies", [])),
            "packaged_frame_files": len(frame_files),
            "referenced_frame_paths": len(referenced_paths),
            "referenced_frame_paths_missing_on_filesystem": missing_referenced_paths,
            "output_types": ["analysis.json", "JPEG evidence frame paths", "summary"],
        },
        "measured": {
            "artifact_parse": True,
            "artifact_inspection_runtime_ms": parse_ms,
            "frames_processed_by_original_run": (parsed or {}).get("metadata", {}).get("frame_count"),
            "report_generation_time_ms": "not_available in committed artifact",
            "stage_timing_ms": "not_available in committed artifact",
            "model_inference_runtime_ms": "not_available; no reproducible inference run performed",
            "memory_mb": "not_available",
            "vram_mb": "not_available",
        },
        "prerequisites": {
            "python_modules": dependencies,
            "checkpoint_paths_found_outside_study": checkpoint_paths,
            "files_with_external_drive_or_pretrained_references": sorted(set(external_drive_refs + pretrained_calls))[:80],
            "source_video_found_in_repository": any(path.suffix.lower() in {".mp4", ".avi", ".mkv", ".mov"} for path in REPO.rglob("*") if "CCTV_Compliance_Feasibility" not in path.parts),
        },
        "failure_conditions": [
            "The report artifact references Google Drive frame paths that are not present at those absolute paths in this checkout.",
            "The original source video is not present in the checkout, so the report-generation run cannot be replayed from its input.",
            "The checkout does not provide the torch/cv2/ultralytics stack needed for the relevant inference paths.",
            "The available checkpoint inventory does not establish a runnable TimeSformer or YOLO inference configuration.",
            "The notebook-based pipeline uses external data/checkpoint paths and is not a deterministic command-line run.",
        ],
        "conclusion": "Repository evidence and artifact inspection are measured; SceneSolver model runtime, stage latency, memory, and target deployment capacity remain unmeasured.",
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "anomaly_records": output["repository_output"]["anomaly_records"], "frames_processed_by_original_run": output["measured"]["frames_processed_by_original_run"], "parse_ms": parse_ms, "full_inference": "not_run"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
