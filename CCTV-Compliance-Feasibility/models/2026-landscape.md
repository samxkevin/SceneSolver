# 2026 Model Landscape Refresh

**Status:** candidates for controlled evaluation, not recommendations.
**Checked:** 2026-10-05 (Asia/Calcutta).
**Selection rule:** newer or broader does not mean better for continuous CCTV. Every candidate must pass the measurement, incremental value, resource, privacy, licensing and reliability gates.

## Supervisor supplied research scope

The supervisor supplied a model seed list spanning Tracking Any Point, open world detection and segmentation, NVIDIA models, general vision language models, and foundation visual encoders. The non Ultralytics portion is tracked in models/supervisor-non-ultralytics-survey.md.

The existing SceneSolver seven class classifier is explicitly **not the baseline**. This folder remains a feasibility study and is not implementing the CCTV product at this stage.

## 2025 to 2026 frontier candidates

### Tracking

- TAPNext
- TAPNext plus plus
- SpatialTrackerV2

### Detection, grounding and segmentation

- DINOv3
- SAM 3
- SAM 3.1
- Grounding DINO 1.6
- DINO X
- OWLv2 as a legacy control

### Vision language

- Qwen3 VL
- InternVL3.5
- NVILA
- Gemini 2.5 family
- GPT 5 vision capable models

### Geometry and representation

- Depth Anything 3
- SigLIP 2

### Physical AI and simulation

- Cosmos 3

## Ultralytics candidates

### YOLO26

Ultralytics documents YOLO26 as a 2026 unified family for detection, instance and semantic segmentation, pose, classification, depth and oriented detection. It includes an optional end to end path without NMS and export paths for common runtimes. The official page publishes COCO and hardware specific timing under its own conditions, including CPU ONNX on an Intel Xeon and T4 TensorRT.

**Why evaluate:** current compact closed set perception candidate, potential CPU and edge improvements, shared heads for detection, pose and segmentation.

**Why not assume it wins:** published COCO and vendor hardware results are not site object recall, camera hour alert quality or target device throughput. The default one to many path may differ from end to end mode. Licensing is a material constraint.

**Experiment:** compare YOLO26n and YOLO26s against the strongest non Ultralytics open world candidates on the same custom labels, input size, runtime, precision and camera conditions where the task formulation permits.

### YOLOE 26

Ultralytics documents YOLOE 26 as an open vocabulary detection and instance segmentation family using text prompts, visual prompts or a prompt free vocabulary. The promptable path may require a text encoder setup, which matters for offline edge deployment.

**Why evaluate:** owner rules may introduce object names not present in the closed set detector. Promptable detection can accelerate candidate exploration and annotation.

**Why not assume it wins:** zero shot prompt recognition is not calibrated site detection. Prompt wording, small objects, occlusion, temporal stability and class confusion can be poor. Open vocabulary expands uncontrolled outputs.

**Experiment:** use YOLOE 26 as a discovery and annotation candidate first. Compare fixed prompt lists against a fine tuned closed set detector on a locked site set. Require stable classes, rule event recall, false alerts per camera hour and offline reproducibility.

## Small VLM and video candidates

### Qwen3 VL

Official Qwen sources describe Qwen3 VL as a multimodal family with image and video understanding, spatial grounding, OCR and timestamp related video modeling. The 2025 family includes dense and MoE variants with Instruct and Thinking editions.

**Why evaluate:** bounded evidence review, difficult action interpretation, evidence grounded narrative and selective video question answering.

**Why not assume it wins:** vision tokens, KV cache and generation cost remain material. Natural language answers can be overconfident. Exact temporal boundaries require validation. It must not be placed in the authoritative policy path without evidence.

### SmolVLM2

SmolVLM2 provides compact video language variants useful as a lower resource advisory review arm.

**Why evaluate:** establishes a low memory lower bound for VLM based evidence review.

**Why not assume it wins:** small models can miss visual details or hallucinate. The model card cautions against high stakes critical automated decisions.

## Landscape conclusion

The 2025 to 2026 refresh does not change the core architecture:

perception -> tracking -> temporal state -> deterministic rule -> evidence.

New models are inserted only when they solve a measurable gap. VLMs are bounded review candidates, not authoritative compliance decision makers. Open world models are perception candidates, not policy engines. The supervisor supplied non Ultralytics models remain part of the survey even when their original release predates 2025, because they provide important reference points and may have newer descendants.

The detailed coverage register and first Tracking Any Point family analysis are in models/supervisor-non-ultralytics-survey.md.
