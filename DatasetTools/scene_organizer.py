#!/usr/bin/env python3
"""
SceneSolver — Scene Organizer
=============================

A safe, deterministic reordering / shuffling utility for SceneSolver scene
folders (Phase 0 -> Phase 2 of the pipeline described in ``Insights.md``).

SceneSolver conventions this tool adapts to (discovered from the repo, not
invented here):

  * A **scene** is one directory whose name is the source video id, e.g.
        outputs/frames/Abuse028_x264/
        results/cctv_analysis_results/frames/
  * Frames inside a scene are written by the extractors as:
        frame_%04d.jpg   (ReportGeneration/VanillaCode/cctv_analysis_script.py)
        frame_%06d.jpg   (UnrefinedCoreFuntionality/ExplorationsInCLIP)
        %06d_%d.jpg      (LLaVa/FireLLaVA_frames -> "<frame>_<variant>")
  * Manifests are JSONL with an ``image`` absolute path (LLaVa/LLaVA_manifests).

The tool NEVER mutates the input tree. It writes an output tree plus a
machine-readable mapping so the operation is fully reversible.

Ordering modes
--------------
  A. ``temporal``       original / correct temporal ordering (default)
  B. ``scene-shuffle``  scenes are shuffled, frames stay in temporal order
  C. ``frame-shuffle``  frames randomized inside each scene (scene grouping
                        still preserved). Opt-in, for ablation studies only.

Usage
-----
    # 1. Dry-run validation only (writes nothing)
    python DatasetTools/scene_organizer.py \
        --input  UnrefinedCoreFuntionality/ExplorationsInCLIP/outputs/frames \
        --dry-run

    # 2. Materialise a temporally-correct copy (hardlinks, cheap)
    python DatasetTools/scene_organizer.py \
        --input  outputs/frames --output build/frames_ordered

    # 3. Deterministic scene-level shuffle for training splits
    python DatasetTools/scene_organizer.py \
        --input outputs/frames --output build/frames_shuffled \
        --mode scene-shuffle --seed 1337

    # 4. Undo anything this tool produced
    python DatasetTools/scene_organizer.py --revert build/frames_shuffled
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

__all__ = [
    "FileRecord",
    "Scene",
    "ValidationReport",
    "natural_key",
    "parse_order_key",
    "discover_scenes",
    "validate",
    "order_scenes",
    "plan",
    "apply_plan",
    "revert",
]

MAPPING_FILENAME = "scene_organizer_mapping.json"
REPORT_FILENAME = "scene_organizer_report.json"

DEFAULT_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".bmp", ".webp",
    ".npy", ".pt", ".json", ".txt",
    ".mp4", ".avi", ".mov", ".mkv",
    ".wav", ".mp3", ".flac",
)

# ---------------------------------------------------------------------------
# Filename -> ordering key
# ---------------------------------------------------------------------------

_NUM_RE = re.compile(r"\d+")

# frame_0007.jpg / frame-7.jpg / frame7.jpg / img_000123.png
_FRAME_RE = re.compile(
    r"(?:^|[^a-z0-9])(?:frame|frm|f|img|image|idx|seq)[ _\-\.]?(\d+)",
    re.IGNORECASE,
)
# 000123_0.jpg  -> (123, 0)   the LLaVA FireLLaVA_frames convention
_FRAME_VARIANT_RE = re.compile(r"^(\d+)_(\d+)$")
# 00:01:23.456 / 00-01-23 / t1234ms
_TIMESTAMP_RE = re.compile(r"(\d{1,2})[:\-h](\d{2})[:\-m](\d{2})(?:[.,](\d{1,6}))?")
_MS_RE = re.compile(r"(?:^|[^a-z0-9])t(?:ime)?[ _\-]?(\d+)ms", re.IGNORECASE)


def natural_key(name: str) -> Tuple:
    """Human/natural sort key: ``frame_2`` < ``frame_10``.

    Splits the string into alternating text and integer runs so numbers are
    compared numerically instead of lexicographically.
    """
    parts = _NUM_RE.split(name)
    nums = _NUM_RE.findall(name)
    key: List = []
    for i, text in enumerate(parts):
        key.append((0, text.lower()))
        if i < len(nums):
            key.append((1, int(nums[i])))
    return tuple(key)


@dataclass(frozen=True)
class OrderKey:
    """How confidently, and by what evidence, a file was ordered."""

    primary: float           # main sort value (frame no. or seconds)
    secondary: int           # tie-breaker (e.g. LLaVA variant index)
    source: str              # 'frame_number' | 'timestamp' | 'trailing_number'
                             # | 'natural' (low confidence)
    confident: bool


def parse_order_key(filename: str) -> OrderKey:
    """Derive a temporal ordering key from a single filename.

    Explicit numeric / temporal evidence is always preferred over
    lexicographic sorting. Returns ``confident=False`` when the only thing we
    could do was a natural-sort fallback, so the caller can warn about it.
    """
    stem = Path(filename).stem

    # 1. explicit "<frame>_<variant>" (LLaVA FireLLaVA_frames)
    m = _FRAME_VARIANT_RE.match(stem)
    if m:
        return OrderKey(float(int(m.group(1))), int(m.group(2)), "frame_number", True)

    # 2. explicit frame/index token
    m = _FRAME_RE.search(stem)
    if m:
        rest = stem[m.end():]
        tail = _NUM_RE.search(rest)
        return OrderKey(
            float(int(m.group(1))),
            int(tail.group(0)) if tail else 0,
            "frame_number",
            True,
        )

    # 3. milliseconds token
    m = _MS_RE.search(stem)
    if m:
        return OrderKey(int(m.group(1)) / 1000.0, 0, "timestamp", True)

    # 4. hh:mm:ss[.frac] timestamp
    m = _TIMESTAMP_RE.search(stem)
    if m:
        h, mi, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
        frac = m.group(4)
        secs = h * 3600 + mi * 60 + s
        if frac:
            secs += int(frac) / (10 ** len(frac))
        return OrderKey(float(secs), 0, "timestamp", True)

    # 5. a bare / trailing number is still explicit numeric evidence
    nums = _NUM_RE.findall(stem)
    if nums:
        return OrderKey(float(int(nums[-1])), 0, "trailing_number", True)

    # 6. nothing numeric -> ambiguous, fall back to natural sort
    return OrderKey(float("inf"), 0, "natural", False)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class FileRecord:
    scene: str
    rel_path: str            # path relative to the input root
    filename: str
    order_key: OrderKey
    size: int = 0
    digest: str = ""         # lazily filled, only when duplicate checking
    index: int = -1          # position assigned inside the scene (0-based)
    new_rel_path: str = ""

    @property
    def confident(self) -> bool:
        return self.order_key.confident


@dataclass
class Scene:
    name: str
    files: List[FileRecord] = field(default_factory=list)


@dataclass
class ValidationReport:
    total_scenes: int = 0
    total_files: int = 0
    files_reordered: int = 0
    files_unchanged: int = 0
    duplicate_filenames: List[Dict] = field(default_factory=list)
    duplicate_contents: List[Dict] = field(default_factory=list)
    missing_sequence: List[Dict] = field(default_factory=list)
    inconsistent_scene: List[Dict] = field(default_factory=list)
    ambiguous_files: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    mode: str = "temporal"
    seed: Optional[int] = None

    def as_dict(self) -> Dict:
        d = asdict(self)
        d["generated_at"] = datetime.now(timezone.utc).isoformat()
        return d

    def to_text(self) -> str:
        L = [
            "=" * 62,
            " SceneSolver — Scene Organizer validation summary",
            "=" * 62,
            f" mode                 : {self.mode}",
            f" seed                 : {self.seed if self.seed is not None else '-'}",
            f" total scenes         : {self.total_scenes}",
            f" total files          : {self.total_files}",
            f" files reordered      : {self.files_reordered}",
            f" files unchanged      : {self.files_unchanged}",
            f" duplicate filenames  : {len(self.duplicate_filenames)}",
            f" duplicate contents   : {len(self.duplicate_contents)}",
            f" missing seq. numbers : {len(self.missing_sequence)}",
            f" inconsistent scenes  : {len(self.inconsistent_scene)}",
            f" ambiguous files      : {len(self.ambiguous_files)}",
            f" warnings             : {len(self.warnings)}",
            "-" * 62,
        ]
        for d in self.duplicate_filenames[:10]:
            L.append(f" [DUP-NAME] scene={d['scene']} name={d['filename']} x{d['count']}")
        for d in self.duplicate_contents[:10]:
            L.append(f" [DUP-DATA] {d['digest'][:12]} -> {', '.join(d['paths'][:3])}")
        for d in self.missing_sequence[:10]:
            miss = d["missing"]
            shown = ", ".join(str(x) for x in miss[:8])
            more = f" (+{len(miss) - 8} more)" if len(miss) > 8 else ""
            L.append(f" [GAP]      scene={d['scene']} missing={shown}{more}")
        for d in self.inconsistent_scene[:10]:
            L.append(f" [SCENE?]   {d['rel_path']}: dir={d['dir_scene']} name={d['name_scene']}")
        for p in self.ambiguous_files[:10]:
            L.append(f" [AMBIG]    {p}")
        for w in self.warnings[:20]:
            L.append(f" [WARN]     {w}")
        L.append("=" * 62)
        return "\n".join(L)

    @property
    def ok(self) -> bool:
        return not (
            self.duplicate_filenames
            or self.duplicate_contents
            or self.inconsistent_scene
        )


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def _scene_hint_from_name(filename: str) -> Optional[str]:
    """Extract a scene id embedded in a filename, e.g.
    ``Abuse028_x264_frame_0003.jpg`` -> ``Abuse028_x264``."""
    stem = Path(filename).stem
    m = _FRAME_RE.search(stem)
    if not m or m.start() == 0:
        return None
    hint = stem[: m.start()].strip("_-. ")
    return hint or None


def discover_scenes(
    input_root: Path,
    extensions: Sequence[str] = DEFAULT_EXTENSIONS,
    recursive: bool = True,
) -> List[Scene]:
    """Walk ``input_root`` and group files into scenes.

    Scene identity rule (matches the existing SceneSolver layout):
      * if ``input_root`` directly contains files, they form one scene named
        after ``input_root`` (the ``.../frames/frame_0000.jpg`` case);
      * otherwise every immediate sub-directory is a scene and keeps its own
        internal sub-structure in ``rel_path`` (the ``frames/<video_id>/`` case).
    """
    input_root = Path(input_root)
    if not input_root.is_dir():
        raise NotADirectoryError(f"input root not found: {input_root}")

    exts = {e.lower() for e in extensions} if extensions else None

    def keep(p: Path) -> bool:
        if not p.is_file() or p.name.startswith("."):
            return False
        if p.name in (MAPPING_FILENAME, REPORT_FILENAME):
            return False
        return exts is None or p.suffix.lower() in exts

    scenes: Dict[str, Scene] = {}

    def add(scene_name: str, path: Path) -> None:
        rel = path.relative_to(input_root).as_posix()
        rec = FileRecord(
            scene=scene_name,
            rel_path=rel,
            filename=path.name,
            order_key=parse_order_key(path.name),
            size=path.stat().st_size,
        )
        scenes.setdefault(scene_name, Scene(scene_name)).files.append(rec)

    loose = [p for p in sorted(input_root.iterdir()) if keep(p)]
    for p in loose:
        add(input_root.name, p)

    for sub in sorted(p for p in input_root.iterdir() if p.is_dir()):
        if sub.name.startswith("."):
            continue
        it = sub.rglob("*") if recursive else sub.iterdir()
        for p in sorted(it):
            if keep(p):
                add(sub.name, p)

    return [scenes[k] for k in sorted(scenes)]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _digest(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def validate(
    scenes: Sequence[Scene],
    input_root: Path,
    check_contents: bool = True,
    gap_tolerance: float = 0.35,
) -> ValidationReport:
    """Run every pre-flight check. Nothing is written and nothing is dropped."""
    rep = ValidationReport()
    rep.total_scenes = len(scenes)
    rep.total_files = sum(len(s.files) for s in scenes)

    by_digest: Dict[str, List[str]] = {}

    for scene in scenes:
        # --- duplicate basenames inside a scene -------------------------
        seen: Dict[str, List[str]] = {}
        for f in scene.files:
            seen.setdefault(f.filename, []).append(f.rel_path)
        for name, paths in seen.items():
            if len(paths) > 1:
                rep.duplicate_filenames.append(
                    {"scene": scene.name, "filename": name,
                     "count": len(paths), "paths": paths}
                )

        # --- ambiguous ordering & scene consistency ---------------------
        for f in scene.files:
            if not f.confident:
                rep.ambiguous_files.append(f.rel_path)
            hint = _scene_hint_from_name(f.filename)
            if hint and hint != scene.name and scene.name not in hint and hint not in scene.name:
                rep.inconsistent_scene.append(
                    {"rel_path": f.rel_path, "dir_scene": scene.name, "name_scene": hint}
                )

        # --- missing sequence numbers -----------------------------------
        nums = sorted(
            {int(f.order_key.primary) for f in scene.files
             if f.order_key.source in ("frame_number", "trailing_number")}
        )
        if len(nums) >= 3:
            lo, hi = nums[0], nums[-1]
            span = hi - lo + 1
            step = _dominant_step(nums)
            expected = set(range(lo, hi + 1, step))
            missing = sorted(expected - set(nums))
            if missing and len(missing) <= gap_tolerance * len(expected):
                rep.missing_sequence.append(
                    {"scene": scene.name, "step": step, "range": [lo, hi],
                     "missing": missing, "count": len(missing)}
                )
            elif missing:
                rep.warnings.append(
                    f"scene '{scene.name}': sequence too sparse to infer continuity "
                    f"({len(nums)} files across span {span}); gaps not reported"
                )

        # --- duplicate content ------------------------------------------
        if check_contents:
            for f in scene.files:
                f.digest = _digest(Path(input_root) / f.rel_path)
                by_digest.setdefault(f.digest, []).append(f.rel_path)

        if not scene.files:
            rep.warnings.append(f"scene '{scene.name}' contains no eligible files")

    for dig, paths in by_digest.items():
        if len(paths) > 1:
            rep.duplicate_contents.append({"digest": dig, "paths": sorted(paths)})

    if rep.ambiguous_files:
        rep.warnings.append(
            f"{len(rep.ambiguous_files)} file(s) had no numeric/temporal evidence; "
            "they were placed last within their scene using natural sort and are "
            "reported, never dropped"
        )
    return rep


def _dominant_step(nums: Sequence[int]) -> int:
    """Most common positive delta between consecutive sequence numbers.

    Extractors sample every N-th frame, so the 'expected' step is not always 1.
    """
    deltas: Dict[int, int] = {}
    for a, b in zip(nums, nums[1:]):
        d = b - a
        if d > 0:
            deltas[d] = deltas.get(d, 0) + 1
    if not deltas:
        return 1
    best = max(deltas.items(), key=lambda kv: (kv[1], -kv[0]))
    return best[0]


# ---------------------------------------------------------------------------
# Ordering
# ---------------------------------------------------------------------------

MODES = ("temporal", "scene-shuffle", "frame-shuffle")


def order_scenes(
    scenes: Sequence[Scene],
    mode: str = "temporal",
    seed: Optional[int] = None,
) -> List[Scene]:
    """Return scenes with files ordered according to ``mode``.

    ``temporal``      : files sorted by their temporal key (A).
    ``scene-shuffle`` : scene *order* shuffled, files still temporal (B).
    ``frame-shuffle`` : files shuffled inside each scene (C). Scene grouping
                        is still absolute — no file ever crosses scenes.
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    if mode != "temporal" and seed is None:
        raise ValueError("a --seed is required for reproducible shuffling")

    out: List[Scene] = []
    for sc in scenes:
        files = sorted(
            sc.files,
            key=lambda f: (
                not f.confident,                 # confident files first
                f.order_key.primary,
                f.order_key.secondary,
                natural_key(f.rel_path),
            ),
        )
        if mode == "frame-shuffle":
            # Per-scene RNG stream => adding/removing a scene cannot change
            # the permutation of any other scene.
            rng = random.Random(f"{seed}:{sc.name}")
            rng.shuffle(files)
        for i, f in enumerate(files):
            f.index = i
        out.append(Scene(sc.name, files))

    # deterministic, name-independent-of-insertion-order scene ordering
    out.sort(key=lambda s: natural_key(s.name))
    if mode == "scene-shuffle":
        random.Random(f"{seed}:scenes").shuffle(out)
    return out


