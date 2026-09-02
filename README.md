# SceneSolver

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Dataset Tools](https://img.shields.io/badge/Dataset-Tools-000000?style=for-the-badge)](DatasetTools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live-Demo-FFB000?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/spaces/samxkevin/SceneSolver)

**SceneSolver is a multimodal forensic analysis system for surveillance video.**
It ingests a CCTV clip, decides whether something anomalous happens in it,
classifies what kind of incident it is, extracts supporting visual and acoustic
evidence, and emits a structured, human-readable forensic report.

**Live demo:** <https://huggingface.co/spaces/samxkevin/SceneSolver>

---

## What SceneSolver does

Given a surveillance video, the system:

1. Extracts frames and derives a per-frame anomaly signal.
2. Decides **anomaly vs. normal** with a fine-tuned video transformer.
3. If anomalous, classifies the **incident category** (e.g. `TheftOrLarceny`,
   `Aggression`, `Firebombing` — see `Timesformer/classification_report_TFM.json`).
4. Runs conditional **weapon/object detection** on the relevant keyframes.
5. Extracts **acoustic features** from the audio track as an environmental signal.
6. Fuses every stage into a single reasoning trace with an explicit verdict.
7. Renders a **PDF/HTML forensic report** with charts, evidence frames and a
   plain-English narrative.

A key design rule, enforced throughout: the pipeline is **staged and ordered**,
and a `Normal` verdict from the binary stage suppresses the downstream
incident-classification and weapon stages rather than letting a weak signal
escalate on its own.

---

## High-level multimodal pipeline

The orchestrated execution order implemented in [`Orchestrator.ipynb`](Orchestrator.ipynb)
("Scene Solver v3 — Coherent Reasoning System"):

| Stage | Component | Role |
|---|---|---|
| 0 | **AutoEncoder (AE)** | Primary anomaly signal, batched reconstruction error |
| 1 | **TimeSformer Binary** | Semantic understanding — anomaly / normal |
| 2 | **TimeSformer Multi-class** | Fine-grained incident classification |
| 3 | **YOLO Weapon** *(experimental)* | Hard safety trigger, conditional |
| 4 | **Audio Feature Extraction** | Environmental / acoustic signal |
| 5 | **Tracking / Behaviour** | Motion behaviour extraction |
| 6 | **Fusion Layer** | Explainable reasoning core |
| 7 | **RL3033** *(experimental)* | Temporal reasoning agent, final stage |
| 8 | **LLaVA** *(experimental)* | Multi-frame context explanation |

Stage 2 uses **segment-wise, AE-weighted temporal sampling**, so frames are
chosen where the anomaly signal is strongest instead of uniformly.

Stages 3, 7 and 8 are marked EXPERIMENTAL in the source and are surfaced as
such in the generated reports.

---

## Core components

### Anomaly detection (AutoEncoder)
Unsupervised reconstruction-error model trained on normal footage; provides the
primary deviation signal that drives temporal sampling downstream.
See [`autoencoderAndReinforcementLearning/RL+AE.ipynb`](autoencoderAndReinforcementLearning/RL%2BAE.ipynb),
with training curves and reconstruction samples in the same directory.

### TimeSformer / video understanding
Two heads built on `facebook/timesformer-base-finetuned-k400`:
a **binary** anomaly/normal classifier and a **multi-class** incident
classifier. Training notebooks, confusion matrix, per-class report and training
history live in [`Timesformer/`](Timesformer/). The recorded binary checkpoint
reports `best_acc ≈ 0.956` (`Timesformer/training_config_binary_TFB.json`).

An enhanced variant with a temporal attention mechanism is in
[`UnrefinedCoreFuntionality/EnhancedTemporalTraining.py`](UnrefinedCoreFuntionality/EnhancedTemporalTraining.py).

### CLIP-based keyframe selection
Frames are embedded and scored against prompts to select action-representative
keyframes, preserving temporal context without bloating computation.
See [`UnrefinedCoreFuntionality/ExplorationsInCLIP/`](UnrefinedCoreFuntionality/ExplorationsInCLIP/)
and the detailed step-by-step spec in [`Insights.md`](Insights.md).

### YOLOv8 evidence extraction
`ultralytics` YOLO (`yolov8n.pt`) runs **conditionally** on anomalous keyframes
as a weapon/dangerous-object safety trigger, not on every frame.

### LLaVA contextual explanation
`LlavaForConditionalGeneration` ingests multiple keyframes and synthesises them
into one coherent scene narrative for the report. Training notebook and the
instruction-tuning manifests are in [`LLaVa/`](LLaVa/) — the manifests follow a
JSONL schema with an `image` path and a user/assistant `conversations` pair.

### Audio analysis
Three distinct pieces:

- **In-pipeline acoustic features** (Stage 4) extracted with `librosa` —
  `rms`, `zcr`, `spectral_centroid`, `spectral_flux` and `mfcc`, each normalised
  to 0–1 against global ranges and combined into a weighted composite score.
  Classification rule: 2+ features above 0.4 = `ANOMALY`, 1 = `SUSPICIOUS`,
  0 = `NORMAL`. Audio is optional; the stage degrades gracefully when `librosa`
  is unavailable or the track is silent.
- **Spectrogram anomaly detection** — a convolutional autoencoder trained
  unsupervised on mel-spectrograms of normal surveillance audio
  ([`SpectrogramAnalysis/`](SpectrogramAnalysis/)), with a checkpoint, training
  curves and results JSON included.
- **LFM2.5-Audio speech interface** — `LiquidAI/LFM2.5-Audio-1.5B` via the
  `liquid-audio` package, used as the speech bridge for the Sherl0ck agent
  (see below): ASR for the analyst's speech and TTS for the agent's replies.

### LFM (Liquid Foundation Model) speech layer
> Implemented in [`NewChecker.ipynb`](NewChecker.ipynb), alongside the Sherl0ck
> agent below. These two sections describe that notebook rather than
> `Orchestrator.ipynb`.

The **LFM2.5-Audio-1.5B** model (~3.65 GB, lazily loaded on first use, moved to
CUDA when available) performs both directions of the voice interface:

- **ASR** — `ChatState` with a `"Perform ASR."` system turn transcribes the
  analyst's recorded utterance. Output is stripped of special tokens and
  rejected if it looks like non-English/garbled decoding.
- **TTS** — a `"Perform TTS. Use the US male voice."` system turn generates
  audio codes, decoded to a 24 kHz waveform. Every generated file is validated
  (RIFF/WAVE header, sample rate, frame count) before being returned.

LFM handles **speech only** — the reasoning is Cohere's. Availability is
detected at import; the voice layer degrades cleanly when `liquid-audio` is
absent.

### Sherl0ck — agentic escalation layer
A voice-driven escalation agent layered on top of the finished analysis. When a
run crosses the critical threshold, the app can place a simulated call: the
browser records the analyst with client-side VAD and `MediaRecorder`, posts the
WebM/Opus blob to a same-origin FastAPI route mounted on the Gradio app
(`POST /ssvoice/turn`, with `/ssvoice/health`, `/ssvoice/end`, `/ssvoice/accept`
and `/ssvoice/ringtone` alongside), and gets spoken audio back — with barge-in
supported mid-reply.

The turn loop is: **LFM ASR → Cohere reasoning (`ClientV2`) → LFM TTS**. The
agent is briefed with the full case context so it can answer questions about the
specific incident rather than in the abstract.

Escalation itself is threshold-driven — `THRESH_CRITICAL = 0.90` and
`THRESH_HIGH = 0.70` — and a critical result can auto-dispatch the peak-anomaly
frame and the forensic PDF to Telegram, Discord and email.

### Forensic report generation
`reportlab`-based PDF plus HTML output containing an executive summary, a
status badge (`ANOMALY DETECTED (CRITICAL)` / `NO ANOMALY DETECTED (SAFE)`),
per-stage findings, an AE-deviation graph, a Stage 2 class-distribution chart,
annotated evidence frames and plain-English explanations of the acoustic and
RL observation dimensions. See [`ReportGeneration/`](ReportGeneration/) for the
notebook, the standalone scripts in
[`ReportGeneration/VanillaCode/`](ReportGeneration/VanillaCode/), and a complete
worked example under `ReportGeneration/InferenceResults/`.

### Contact / email notification workflow
The web app includes an SMTP (`smtplib` + `ssl`, `SMTP_SSL`) contact-form
handler that emails submissions to an administrator address. It is credential-
gated: without `SENDER_EMAIL` / `SENDER_PASS` set it falls back to appending to
a local log file instead of sending. See the note under
[Setup](#setup--usage) about configuring these.

### Web interface
A Gradio application defined in [`Orchestrator.ipynb`](Orchestrator.ipynb)
provides Home / Analyse / Contact tabs, video upload, inline rendering of the
AE deviation graph, the risk-assessment report and a disclaimer banner. This is
what backs the Hugging Face Space.

Earlier React/HTML prototypes are preserved under [`WebApp/`](WebApp/).

---

## Architecture / workflow overview

```
        surveillance video (.mp4)
                  │
                  ▼
    ┌─────────────────────────────┐
    │ frame extraction            │  cv2, fixed interval → frame_%04d.jpg
    └─────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │ DatasetTools (offline prep) │  validate • order • split  → order.jsonl
    └─────────────────────────────┘
                  │
                  ▼
   Stage 0  AutoEncoder ─────────────► per-frame deviation signal
                  │                             │
                  ▼                             │ AE-weighted
   Stage 1  TimeSformer Binary                  │ segment sampling
                  │                             │
        ┌─────────┴─────────┐                   │
     Normal              Anomaly ◄──────────────┘
        │                   │
        │                   ▼
        │        Stage 2  TimeSformer Multi-class
        │                   │
        │                   ▼
        │        Stage 3  YOLOv8 weapon detection (conditional)
        │                   │
        └─────────┬─────────┘
                  ▼
   Stage 4  Audio features   Stage 5  Tracking / behaviour
                  │                   │
                  └─────────┬─────────┘
                            ▼
                 Stage 6  Fusion / reasoning
                            ▼
                 Stage 7  RL3033 (experimental)
                            ▼
                 Stage 8  LLaVA narrative (experimental)
                            ▼
                 PDF + HTML forensic report
```

---

## Dataset and preprocessing / training workflow

SceneSolver is built around **UCF-Crime**-style classwise surveillance footage.
The phased workflow documented in [`Insights.md`](Insights.md):

| Phase | Step |
|---|---|
| 0 | Raw `.mp4` videos in classwise folders |
| 1 | **Dataset integrity** — verify every file against `train.txt`, no broken paths |
| 2 | **Frame extraction** — uniform or length-adaptive sampling per video |
| 3 | **CLIP keyframe selection** — rank and keep action-representative frames |
| 4 | **Binary anomaly detection** — train/fine-tune TimeSformer |
| 5 | **Incident classification** — fine-tune the classifier head on anomalies only |
| 6 | **Evidence extraction** — YOLOv8 on anomalous keyframes |
| 7 | **Report generation** — LLaVA over keyframes + detections |

Frame-naming conventions already produced by the extractors in this repository:

| Producer | Pattern |
|---|---|
| `ReportGeneration/VanillaCode/cctv_analysis_script.py` | `frame_%04d.jpg` |
| `UnrefinedCoreFuntionality/ExplorationsInCLIP` | `frame_%06d.jpg` |
| `LLaVa` (`FireLLaVA_frames`) | `%06d_%d.jpg` = `<frame>_<variant>` |

A **scene** is one directory named after the source video id, e.g.
`outputs/frames/Abuse028_x264/`.

---

## DatasetTools

[`DatasetTools/`](DatasetTools/) is the dataset preparation module that sits
between **Phase 2 (frame extraction)** and **Phase 4 (training)**. It exists
because naive `sorted(os.listdir(...))` orders frames as
`frame_1, frame_10, frame_2` — silently corrupting the temporal sequence fed to
TimeSformer.

It provides:

- **Deterministic scene/frame ordering** — parses frame numbers, `<frame>_<variant>`
  pairs, `hh:mm:ss` timestamps and millisecond tokens, always preferring explicit
  numeric/temporal evidence over lexicographic sorting.
- **Scene-level shuffling** — shuffles scene order for train/val splits while
  every clip stays temporally contiguous.
- **Frame-level randomization** — opt-in, for ablations; scene grouping is
  still never broken.
- **Reproducible seeds** — per-scene RNG streams, so the same seed always yields
  the same output and adding a scene cannot perturb another's permutation.
- **Validation** — duplicate filenames, duplicate content by SHA-256, missing
  sequence numbers (with sampled-step awareness), files assigned to inconsistent
  scenes, and files that cannot be confidently ordered. Nothing is silently
  discarded.
- **Reversible, non-destructive preparation** — the input tree is read-only,
  output goes to a separate directory (hardlink by default), a full
  original → new mapping is written, and `--revert` undoes the operation.

Quick start:

```bash
# validate only — writes nothing
python DatasetTools/scene_organizer.py -i outputs/frames --dry-run

# deterministic training split
python DatasetTools/scene_organizer.py \
    -i outputs/frames -o build/frames_train -m scene-shuffle --seed 1337

# undo
python DatasetTools/scene_organizer.py --revert build/frames_train --delete
```

Downstream code should consume the ordering helpers rather than listing
directories directly:

```python
from DatasetTools.scene_loader import ordered_frames, iter_scenes

frames = ordered_frames(frames_dir)          # frame_1, frame_2, frame_10
```

📖 **Full module documentation: [`DatasetTools/README.md`](DatasetTools/README.md)**

---

## Repository structure

```
SceneSolver/
├── README.md                          # this file
├── LICENSE                            # MIT
├── Insights.md                        # project documentation, phases, dev log
├── Orchestrator.ipynb                 # v3 pipeline + Gradio web app
│
├── DatasetTools/                      # dataset/scene organization module
│   ├── README.md                      # detailed module documentation
│   ├── scene_organizer.py             # CLI: validate / order / shuffle / revert
│   ├── scene_loader.py                # ordered_frames() / iter_scenes()
│   └── tests/                         # 30 tests
│
├── Timesformer/                       # binary + multi-class training, metrics
├── autoencoderAndReinforcementLearning/  # AE + RL notebooks, training logs
├── SpectrogramAnalysis/               # audio CAE, checkpoint, results
├── LLaVa/                             # LLaVA training + JSONL manifests
├── ReportGeneration/                  # report notebooks, scripts, sample output
│   ├── VanillaCode/                   # standalone analysis scripts
│   └── InferenceResults/              # worked example: frames, PDF, HTML, JSON
├── UnrefinedCoreFuntionality/         # temporal training, CLIP explorations
│   └── ExplorationsInCLIP/            # CLIP anomaly inference + frame outputs
├── WebApp/                            # earlier React / HTML front-end prototypes
└── InitiationActivities/              # early preprocessing experiments
```

---

## Setup / usage

### Easiest path — hosted demo

Use the Hugging Face Space, no installation required:
<https://huggingface.co/spaces/samxkevin/SceneSolver>

### DatasetTools locally

DatasetTools is **pure standard library** — no third-party dependencies:

```bash
git clone https://github.com/samxkevin/SceneSolver.git
cd SceneSolver

python DatasetTools/scene_organizer.py --help
python DatasetTools/scene_organizer.py -i <frames_dir> --dry-run
```

Running its test suite requires only `pytest`:

```bash
pip install pytest
python -m pytest DatasetTools/tests -q      # 30 passed
```

### Full pipeline

The pipeline notebooks were developed in Google Colab against Google
Drive–mounted data, and expect GPU plus model checkpoints that are not stored
in this repository. Dependencies are installed inline by the notebooks:

```python
!pip install -qq reportlab stable-baselines3 ultralytics
!pip install -q librosa soundfile audioread pydub torchaudio
!pip install -q "cohere>=5.0.0" liquid-audio soundfile
!apt-get install -y -qq ffmpeg
```

Open [`Orchestrator.ipynb`](Orchestrator.ipynb) and run the pipeline cell, then
the Gradio app cell. Optional graceful degradations are built in:
`stable-baselines3` missing → Stage 7 skipped; `librosa` missing → audio stage
skipped; `liquid-audio` missing → the Sherl0ck voice layer is disabled while
the rest of the app runs normally.

To enable the contact-form email workflow, set `SENDER_EMAIL` and
`SENDER_PASS` in the environment (Hugging Face Space secrets, or your shell).
**Never commit credentials.** Without them the handler logs locally instead.

### Standalone report generation

```bash
python ReportGeneration/VanillaCode/RunAnalysis.py
```

---

## Disclaimer

SceneSolver is a research and academic project. Several stages are explicitly
marked EXPERIMENTAL. Its output is **not** a substitute for professional
forensic examination and must not be treated as evidence or as the basis for
any legal or enforcement decision.

---

## License

Released under the MIT License — see [`LICENSE`](LICENSE).

Copyright (c) 2026 Anumula Samarth
