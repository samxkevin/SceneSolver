# Supervisor Supplied Non Ultralytics Model Survey

**Status:** Active feasibility study. Candidates are documented for research and controlled Arena evaluation, not production recommendations.

**Study date:** 2026 10 05.

## Supervisor constraints

1. The existing SceneSolver seven class classifier is not the baseline.
2. The CCTV system is not being implemented at this stage. This is a feasibility study.
3. The baseline must therefore be evaluated around open world perception and the resulting event, temporal, rule and evidence contracts.
4. GitHub is the primary implementation and documentation source whenever an official repository exists.
5. Published benchmarks are recorded separately from future Arena measurements.
6. A model cannot be selected solely because it is newer or has a higher published benchmark.

## 1. Supervisor supplied seed set outside the Ultralytics family

The following names are retained as the supervisor supplied research seed set. They remain in the survey even when their original release predates 2025, because they are useful references or may have newer descendants.

### Tracking Any Point

TAPNext, CoTracker3, BootsTAP, SpatialTracker.

### Detection, grounding and segmentation

Grounding DINO 1.6, DINOv3, OWLv2, SAM 2, SAM 3.

### NVIDIA

NVILA, Cosmos World Foundation Models, FoundationPose, NVDINOv2, CuMo.

### General vision language models

Qwen2.5 VL, Qwen3 VL, InternVL3, InternVL3.5, PaliGemma 2, Florence 2, Florence 3, LLaVA NeXT, LLaVA OneVision, Gemini 2.5 Flash, Gemini 2.5 Pro Vision, GPT 4o vision, GPT 5 vision.

### Core visual encoders and geometry

SigLIP 2, EVA 02, EVA CLIP, ConvNeXt V2, DINOv2.5, Depth Anything 3, Depth Pro.

Names that remain uncertain in the original seed set, especially Florence 3, DINOv2.5 and NVDINOv2, require exact model identity and primary source verification before they receive a final model card. They are not silently replaced.

## 2. Current generation classification

| Candidate | Current survey status | Notes |
|---|---|---|
| TAPNext | 2025 frontier | Current Google DeepMind point tracker |
| TAPNext plus plus | 2026 frontier descendant | Long horizon, occlusion and redetection extension |
| BootsTAP | Training method | Bootstrapped training procedure used for TAPIR and TAPNext |
| CoTracker3 | 2024 reference | Important stable point tracking reference |
| SpatialTracker | 2024 reference | 3D point tracking reference |
| SpatialTrackerV2 | 2025 frontier descendant | Current successor to SpatialTracker V1 |
| Grounding DINO 1.6 | 2024 reference | Strong open vocabulary detector |
| DINOv3 | 2025 frontier | Visual foundation backbone and downstream model family |
| OWLv2 | 2023 reference | CLIP based open vocabulary detector |
| SAM 2 | 2024 reference | Promptable video segmentation and tracking |
| SAM 3 | 2025 frontier | Open vocabulary concept segmentation and tracking |
| SAM 3.1 | 2026 frontier update | Multi object tracking efficiency update |
| YOLO World V2.1 | 2025 reference | Non Ultralytics open vocabulary YOLO line |
| YOLOE 26 | 2026 frontier | Ultralytics open vocabulary line, documented separately |
| YOLO26 | 2026 frontier | Ultralytics closed set real time family, documented separately |
| Qwen3 VL | 2025 frontier | General image and video language model family |
| InternVL3.5 | 2025 frontier | Open multimodal model family |
| Cosmos 3 | 2026 frontier | Physical AI world model family |
| Depth Anything 3 | 2025 frontier | Multi view and monocular geometry family |
| SigLIP 2 | 2025 frontier | Vision language encoder family |

## 3. Tracking Any Point family

### 3.1 TAPNext

Official implementation: https://github.com/google-deepmind/tapnet

TAPNext is Google DeepMind's 2025 Tracking Any Point model. The official repository describes it as the latest, fastest and simplest tracker in the TAP family and formulates tracking as next token prediction. It can operate online, propagating point information through the network.

Input: video frames plus query points.

Output: point trajectories and visibility over subsequent frames.

What it could do for CCTV:
- Track arbitrary points on objects without requiring a fixed object class.
- Provide fine grained trajectories for motion and deformation analysis.
- Operate online, which is suitable in principle for continuous camera streams.
- Support class agnostic motion tracking.

What it cannot do:
- Detect an object semantically by itself.
- Decide whether the tracked entity is authorized.
- Determine a compliance rule.
- Replace a multi object detector when initial target points are not known.
- Produce a policy decision.

Important architectural point: TAPNext is a tracking component, not the open world perception layer.

Potential path: detector or promptable model -> query points -> TAPNext -> trajectories -> temporal state -> rule.

### 3.2 TAPNext plus plus

The current official TAP repository also provides TAPNext plus plus, a stronger 2026 checkpoint. The repository describes approximately 40 times longer stable tracking, occlusion tracking and redetection. It is fine tuned on 1024 frame synthetic sequences, and the current repository includes 512 by 512 VOTSp2026 evaluation code.