# ---------------------------------------------------------------------------
# Planning / applying
# ---------------------------------------------------------------------------


def plan(
    scenes: Sequence[Scene],
    rename: bool = False,
    pad: int = 6,
) -> List[FileRecord]:
    """Fill ``new_rel_path`` on every record and return the flat plan.

    By default filenames are **preserved verbatim** (requirement 1) and the
    ordering is carried by the mapping/manifest. ``rename=True`` additionally
    emits a zero-padded ``<index>__<original name>`` prefix for consumers that
    can only do lexicographic directory listing; the original name is still
    fully embedded, so no metadata is lost and the rename is invertible.
    """
    records: List[FileRecord] = []
    for si, sc in enumerate(scenes):
        for f in sc.files:
            sub = Path(f.rel_path)
            # keep any sub-structure below the scene dir
            tail = Path(*sub.parts[1:]) if len(sub.parts) > 1 else Path(sub.name)
            name = tail.name
            if rename:
                name = f"{f.index:0{pad}d}__{name}"
            f.new_rel_path = (Path(sc.name) / tail.parent / name).as_posix()
            records.append(f)
    return records


def apply_plan(
    records: Sequence[FileRecord],
    scenes: Sequence[Scene],
    input_root: Path,
    output_root: Path,
    report: ValidationReport,
    link: str = "hardlink",
    overwrite: bool = False,
) -> Dict:
    """Materialise the plan into ``output_root`` and write the mapping.

    ``link`` is one of ``hardlink`` (default, cheap and non-destructive),
    ``symlink`` or ``copy``. The input tree is only ever read.
    """
    input_root = Path(input_root).resolve()
    output_root = Path(output_root).resolve()
    if output_root == input_root or input_root in output_root.parents:
        raise ValueError("output directory must be outside the input tree")
    if output_root.exists() and any(output_root.iterdir()) and not overwrite:
        raise FileExistsError(
            f"{output_root} is not empty; pass --overwrite to replace it"
        )
    if output_root.exists() and overwrite:
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    for f in records:
        src = input_root / f.rel_path
        dst = output_root / f.new_rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            dst.unlink()
        if link == "hardlink":
            try:
                os.link(src, dst)
            except OSError:
                shutil.copy2(src, dst)
        elif link == "symlink":
            os.symlink(src, dst)
        else:
            shutil.copy2(src, dst)

    mapping = {
        "tool": "SceneSolver/DatasetTools/scene_organizer.py",
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_root": str(input_root),
        "output_root": str(output_root),
        "mode": report.mode,
        "seed": report.seed,
        "link": link,
        "scene_order": [s.name for s in scenes],
        "entries": [
            {
                "scene": f.scene,
                "index": f.index,
                "original_path": f.rel_path,
                "new_path": f.new_rel_path,
                "order_source": f.order_key.source,
                "order_value": (
                    None if f.order_key.primary == float("inf") else f.order_key.primary
                ),
                "confident": f.confident,
                "size": f.size,
                "sha256": f.digest or None,
            }
            for f in records
        ],
    }
    (output_root / MAPPING_FILENAME).write_text(json.dumps(mapping, indent=2))
    (output_root / REPORT_FILENAME).write_text(json.dumps(report.as_dict(), indent=2))

    # Per-scene ordered manifest — this is what the downstream frame-extraction
    # / temporal-segmentation code should read instead of os.listdir().
    for sc in scenes:
        lines = [
            json.dumps({
                "scene": f.scene,
                "index": f.index,
                "path": f.new_rel_path,
                "original_path": f.rel_path,
            })
            for f in sc.files
        ]
        (output_root / sc.name / "order.jsonl").write_text("\n".join(lines) + "\n")

    return mapping


