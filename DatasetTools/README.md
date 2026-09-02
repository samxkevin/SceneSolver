# DatasetTools — SceneSolver scene organization

Safe, deterministic reordering / shuffling for SceneSolver scene folders.
Sits in front of **Phase 2 (Frame Extraction)** and **Phase 3 (CLIP keyframe
selection)** of the pipeline in [`../Insights.md`](../Insights.md), so
TimeSformer never receives a temporally scrambled sequence.

## Live demo

The SceneSolver analysis pipeline that DatasetTools feeds is published as a
Hugging Face Space — this is the live/demo interface for the project:

**<https://huggingface.co/spaces/samxkevin/SceneSolver>**

DatasetTools prepares and validates the scene/frame data that the Space's
pipeline (AutoEncoder → TimeSformer → YOLO → fusion → LLaVA) consumes.

```
DatasetTools/
├── __init__.py
├── scene_organizer.py     # the CLI + library (validate / order / shuffle / revert)
├── scene_loader.py        # ordered_frames() / iter_scenes() for downstream code
└── tests/
    └── test_scene_organizer.py
```

No third-party dependencies (stdlib only). `pytest` is needed for the tests.

---

## Why

The repo already writes frames with several conventions:

| Producer | Pattern |
|---|---|
| `ReportGeneration/VanillaCode/cctv_analysis_script.py` | `frame_%04d.jpg` |
| `UnrefinedCoreFuntionality/ExplorationsInCLIP` | `frame_%06d.jpg` |
| `LLaVa/LLaVA_manifests` (`FireLLaVA_frames`) | `%06d_%d.jpg` (`<frame>_<variant>`) |

A scene is **one directory named after the source video id**
(`outputs/frames/Abuse028_x264/`). None of that is changed here — the tool
reads the existing layout and never invents a new format.

The failure mode this removes: plain `sorted()` / `os.listdir()` gives
`frame_1, frame_10, frame_2`. This tool parses the number and orders `1, 2, 10`.

---

## Ordering modes

| Mode | Scene order | Frame order inside scene | Use for |
|---|---|---|---|
| `temporal` (default) | natural, stable | **true temporal order** | inference, frame extraction, TimeSformer input |
| `scene-shuffle` | seeded shuffle | **true temporal order** | building train/val splits |
| `frame-shuffle` | natural, stable | seeded shuffle | ablations / frame-level classifiers only |

In **every** mode a file stays inside its own scene directory. Scene grouping
is structural, not a sort key, so it cannot be broken by shuffling.

Each scene gets its own RNG stream (`seed:<scene_name>`), so adding or removing
one scene never perturbs the permutation of the others.

---

## Ordering evidence (highest precedence first)

1. `<frame>_<variant>` — e.g. `000123_1.jpg` → `(123, 1)`
2. explicit token — `frame_7`, `frame-7`, `frame7`, `img_0007`, `seq_7`, `idx7`
3. milliseconds — `t2500ms` → `2.5 s`
4. timestamp — `00:01:30` / `00-01-30.500` → seconds
5. trailing bare number
6. **fallback:** natural sort — flagged `confident=False`, reported as
   *ambiguous*, sorted last within the scene, **never dropped**

---

## Usage

```bash
# 1. Validate only — writes nothing
python DatasetTools/scene_organizer.py \
    -i UnrefinedCoreFuntionality/ExplorationsInCLIP/outputs/frames --dry-run

# 2. Materialise a temporally-correct copy (hardlinks: near-zero disk cost)
python DatasetTools/scene_organizer.py \
    -i outputs/frames -o build/frames_ordered

# 3. Deterministic scene-level shuffle for a training split
python DatasetTools/scene_organizer.py \
    -i outputs/frames -o build/frames_train \
    -m scene-shuffle --seed 1337

# 4. Frame-level randomization (ablation only), with index-prefixed names
python DatasetTools/scene_organizer.py \
    -i outputs/frames -o build/frames_ablation \
    -m frame-shuffle --seed 1337 --rename

# 5. Refuse to write if validation found blocking problems
python DatasetTools/scene_organizer.py -i outputs/frames -o build/out --strict

# 6. Machine-readable report (CI)
python DatasetTools/scene_organizer.py -i outputs/frames --dry-run --json

# 7. Undo anything the tool produced
python DatasetTools/scene_organizer.py --revert build/frames_train --delete
```