Current repository benchmark table:
- TAPNext, TrecViT B, 256 by 256, DAVIS First AJ 65.25 percent.
- TAPNext plus plus, TrecViT B, 256 by 256, DAVIS First AJ 65.6 percent.
- TAPNext plus plus at 512 by 512, DAVIS First AJ 67.0 percent and DAVIS Strided AJ 71.2 percent.

These are TAP benchmark conditions, not CCTV compliance measurements.

### 3.3 BootsTAP

BootsTAP is important to classify correctly. It is primarily a training procedure, not a separate tracker architecture.

The official DeepMind repository describes Bootstrapped Training for TAP as using unlabeled real world video to improve tracking consistency under spatial transformations, video corruptions and different query point selections.

It was used to create BootsTAPIR and contributes to the training of the strongest TAPNext checkpoint.

Why it matters: if representative deployment video is available, this style of self training may reduce manual tracking annotation requirements.

Arena role: not a primary inference competitor. Evaluate indirectly through the tracker checkpoint it produces.

### 3.4 CoTracker3

Official implementation: https://github.com/facebookresearch/co-tracker

CoTracker3 is a transformer based model for tracking any point in a video. The official repository supports online and offline variants.

What it could do:
- Track arbitrary pixels.
- Track many points together.
- Operate online or offline.
- Provide trajectories and visibility useful for geometric temporal analysis.

Limitations:
- It is not a semantic detector.
- A point trajectory does not identify the object class.
- Dense point tracking can become expensive.
- Severe occlusion and appearance changes can still break tracks.
- A conventional detector plus lightweight association tracker may be cheaper for many CCTV duration rules.

Resource evidence:
The official repository recommends CUDA for normal use but states that small tasks can run on CPU.

Arena role: point tracking reference and geometric challenger to box based tracking.

### 3.5 SpatialTracker

SpatialTracker V1 is a CVPR 2024 system for tracking 2D pixels in 3D space. Its method lifts image points into 3D using monocular depth, uses a triplane representation and estimates 3D trajectories.

Official implementation: https://github.com/RR-2000/SpaTracker_Datagen

The official implementation reports an RTX A6000 setup and approximately 22 GB GPU memory sufficient for dense tracking of around 10,000 points.

What it adds:
- 2D point motion becomes an estimated 3D trajectory.
- Potentially useful for distance, spatial motion and camera motion analysis.

Why it should not be the core baseline automatically:
Most compliance rules do not require full 3D reconstruction. A 2D zone dwell rule can normally be solved using image geometry, tracking and timers. Full 3D tracking may add compute, depth uncertainty and calibration complexity without adding rule value.

### 3.6 SpatialTrackerV2

SpatialTrackerV2 is the 2025 successor and should be the current representative of this family in the 2025 to 2026 survey.

The project reports jointly producing:
- consistent depth
- camera poses
- pixel wise 3D tracking

It was announced in July 2025 and accepted at ICCV 2025.

Arena question:
Does 3D trajectory information improve an actual CCTV rule enough to justify additional compute and geometry dependence?

## 4. Tracking family conclusion

TAPNext and TAPNext plus plus are the strongest current family candidates.

CoTracker3 is a strong stable reference.

SpatialTrackerV2 is the most interesting 3D successor.

BootsTAP should be classified as a training method.

The default CCTV baseline should not automatically become a TAP system. A normal object detector plus a lightweight MOT tracker may remain substantially cheaper for common rules.

The relevant Arena question is not which tracker has the highest TAP benchmark.

The relevant question is which tracking method most reliably preserves the entity state required by actual rules at acceptable cost.

## 5. Latest year expansion outside Ultralytics

The first verified 2025 to 2026 expansion beyond the supervisor seed list includes:

TAPNext, TAPNext plus plus, SpatialTrackerV2, DINOv3, SAM 3, SAM 3.1, Qwen3 VL, InternVL3.5, Cosmos 3, Depth Anything 3 and SigLIP 2.

These are the first priority for the frontier pass.

Older supervisor supplied models remain as controlled references rather than being discarded.

## 6. Current non Ultralytics research queue

Priority 1:
DINOv3, SAM 3 and SAM 3.1, Grounding DINO 1.6, DINO X, OWLv2.

Priority 2:
Qwen3 VL, InternVL3.5, NVILA, Cosmos 3, SigLIP 2, Depth Anything 3, Depth Pro.

Priority 3:
Qwen2.5 VL, PaliGemma 2, Florence 2, LLaVA NeXT, LLaVA OneVision, EVA 02, EVA CLIP, ConvNeXt V2, FoundationPose, CoTracker3 and SpatialTracker.

Priority 4:
Exact verification of Florence 3, DINOv2.5 and NVDINOv2, plus any additional 2025 to 2026 models discovered during the literature search.

## 7. Arena boundary

Arena is an evaluation instrument in this study.

No model is promoted merely because it is newer, larger, higher scoring on a paper benchmark, or marketed as real time.

Promotion requires evidence that the model improves the observations needed by a CCTV compliance rule at acceptable resource, privacy, reliability and licensing cost.
