# AI/CV Model Feasibility Matrix

This matrix is a shortlist for experiments, not a ranking. “CPU feasible” means a plausible candidate for measured, sampled inference; it does not mean a complete multi-camera system will meet an SLO.

## Task formulation first

| Requirement | Correct formulation | Typical output | Not to confuse with |
|---|---|---|---|
| Person/object visible | object detection or instance segmentation | boxes/masks, class and score per frame | compliance decision |
| Same entity over time | multi-object tracking / data association | camera-local track, trajectory, quality | identity/authorization |
| Enter/leave/line crossing | state estimation over track + geometry | `entered`, `exited`, timestamp interval | frame classification |
| Smoking / lifting / hand-object action | temporal action recognition or sequence classification; sometimes pose + object cues | action probability over a clip/window | regression |
| Label at each time | sequence labeling / temporal action localization | per-frame/segment labels and boundaries | one label for a whole clip |
| “Still open/present” | state estimation + duration/absence logic | state interval and timer | anomaly score |
| “Required action not completed” | temporal logic over expected and observed events | violation after deadline | VLM free-text judgement |
| Unusual but unknown | anomaly detection / novelty detection | deviation/candidate score | violation class |
| Find images matching text | image-text retrieval / CLIP-style embedding | ranked frames | calibrated event detector |
| Explain a completed decision | constrained VLM/LLM generation grounded in evidence | narrative with citations | authoritative rule evaluation |
| Read badge/sign | OCR or access-control integration | text/token + quality | face recognition |

## Family matrix