### Key flags

| Flag | Meaning |
|---|---|
| `-m/--mode` | `temporal` \| `scene-shuffle` \| `frame-shuffle` |
| `--seed` | required for either shuffle mode; same seed ⇒ identical output |
| `--link` | `hardlink` (default) \| `symlink` \| `copy` |
| `--rename` | prefix `%06d__` order index; original name kept in full |
| `--ext` | restrict extensions, e.g. `--ext jpg png` |
| `--no-hash` | skip SHA-256 duplicate-content check (faster) |
| `--strict` | exit `2` on duplicates / inconsistent scenes |
| `--dry-run` | validate and report only |
| `--revert DIR` | verify the mapping against the intact source, optionally delete |

---

## Sample report

```
==============================================================
 SceneSolver — Scene Organizer validation summary
==============================================================
 mode                 : temporal
 seed                 : -
 total scenes         : 1
 total files          : 1412
 files reordered      : 0
 files unchanged      : 1412
 duplicate filenames  : 0
 duplicate contents   : 2
 missing seq. numbers : 0
 inconsistent scenes  : 0
 ambiguous files      : 0
 warnings             : 0
--------------------------------------------------------------
 [DUP-DATA] 7803302b0800 -> Abuse028_x264/frame_001160.jpg, Abuse028_x264/frame_001162.jpg
 [DUP-DATA] 9c2ec7082fc0 -> Abuse028_x264/frame_001220.jpg, Abuse028_x264/frame_001222.jpg
==============================================================
(dry run — nothing written)
```

---

## Output layout

```
build/frames_train/
├── scene_organizer_mapping.json   # original_path -> new_path, index, sha256
├── scene_organizer_report.json    # the validation summary, machine-readable
└── Abuse028_x264/
    ├── order.jsonl                # authoritative per-scene ordering
    ├── frame_000001.jpg
    └── ...
```

`order.jsonl` (one JSON object per line):

```json
{"scene": "Abuse028_x264", "index": 0, "path": "Abuse028_x264/frame_000001.jpg", "original_path": "Abuse028_x264/frame_000001.jpg"}
```

---

## Safety guarantees

* The input tree is opened **read-only**; output must live outside it (enforced).
* Writing to a non-empty output dir requires `--overwrite`.
* Default `hardlink` means no data is duplicated and no bytes are rewritten.
* Every file appears in the mapping — nothing is silently discarded.
* `--revert` verifies each original still exists before removing the copy.
* Filenames are preserved verbatim unless `--rename` is given, and `--rename`
  embeds the full original name (`000003__frame_10.jpg`), so it is invertible.

---

## Downstream integration

Replace ad-hoc listing in the frame-extraction / temporal code:

```python
# before
frames = sorted(os.listdir(frames_dir))          # frame_1, frame_10, frame_2

# after
from DatasetTools.scene_loader import ordered_frames, iter_scenes

frames = ordered_frames(frames_dir)              # frame_1, frame_2, frame_10

for scene_name, frame_paths in iter_scenes("build/frames_train"):
    clip = frame_paths[:CONFIG["NUM_FRAMES"]]    # temporally contiguous
```

`ordered_frames` uses `order.jsonl` when present and falls back to parsing the
filenames otherwise, so it is a drop-in for both organized and raw trees.
`iter_scenes` replays the recorded `scene_order`, so a seeded split is
reproduced exactly on every epoch/run.

---

## Tests

```bash
python -m pytest DatasetTools/tests -q     # 30 passed
```

Coverage: numeric ordering, multi-digit / mixed padding, multiple scenes, flat
single-scene dirs, deterministic scene & frame shuffling, seed requirement,
duplicate name & content detection, missing-sequence detection (with sampled
step awareness), ambiguous filenames, inconsistent scene assignment, scene
boundary preservation, input immutability, mapping completeness,
reversibility, `--rename` invertibility, end-to-end reproducibility, and CLI.

---

## License

Released under the MIT License. See [`../LICENSE`](../LICENSE) at the
repository root.
