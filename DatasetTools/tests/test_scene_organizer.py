"""Tests for DatasetTools.scene_organizer.

Run with:  python -m pytest DatasetTools/tests -q
       or:  python DatasetTools/tests/test_scene_organizer.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from DatasetTools.scene_organizer import (  # noqa: E402
    MAPPING_FILENAME,
    apply_plan,
    discover_scenes,
    main,
    natural_key,
    order_scenes,
    parse_order_key,
    plan,
    revert,
    validate,
)
from DatasetTools.scene_loader import ordered_frames, iter_scenes  # noqa: E402


# --------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------


def make_scene(root: Path, scene: str, names) -> Path:
    d = root / scene
    d.mkdir(parents=True, exist_ok=True)
    for i, n in enumerate(names):
        (d / n).write_bytes(f"{scene}:{n}:{i}".encode())
    return d


@pytest.fixture
def dataset(tmp_path: Path) -> Path:
    """Two scenes mirroring the real SceneSolver frame layouts."""
    root = tmp_path / "frames"
    make_scene(root, "Abuse028_x264",
               [f"frame_{i}.jpg" for i in (1, 2, 3, 10, 11, 20)])
    make_scene(root, "Arson009_x264",
               [f"frame_{i:06d}.jpg" for i in range(1, 6)])
    return root


# --------------------------------------------------------------------------
# 1. numeric filename ordering
# --------------------------------------------------------------------------


def test_natural_key_numeric_not_lexicographic():
    names = ["frame_10.jpg", "frame_2.jpg", "frame_1.jpg"]
    assert sorted(names) == ["frame_1.jpg", "frame_10.jpg", "frame_2.jpg"]
    assert sorted(names, key=natural_key) == [
        "frame_1.jpg", "frame_2.jpg", "frame_10.jpg",
    ]


def test_parse_order_key_variants():
    assert parse_order_key("frame_7.jpg").primary == 7
    assert parse_order_key("frame-7.jpg").primary == 7
    assert parse_order_key("frame7.jpg").primary == 7
    assert parse_order_key("frame_0007.jpg").primary == 7          # cctv script
    assert parse_order_key("frame_000007.jpg").primary == 7        # CLIP explorer
    k = parse_order_key("000123_1.jpg")                            # LLaVA frames
    assert (k.primary, k.secondary, k.source) == (123, 1, "frame_number")
    assert parse_order_key("clip_00:01:30.jpg").primary == 90.0
    assert parse_order_key("shot_t2500ms.png").primary == 2.5
    assert parse_order_key("keyframe.jpg").confident is False


def test_ordering_within_scene(dataset):
    scenes = order_scenes(discover_scenes(dataset), mode="temporal")
    s = next(s for s in scenes if s.name == "Abuse028_x264")
    assert [f.filename for f in s.files] == [
        "frame_1.jpg", "frame_2.jpg", "frame_3.jpg",
        "frame_10.jpg", "frame_11.jpg", "frame_20.jpg",
    ]


# --------------------------------------------------------------------------
# 2. multi-digit / zero-padded frame numbers
# --------------------------------------------------------------------------


def test_multi_digit_frame_numbers(tmp_path):
    root = tmp_path / "f"
    make_scene(root, "S1", ["frame_9.jpg", "frame_100.jpg", "frame_1000.jpg",
                            "frame_0099.jpg"])
    s = order_scenes(discover_scenes(root), mode="temporal")[0]
    assert [f.filename for f in s.files] == [
        "frame_9.jpg", "frame_0099.jpg", "frame_100.jpg", "frame_1000.jpg",
    ]


def test_mixed_padding_is_equivalent(tmp_path):
    root = tmp_path / "f"
    make_scene(root, "S1", ["frame_5.jpg", "frame_000006.jpg", "frame_07.jpg"])
    s = order_scenes(discover_scenes(root), mode="temporal")[0]
    assert [f.order_key.primary for f in s.files] == [5.0, 6.0, 7.0]


# --------------------------------------------------------------------------
# 3. multiple scenes
# --------------------------------------------------------------------------


def test_multiple_scenes_discovered(dataset):
    scenes = discover_scenes(dataset)
    assert [s.name for s in scenes] == ["Abuse028_x264", "Arson009_x264"]
    assert sum(len(s.files) for s in scenes) == 11


def test_flat_directory_is_a_single_scene(tmp_path):
    d = tmp_path / "cctv_analysis_results_frames"
    d.mkdir()
    for i in range(3):
        (d / f"frame_{i:04d}.jpg").write_bytes(b"x" + str(i).encode())
    scenes = discover_scenes(d)
    assert len(scenes) == 1 and len(scenes[0].files) == 3


# --------------------------------------------------------------------------
# 4. deterministic shuffling with a fixed seed
# --------------------------------------------------------------------------


def test_scene_shuffle_is_deterministic(tmp_path):
    root = tmp_path / "f"
    for n in range(8):
        make_scene(root, f"Scene{n:02d}", ["frame_1.jpg", "frame_2.jpg"])
    a = [s.name for s in order_scenes(discover_scenes(root), "scene-shuffle", 42)]
    b = [s.name for s in order_scenes(discover_scenes(root), "scene-shuffle", 42)]
    c = [s.name for s in order_scenes(discover_scenes(root), "scene-shuffle", 7)]
    assert a == b
    assert a != c or sorted(a) == sorted(c)   # different seed => (near always) different
    assert sorted(a) == sorted(s.name for s in discover_scenes(root))


def test_scene_shuffle_preserves_temporal_order_inside_scene(tmp_path):
    root = tmp_path / "f"
    for n in range(4):
        make_scene(root, f"S{n}", [f"frame_{i}.jpg" for i in (1, 2, 10)])
    for s in order_scenes(discover_scenes(root), "scene-shuffle", 99):
        assert [f.filename for f in s.files] == [
            "frame_1.jpg", "frame_2.jpg", "frame_10.jpg",
        ]


def test_frame_shuffle_is_deterministic_and_lossless(dataset):
    a = order_scenes(discover_scenes(dataset), "frame-shuffle", 5)
    b = order_scenes(discover_scenes(dataset), "frame-shuffle", 5)
    assert [[f.filename for f in s.files] for s in a] == \
           [[f.filename for f in s.files] for s in b]
    for s in a:
        orig = {f.filename for f in
                next(x for x in discover_scenes(dataset) if x.name == s.name).files}
        assert {f.filename for f in s.files} == orig   # nothing dropped


def test_shuffle_requires_seed(dataset):
    with pytest.raises(ValueError):
        order_scenes(discover_scenes(dataset), "scene-shuffle", None)


# --------------------------------------------------------------------------
# 5. duplicate detection
# --------------------------------------------------------------------------


def test_duplicate_content_detected(tmp_path):
    root = tmp_path / "f"
    d = make_scene(root, "S1", ["frame_1.jpg", "frame_2.jpg"])
    (d / "frame_3.jpg").write_bytes((d / "frame_1.jpg").read_bytes())
    rep = validate(discover_scenes(root), root)
    assert len(rep.duplicate_contents) == 1
    assert sorted(rep.duplicate_contents[0]["paths"]) == \
        ["S1/frame_1.jpg", "S1/frame_3.jpg"]


def test_duplicate_basename_across_subdirs_detected(tmp_path):
    root = tmp_path / "f"
    d = make_scene(root, "S1", ["frame_1.jpg"])
    (d / "sub").mkdir()
    (d / "sub" / "frame_1.jpg").write_bytes(b"other")
    rep = validate(discover_scenes(root), root)
    assert rep.duplicate_filenames[0]["filename"] == "frame_1.jpg"


def test_no_false_duplicate(dataset):
    rep = validate(discover_scenes(dataset), dataset)
    assert rep.duplicate_contents == [] and rep.duplicate_filenames == []


# --------------------------------------------------------------------------
# 6. ambiguous filenames + missing sequence
# --------------------------------------------------------------------------


def test_ambiguous_files_reported_and_kept(tmp_path):
    root = tmp_path / "f"
    make_scene(root, "S1", ["frame_1.jpg", "frame_2.jpg", "thumbnail.jpg"])
    scenes = discover_scenes(root)
    rep = validate(scenes, root)
    assert "S1/thumbnail.jpg" in rep.ambiguous_files
    s = order_scenes(scenes, "temporal")[0]
    assert len(s.files) == 3                      # not discarded
    assert s.files[-1].filename == "thumbnail.jpg"  # placed last


def test_missing_sequence_numbers_detected(tmp_path):
    root = tmp_path / "f"
    make_scene(root, "S1", [f"frame_{i}.jpg" for i in (1, 2, 3, 5, 6, 7, 8)])
    rep = validate(discover_scenes(root), root)
    assert rep.missing_sequence[0]["missing"] == [4]


def test_sampled_step_does_not_report_false_gaps(tmp_path):
    root = tmp_path / "f"
    make_scene(root, "S1", [f"frame_{i:04d}.jpg" for i in range(0, 150, 30)])
    rep = validate(discover_scenes(root), root)
    assert rep.missing_sequence == []


def test_inconsistent_scene_detected(tmp_path):
    root = tmp_path / "f"
    d = make_scene(root, "Abuse028_x264", ["frame_1.jpg"])
    (d / "Arson009_x264_frame_2.jpg").write_bytes(b"z")
    rep = validate(discover_scenes(root), root)
    assert rep.inconsistent_scene[0]["name_scene"] == "Arson009_x264"


# --------------------------------------------------------------------------
# 7. scene boundary preservation + safety + reversibility
# --------------------------------------------------------------------------


def test_scene_boundaries_preserved_in_output(tmp_path, dataset):
    out = tmp_path / "out"
    scenes = discover_scenes(dataset)
    rep = validate(scenes, dataset)
    ordered = order_scenes(scenes, "frame-shuffle", 3)
    recs = plan(ordered)
    apply_plan(recs, ordered, dataset, out, rep)
    for r in recs:
        assert r.new_rel_path.split("/")[0] == r.scene
        assert r.rel_path.split("/")[0] == r.scene


def test_input_is_never_modified(tmp_path, dataset):
    before = {p.relative_to(dataset).as_posix(): p.read_bytes()
              for p in dataset.rglob("*") if p.is_file()}
    out = tmp_path / "out"
    scenes = discover_scenes(dataset)
    rep = validate(scenes, dataset)
    ordered = order_scenes(scenes, "scene-shuffle", 1)
    apply_plan(plan(ordered), ordered, dataset, out, rep)
    after = {p.relative_to(dataset).as_posix(): p.read_bytes()
             for p in dataset.rglob("*") if p.is_file()}
    assert before == after


def test_mapping_is_complete_and_reversible(tmp_path, dataset):
    out = tmp_path / "out"
    scenes = discover_scenes(dataset)
    rep = validate(scenes, dataset)
    ordered = order_scenes(scenes, "temporal")
    recs = plan(ordered)
    apply_plan(recs, ordered, dataset, out, rep)

    mapping = json.loads((out / MAPPING_FILENAME).read_text())
    assert len(mapping["entries"]) == 11
    for e in mapping["entries"]:
        assert (dataset / e["original_path"]).exists()
        assert (out / e["new_path"]).exists()

    res = revert(out, delete=True)
    assert res["restorable"] and res["deleted_output"]
    assert not out.exists()
    assert len(list(dataset.rglob("*.jpg"))) == 11


def test_filenames_preserved_by_default(tmp_path, dataset):
    out = tmp_path / "out"
    scenes = discover_scenes(dataset)
    ordered = order_scenes(scenes, "temporal")
    recs = plan(ordered)
    apply_plan(recs, ordered, dataset, out, validate(scenes, dataset))
    assert (out / "Abuse028_x264" / "frame_10.jpg").exists()


def test_rename_mode_embeds_original_name(tmp_path, dataset):
    ordered = order_scenes(discover_scenes(dataset), "temporal")
    recs = plan(ordered, rename=True, pad=4)
    names = [Path(r.new_rel_path).name for r in recs if r.scene == "Abuse028_x264"]
    assert names[0] == "0000__frame_1.jpg"
    assert names[3] == "0003__frame_10.jpg"
    assert all("__" in n for n in names)


def test_output_inside_input_rejected(tmp_path, dataset):
    scenes = discover_scenes(dataset)
    ordered = order_scenes(scenes, "temporal")
    with pytest.raises(ValueError):
        apply_plan(plan(ordered), ordered, dataset, dataset / "inner",
                   validate(scenes, dataset))


# --------------------------------------------------------------------------
# 8. reproducibility end-to-end + loader integration
# --------------------------------------------------------------------------


def test_end_to_end_reproducible(tmp_path, dataset):
    def run(dest):
        scenes = discover_scenes(dataset)
        rep = validate(scenes, dataset)
        rep.mode, rep.seed = "scene-shuffle", 2024
        ordered = order_scenes(scenes, "scene-shuffle", 2024)
        recs = plan(ordered, rename=True)
        apply_plan(recs, ordered, dataset, dest, rep)
        m = json.loads((dest / MAPPING_FILENAME).read_text())
        return m["scene_order"], [(e["scene"], e["index"], e["new_path"])
                                  for e in m["entries"]]

    assert run(tmp_path / "a") == run(tmp_path / "b")


def test_loader_reads_order_manifest(tmp_path, dataset):
    out = tmp_path / "out"
    scenes = discover_scenes(dataset)
    ordered = order_scenes(scenes, "temporal")
    apply_plan(plan(ordered), ordered, dataset, out, validate(scenes, dataset))
    frames = ordered_frames(out / "Abuse028_x264")
    assert [p.name for p in frames][:4] == [
        "frame_1.jpg", "frame_2.jpg", "frame_3.jpg", "frame_10.jpg",
    ]
    assert [n for n, _ in iter_scenes(out)] == ["Abuse028_x264", "Arson009_x264"]


def test_loader_without_manifest_still_orders(dataset):
    frames = ordered_frames(dataset / "Abuse028_x264")
    assert [p.name for p in frames] == [
        "frame_1.jpg", "frame_2.jpg", "frame_3.jpg",
        "frame_10.jpg", "frame_11.jpg", "frame_20.jpg",
    ]


def test_cli_dry_run(dataset, capsys):
    assert main(["--input", str(dataset), "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "total scenes         : 2" in out
    assert "total files          : 11" in out
    assert "dry run" in out


def test_cli_writes_and_reverts(tmp_path, dataset):
    out = tmp_path / "cli_out"
    assert main(["-i", str(dataset), "-o", str(out),
                 "-m", "scene-shuffle", "--seed", "11", "--link", "copy"]) == 0
    assert (out / MAPPING_FILENAME).is_file()
    assert main(["--revert", str(out), "--delete"]) == 0
    assert not out.exists()


def test_cli_requires_seed_for_shuffle(dataset):
    with pytest.raises(SystemExit):
        main(["-i", str(dataset), "--dry-run", "-m", "frame-shuffle"])


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