| Family / candidate | Problem and inputs/outputs | Training / adaptation | CPU / iGPU/NPU / edge GPU / cloud | Latency and memory considerations | Quantisation / optimisation | Best system role and failure modes |
|---|---|---|---|---|---|---|
| Small YOLO-family detector | RGB frame/ROI -> boxes/classes/scores; custom classes may include person, gate, smoking cue, pallet/object | pretrained for common objects; custom labels needed for site objects/actions | **CPU:** first candidate at low rate/resolution. **iGPU/NPU:** export/runtime dependent. **Edge GPU:** strong candidate. **Cloud:** easy to scale | Cost varies drastically by variant/input/backend; benchmark end-to-end, not model-only | ONNX/OpenVINO/TensorRT exports; FP16/INT8 often practical; calibration required for INT8 | Default perception baseline. Misses small/occluded objects; detector confidence is not calibrated violation probability; licensing/model version must be reviewed |
| RT-DETR / RT-DETRv2 | Transformer detector; frame -> end-to-end detections | pretrained and fine-tuned for custom classes | **CPU:** likely less attractive than smallest CNN detector without measurement. **GPU/cloud:** credible comparison | Paper/vendor FPS and AP are condition-specific; no NMS may simplify graph but not guarantee edge efficiency | Export/runtime support and post-training calibration must be tested | Accuracy/speed challenger when small objects or crowded scenes justify it; heavier deployment and operator support risk |
| MobileNet/SSD/EfficientDet-lite-style detector | RGB frame -> boxes; compact CNN family | pretrained/custom training | **CPU:** strongest low-resource baseline. **Integrated:** plausible. **Edge/cloud:** yes | Lower capacity may reduce recall on tiny/distant objects; usually simpler memory profile | TFLite/ONNX/OpenVINO INT8; QAT if accuracy loss matters | Camera-local simple objects; can be distilled from a stronger teacher. May need per-site custom training |
| ByteTrack / SORT-style tracker | detections + timestamps -> track IDs/boxes/trajectory/quality | no neural training for base association; tuning required | CPU friendly; scales better than rerunning detector; edge/cloud | Tracker is cheap, but association errors grow with missed/ambiguous detections and long detector gaps | Tune detector interval, thresholds, motion model; appearance features optional | Zone/duration/trajectory state. Track ID is not identity; ID switches create rule errors |
| BoT-SORT / DeepSORT-style | detections + motion + optional appearance -> tracks | appearance encoder may be pretrained/fine-tuned | CPU feasible at low rate; added appearance cost; GPU helps | More robust in some occlusions but extra memory/latency and embedding privacy risk | Quantise appearance encoder; avoid appearance if it adds no measured rule value | Compare where crowded scenes break simple tracking; re-ID can expose privacy/legal concerns |
| Pose estimation | RGB crop -> keypoints/confidence | pretrained; custom domain tuning may be required | Tiny pose CPU candidate; larger models GPU/cloud | Cost per person; crowded/occluded scenes degrade; person count is a multiplier | crop ROI, keypoint subset, INT8 where supported | smoking/hand-over-face, posture and fall cues. Keypoints do not prove intent or policy violation |
| Tiny action/temporal classifier | short RGB/pose/object feature window -> action/segment score | requires site-specific positive/negative temporal labels | CPU possible for tiny feature/TCN; video transformer generally GPU/selective | Window length and stride control latency/memory; boundary quality matters | distillation, reduced frames/resolution, INT8; benchmark calibration | Hard action predicates. Dataset must cover camera angle, negatives and confounders |
| TimeSformer | multi-frame RGB clip -> clip classification; SceneSolver uses base K400 checkpoint | fine-tuning needed for target labels; published benchmarks use specific datasets/clip views | CPU continuous use is not assumed; GPU/cloud or offline/triggered candidate | Attention and frame/patch count drive memory; paper conditions are not CCTV latency | FP16/INT8 export is an experiment; reduce frames/ROI/distill | SceneSolver comparison / temporal classifier for difficult clips. Whole-clip class may hide boundaries and is not generic policy |
| VideoMAE-style encoder | video clips -> representation; fine-tune for action/temporal labels | self-supervised pretraining + task fine-tune; domain shift matters | GPU/cloud training; selective GPU inference; CPU not default | ViT/video memory and window size matter | feature caching, distillation, reduced clip size; quantise only after task validation | Research option when target video labels are scarce and unlabeled site video is available |
| CLIP-style image-text encoder | image + text prompts -> embeddings/similarity | zero-shot prompt selection; fine-tune optional | Small variants may run CPU/GPU; video-wide scoring is costly | Each sampled frame incurs image encoder work; prompt scores are not calibrated | cache text embeddings, sample/keyframe/ROI, quantise | retrieval/keyframe search and candidate generation. Prompt bias and static-frame failure |
| Segmentation | RGB -> pixel mask for gate/door/object/zone/occupancy | custom labels often needed | CPU only for small/low-rate; GPU preferred | higher memory/latency than boxes; mask quality affects geometry | ROI, low resolution, INT8 if supported | gate state, precise object placement, boundary cases; use only where boxes fail |
| Classical CV / background / optical flow | pixels or ROI -> motion/edges/color/shape/state | no training; camera-specific thresholds/calibration | CPU friendly and transparent | cheap but sensitive to lighting/camera movement/compression | ROI, morphology, adaptive thresholds | fixed gate state, line crossing, motion trigger, camera health. Not robust semantic recognition |
| OCR | crop -> text/token/confidence | pretrained; custom fonts/domain may need tuning | small OCR CPU candidate; GPU for many streams | crop quality and angle dominate; privacy/security for identifiers | ROI, rectify, small text detector; quantise supported models | badge/label/plate/token under policy. Prefer access-control events where possible |
| Audio features / classifier | waveform/spectrogram -> sound event features/labels | site audio labels; privacy review | CPU feasible for low-rate features; larger audio model GPU | audio sync and noise; continuous audio may increase privacy risk | feature extraction, small classifier, disable by default unless justified | corroborating signal only; never assume microphone is permitted or reliable |
| Qwen3-VL 2B/4B/8B Instruct | selected frames/video + prompt -> grounded answer, OCR, spatial/timestamp candidate or narrative | zero-shot or adapter evaluation; model card, checkpoint and dependency audit | 2B/4B: selective edge/workstation candidates; 8B: workstation/cloud candidate; CPU continuous use not assumed | vision tokens, KV cache and generation drive latency; video sampling and output length must be fixed | quantised GPU/edge tests; constrained JSON and citations; quantisation does not guarantee CPU speed | optional advisory evidence review; no deterministic policy authority; hallucination, temporal boundary and privacy risk |
| SmolVLM2 500M/2.2B | selected frames/video + prompt -> compact multimodal answer | zero-shot or task adaptation; use model-card limitations | 500M is low-memory review candidate; 2.2B selective edge/workstation/cloud; not default continuous CPU | vendor model-card memory result is not target capacity; video tokens and generation still cost | test low-bit variants and deterministic decoding; record exact checkpoint | advisory review/lower-bound VLM; model card cautions against high-stakes automated decisions |
| VLM (LLaVA-style / modern small VLM) | selected frames/video + prompt -> narrative/answer/structured candidate | zero-shot or LoRA/adaptation; model card/license review | CPU-only continuous use not credible for 7B/13B class by default; quantised GPU/edge selective; cloud easiest | weights/KV cache/vision tokens and generation create latency; multi-image/video increases cost | INT8/INT4 weight-only can reduce memory; does not ensure CPU speed or visual quality; LoRA reduces trainable params, not base inference cost | bounded evidence review, explanation, open-world candidate. Hallucination, bias, poor temporal precision and data egress risk |
| LLM/rule assistant | text rule description/event schema -> validated rule draft | no vision; prompting/RAG/grammar | CPU feasible for small local model; cloud optional | small relative to video but validation and security matter | constrained decoding, quantisation, no direct execution | translate natural language to draft DSL; human approves; never execute free text |
| Anomaly autoencoder | normal frame/feature/audio -> reconstruction/deviation score | normal-only data; threshold calibration | small AE CPU possible; SceneSolver video AE is a candidate only after measurement | cheap-ish per frame but score drift and thresholding dominate | small input/feature AE, INT8; calibrate on deployment domain | novelty trigger, sampling or health signal; not a compliance decision |

