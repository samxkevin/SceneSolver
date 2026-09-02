"""
SceneSolver — ordered scene loading helpers.

Thin, dependency-free helpers meant to replace ad-hoc ``os.listdir`` /
``sorted()`` calls in the frame-extraction and temporal-segmentation code
(``ReportGeneration/VanillaCode/cctv_analysis_script.py``,
``UnrefinedCoreFuntionality/EnhancedTemporalTraining.py``, ``Orchestrator.ipynb``).

    from DatasetTools.scene_loader import ordered_frames, iter_scenes

    for path in ordered_frames("outputs/frames/Abuse028_x264"):
        ...   # guaranteed frame_1, frame_2, ..., frame_10 order
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

from .scene_organizer import (
    DEFAULT_EXTENSIONS,
    MAPPING_FILENAME,
    natural_key,
    parse_order_key,
)

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def ordered_frames(
    scene_dir: str | Path,
    extensions: Sequence[str] = IMAGE_EXTS,
) -> List[Path]:
    """Return the frames of one scene in correct temporal order.

    Prefers an ``order.jsonl`` written by ``scene_organizer`` if present,
    otherwise derives the order from the filenames themselves.
    """
    scene_dir = Path(scene_dir)
    manifest = scene_dir / "order.jsonl"
    if manifest.is_file():
        out: List[Path] = []
        for line in manifest.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                out.append(scene_dir.parent / rec["path"])
        return out

    exts = {e.lower() for e in extensions}
    files = [p for p in scene_dir.iterdir()
             if p.is_file() and p.suffix.lower() in exts and not p.name.startswith(".")]
    return sorted(
        files,
        key=lambda p: (
            not parse_order_key(p.name).confident,
            parse_order_key(p.name).primary,
            parse_order_key(p.name).secondary,
            natural_key(p.name),
        ),
    )


def iter_scenes(
    root: str | Path,
    extensions: Sequence[str] = IMAGE_EXTS,
) -> Iterator[Tuple[str, List[Path]]]:
    """Yield ``(scene_name, ordered_frame_paths)`` for every scene under root.

    Respects the scene order recorded by ``scene_organizer`` when a mapping
    file is present (so a shuffled split replays identically).
    """
    root = Path(root)
    mapping = root / MAPPING_FILENAME
    if mapping.is_file():
        names = json.loads(mapping.read_text())["scene_order"]
    else:
        names = sorted((p.name for p in root.iterdir() if p.is_dir()), key=natural_key)
    for name in names:
        d = root / name
        if d.is_dir():
            yield name, ordered_frames(d, extensions)


def load_mapping(output_root: str | Path) -> Dict:
    """Load the original -> new path mapping produced by a previous run."""
    return json.loads((Path(output_root) / MAPPING_FILENAME).read_text())


def original_path_for(output_root: str | Path, new_rel_path: str) -> Optional[str]:
    """Reverse lookup: new path -> original path (reversibility helper)."""
    for e in load_mapping(output_root)["entries"]:
        if e["new_path"] == new_rel_path:
            return e["original_path"]
    return None