def revert(output_root: Path, delete: bool = False) -> Dict:
    """Reverse a previous run.

    Because the input tree was never touched, reverting is simply verifying the
    mapping against the still-intact source and (optionally) removing the
    generated tree. Returns the verification result.
    """
    output_root = Path(output_root)
    mapping_path = output_root / MAPPING_FILENAME
    if not mapping_path.is_file():
        raise FileNotFoundError(f"no {MAPPING_FILENAME} in {output_root}")
    mapping = json.loads(mapping_path.read_text())
    src_root = Path(mapping["input_root"])

    missing = [e["original_path"] for e in mapping["entries"]
               if not (src_root / e["original_path"]).exists()]
    result = {
        "input_root": str(src_root),
        "output_root": str(output_root),
        "entries": len(mapping["entries"]),
        "originals_missing": missing,
        "restorable": not missing,
        "deleted_output": False,
    }
    if not missing and delete:
        shutil.rmtree(output_root)
        result["deleted_output"] = True
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="scene_organizer",
        description="SceneSolver scene reordering / deterministic shuffling utility.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Usage\n-----")[-1],
    )
    p.add_argument("--input", "-i", type=Path, help="root containing scene folders")
    p.add_argument("--output", "-o", type=Path, help="output directory (must be empty)")
    p.add_argument("--mode", "-m", default="temporal", choices=MODES,
                   help="A temporal (default) | B scene-shuffle | C frame-shuffle")
    p.add_argument("--seed", type=int, default=None,
                   help="RNG seed; required for any shuffle mode")
    p.add_argument("--link", default="hardlink", choices=("hardlink", "symlink", "copy"))
    p.add_argument("--rename", action="store_true",
                   help="prefix outputs with the zero-padded order index "
                        "(original filename is kept in full)")
    p.add_argument("--pad", type=int, default=6, help="index padding for --rename")
    p.add_argument("--ext", nargs="*", default=None,
                   help="file extensions to include (default: common media/data)")
    p.add_argument("--no-hash", action="store_true",
                   help="skip content hashing (faster, no duplicate-content check)")
    p.add_argument("--dry-run", action="store_true", help="validate and report only")
    p.add_argument("--strict", action="store_true",
                   help="exit non-zero if validation found blocking problems")
    p.add_argument("--json", action="store_true", help="print the report as JSON")
    p.add_argument("--overwrite", action="store_true", help="replace a non-empty output dir")
    p.add_argument("--revert", type=Path, metavar="OUTPUT_DIR",
                   help="verify and undo a previous run")
    p.add_argument("--delete", action="store_true",
                   help="with --revert, also remove the generated output tree")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.revert:
        res = revert(args.revert, delete=args.delete)
        print(json.dumps(res, indent=2))
        return 0 if res["restorable"] else 1

    if not args.input:
        build_parser().error("--input is required (or use --revert)")
    if args.mode != "temporal" and args.seed is None:
        build_parser().error(f"--seed is required for --mode {args.mode}")
    if not args.dry_run and not args.output:
        build_parser().error("--output is required unless --dry-run is given")

    exts = tuple(
        e if e.startswith(".") else "." + e for e in args.ext
    ) if args.ext else DEFAULT_EXTENSIONS

    scenes = discover_scenes(args.input, extensions=exts)
    rep = validate(scenes, args.input, check_contents=not args.no_hash)
    rep.mode, rep.seed = args.mode, args.seed

    ordered = order_scenes(scenes, mode=args.mode, seed=args.seed)
    records = plan(ordered, rename=args.rename, pad=args.pad)

    original = {}
    for sc in scenes:
        for i, f in enumerate(sorted(sc.files, key=lambda x: natural_key(x.rel_path))):
            original[f.rel_path] = i
    rep.files_reordered = sum(1 for f in records if original.get(f.rel_path) != f.index)
    rep.files_unchanged = len(records) - rep.files_reordered

    if args.json:
        print(json.dumps(rep.as_dict(), indent=2))
    else:
        print(rep.to_text())

    if args.strict and not rep.ok:
        print("strict mode: blocking validation problems found, nothing written.",
              file=sys.stderr)
        return 2

    if args.dry_run:
        print("(dry run — nothing written)")
        return 0

    apply_plan(records, ordered, args.input, args.output, rep,
               link=args.link, overwrite=args.overwrite)
    print(f"wrote {len(records)} entries to {args.output}")
    print(f"mapping: {Path(args.output) / MAPPING_FILENAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