## Choice policy

1. Start with the smallest detector that covers the *observations* needed by the first rules.
2. Add segmentation, pose, OCR or action models only when an error analysis shows boxes/tracks/rules cannot satisfy an acceptance gate.
3. Compare ByteTrack and a stronger tracker on rule-level duration/entry metrics, not only MOT metrics.
4. Use TimeSformer/VideoMAE only for a labelled action/temporal task whose incremental value over pose/object features is measured.
5. Use CLIP/VLM/anomaly scores as candidate generation or review unless a specific task benchmark proves otherwise.
6. Promote a quantised model only after accuracy, calibration, latency, memory and thermal tests on the target runtime.

## LoRA and distillation clarification

- **LoRA/adapters:** reduce trainable parameters and adaptation storage; they do not automatically reduce the base model's inference memory, activation memory, or latency unless the deployment stack merges/prunes or uses an adapter-aware runtime.
- **Quantisation:** lowers weight/activation precision and may reduce memory/bandwidth; speed depends on kernels and hardware. Unsupported operators can fall back to FP32/CPU.
- **Distillation:** can make a small student viable, but requires a teacher, representative data and an evaluation that preserves rare-event recall.

## 2026-10-22 supervisor seed coverage audit (individual entries; not model selections)

This audit complements the family-level table above. **Source status is not a deployment approval.** `PUBLISHED` denotes official project/model documentation, `INFERENCE` denotes proposed relevance to CCTV, and `OPEN` denotes an unresolved exact-checkpoint, environment, license, or performance gate. None of these candidates has measured P1 CCTV performance. The existing SceneSolver seven-class classifier is a reference only, not the CCTV baseline.

| Supervisor category | Supplied candidate (retained) | Task fit / important distinction | Audit status |
|---|---|---|---|
| Tracking | TAPNext | point tracker, not detector | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Tracking | CoTracker3 | point tracker, not detector | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Tracking | BootsTAP | training procedure, not inference model | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Tracking | SpatialTracker | 3D point tracker | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Grounding/segmentation | Grounding DINO 1.6 | text-phrase to boxes; exact release/version gate | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Grounding/segmentation | DINOv3 | features/backbone, not zero-shot detector alone | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Grounding/segmentation | OWLv2 | text-query open-vocabulary boxes | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Grounding/segmentation | SAM2 | promptable masks/video propagation | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Grounding/segmentation | SAM3 | promptable open-vocabulary segmentation/tracking; custom license | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| NVIDIA | NVILA | VILA 2.0; image/video VLM | PUBLISHED: official family; OPEN: exact deployment gates |
| NVIDIA | Cosmos World Foundation Models | world-model/physical-AI family, not CCTV detector | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| NVIDIA | FoundationPose | 6D object pose estimation | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| NVIDIA | NV-DINOv2 (supervisor: NVDINOv2) | visual embeddings; official NVIDIA TAO/TensorRT constraints | PUBLISHED: official family; OPEN: exact deployment gates |
| NVIDIA | CuMo | multimodal MoE VLM; pretrained weights noncommercial | PUBLISHED: official family; OPEN: exact deployment gates |
| Vision-language | Qwen2.5 VL | VLM; evidence review only | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Vision-language | Qwen3 VL | VLM; evidence review only | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Vision-language | InternVL3 | VLM; evidence review only | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Vision-language | InternVL3.5 | VLM; evidence review only | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Vision-language | PaliGemma 2 | VLM; exact variant needed | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Vision-language | Florence 2 | vision-language generalist; exact checkpoint needed | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Vision-language | Florence 3 | identity unresolved; preserve seed | OPEN: model identity |
| Vision-language | LLaVA NeXT | VLM; exact checkpoint needed | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Vision-language | LLaVA OneVision | VLM; exact checkpoint needed | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Vision-language | Gemini 2.5 Flash | hosted multimodal service; API terms/data policy | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Vision-language | Gemini 2.5 Pro Vision | model/endpoint identity and availability check | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Vision-language | GPT 4o vision | hosted multimodal service; version pin | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Vision-language | GPT 5 vision | hosted model identity and version pin | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Representation/geometry | SigLIP 2 | embedding encoder | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Representation/geometry | EVA 02 | visual representation encoder | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Representation/geometry | EVA CLIP | image/text representation encoder | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Representation/geometry | ConvNeXt V2 | visual backbone | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Representation/geometry | DINOv2.5 | identity unresolved; preserve seed | OPEN: model identity |
| Representation/geometry | Depth Anything 3 | depth/geometry | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |
| Representation/geometry | Depth Pro | monocular depth/geometry | Seed preserved; OPEN: dedicated checkpoint/licensing/runtime card |

**Coverage: 34/34 supervisor seed names explicitly enumerated.** Aliases normalized without losing original spelling: `NVDINOv2` -> `NV-DINOv2`; `NVILA` = `NVILA (a.k.a. VILA 2.0)`; `CuMo` is the Co-Upcycled Mixture-of-Experts paper. `Florence 3` and `DINOv2.5` remain unverified identities; no replacement is implied. This list does not assert that every name has a completed model card. Newer additions (SAM3.1, TAPNext++, SpatialTrackerV2, DINO X, etc.) remain in the separate landscape survey and are not substituted for any supervisor seed.

### Newly expanded individual feasibility cards

| Candidate | Verified published/model documentation | Inputs -> outputs and possible position | Practical evaluation and failure risks | Hardware/precision and license gate | Decision |
|---|---|---|---|---|---|
| **NVILA (VILA 2.0)** | [NVlabs/VILA](https://github.com/NVlabs/VILA) identifies NVILA as VILA 2.0 and includes video-understanding variants; repository identifies Apache-2.0 *code* | Selected images/video + question -> generated answer/narrative. Optional bounded evidence review downstream of deterministic rules | Test hallucination, temporal grounding, prompt variability, GPU memory, p95 review latency, privacy/egress. Not primary detector, tracker, or policy authority | GPU/TensorRT-LLM/TinyChat examples are published for specific variants, **not site measurements**. Exact 3B/8B/video checkpoint, weights terms, quantized artifact, dependencies, CUDA/device, and redistribution remain **OPEN** | Research candidate only |
| **CuMo** | [SHI-Labs/CuMo](https://github.com/SHI-Labs/CuMo) and [NeurIPS paper](https://papers.nips.cc/paper_files/paper/2024/hash/ed1d3d4c64dc1b95332a8cde3f2a0bdf-Abstract-Conference.html). Co-Upcycled sparse MoE vision-encoder/connector components; Apache-2.0 code; released weights **CC BY-NC 4.0** | Image + language prompt -> VLM response. Advisory exploratory comparator only | MoE routing and total runtime memory may remain large; image QA is not grounded CCTV temporal rule evidence; no site latency/reliability established | Repository describes 4/8-bit load options, not proven edge use. Released weight non-commercial restriction: **BLOCKED for commercial deployment absent separate clearance**. Exact checkpoint/dependency gate OPEN | Research-only; no production approval |
| **NVIDIA NV-DINOv2** | [NVIDIA official model card](https://docs.api.nvidia.com/nim/reference/nvidia-nv-dinov2) identifies NV-DinoV2-224-V0 and NV-DinoV2-518-V0; model card says commercially pretrained | RGB image -> image embedding (published 1024-D ViT-L, 1536-D ViT-G); downstream detection/classification/segmentation needs task-specific head. Not a stand-alone open-vocabulary detector | Determine whether embedding+head improves necessary observations vs direct small detector; new training/head, object size, domain shift and runtime add cost | Official card restricts use to **NVIDIA hardware** with **TAO Toolkit or TensorRT**; named NVIDIA GPU/Jetson architectures, Linux/Linux4Tegra, TAO 5.2 listed. Card says 'ready for commercial use', but exact weights terms, redistribution and legal acceptance still OPEN; vendor inference-only FPS is not CCTV end-to-end | Research candidate only |

### Mandatory model-card fields prior to controlled candidate selection

For each exact checkpoint, record repository commit/revision, model/weight ID and hash, code and weights licenses separately, upstream dependencies, commercial use and redistribution, consent/retention or egress implications, input/output contract, target hardware and runtime, model load time, p50/p95 latency, peak RAM/VRAM, dropped/skipped frames, camera-hour false alerts, missed/false zone entries, dwell timing error, unknown/degraded intervals, rule-level utility and supervisor disposition. Do not infer a license from a GitHub repository's headline badge. No score or winner is asserted until a locked P1 dataset and rule specification exist.
