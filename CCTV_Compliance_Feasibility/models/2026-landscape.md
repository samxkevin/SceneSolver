# 2026 Model Landscape Refresh

**Status:** candidates for controlled evaluation, not recommendations.
**Checked:** 2026-10-02 (Asia/Calcutta local study date).
**Selection rule:** newer or broader does not mean better for continuous CCTV. Every candidate must pass the measurement, incremental value, resource, privacy, licensing and reliability gates.

## Perception candidates

### YOLO26

Ultralytics documents YOLO26 as a 2026 unified family for detection, instance/semantic segmentation, pose, classification, depth and oriented detection. It includes an optional end-to-end path without NMS and export paths for common runtimes. The official page publishes COCO and hardware-specific timing under its own conditions, including CPU ONNX on an Intel Xeon and T4 TensorRT.

**Why evaluate:** current compact closed-set perception candidate, potential CPU/edge improvements, shared heads for detection/pose/segmentation.
**Why not assume it wins:** published COCO and vendor hardware results are not site-object recall, camera-hour alert quality or target-device throughput; the default one-to-many path may differ from end-to-end mode; licensing is a material constraint.
**Experiment:** compare YOLO26n/s against the existing YOLOv8n arm on the same custom labels, input size, runtime, precision and camera conditions. Record small-object and zone-event recall.

### YOLOE-26

Ultralytics documents YOLOE-26 as an open-vocabulary detection and instance-segmentation family using text prompts, visual prompts or a prompt-free vocabulary. The promptable path may require a text encoder download/setup, which matters for offline edge deployment.

**Why evaluate:** owner rules may introduce object names not present in the closed-set detector; promptable detection can accelerate candidate exploration and annotation.
**Why not assume it wins:** zero-shot prompt recognition is not calibrated site detection; prompt wording, small objects, occlusion, temporal stability and class confusion can be poor; open vocabulary expands uncontrolled outputs and may increase privacy/operational complexity. Prompt embeddings do not replace supervised target labels.
**Experiment:** use YOLOE only as a discovery/annotation and candidate arm first. Compare fixed prompt lists against a fine-tuned closed-set detector on a locked site set. Require stable classes, rule-event recall, false alerts per camera-hour and offline reproducibility.

## Small VLM and video candidates

### Qwen3-VL-2B, 4B and 8B Instruct

Official Qwen sources describe Qwen3-VL as a multimodal family with image and video understanding, spatial grounding, OCR and timestamp-related video modeling. The official release includes 2B, 4B and 8B dense checkpoints, with Instruct and Thinking variants. Official repositories state Apache-2.0 for the Qwen3-VL project, but the exact checkpoint license and any dependency licenses must be captured in the model manifest before production.

**Why evaluate:** bounded evidence review, difficult action interpretation, evidence-grounded narrative, and selective video question answering. The 2B/4B variants are plausible workstation or edge-GPU review candidates; the 8B variant is a stronger cloud/workstation candidate.
**Why not assume it wins:** even small VLMs have vision-token, KV-cache, decode and generation cost; natural-language answers can be overconfident; video sampling and exact boundary localization require validation; the model card's general benchmarks do not establish CCTV compliance. Do not put it in the always-on critical path without an explicit latency and privacy result.
**Experiment:** compare all three on identical evidence packages with deterministic decoding, constrained JSON/citation output, and blinded labels. Measure grounded predicate accuracy, cited-frame coverage, latency, peak memory, privacy classification and cost.

### SmolVLM2-500M-Video and 2.2B

Hugging Face model cards describe 500M, 2.2B and 256M video-capable variants. The 500M card reports Apache-2.0 licensing and a vendor-reported 1.8GB GPU RAM requirement for video inference; its model card reports Video-MME, MLVU and MVBench results under the model's evaluation setup.

**Why evaluate:** low-memory advisory review or evidence summarisation; 500M is a useful lower-bound VLM candidate.
**Why not assume it wins:** the model card explicitly limits high-stakes/critical decision use; English-only limitations and small-model hallucination/visual omissions matter; benchmark results are not owner-rule results. Use it only as advisory and measure whether it adds value over structured overlays and captions.
**Experiment:** S3 review arm on selected ambiguous clips, with no policy authority and no personal scoring. Compare against Qwen3-VL-2B and no-VLM review.

## Candidate roles by deployment

| Candidate | CPU laptop | Integrated GPU/NPU | Edge GPU | Cloud GPU | Default role |
|---|---|---|---|---|---|
| YOLO26n | test candidate | test candidate | strong candidate | yes | closed-set perception arm |
| YOLOE-26n/s | discovery/low-rate only until measured | selective | selective | yes | open-vocabulary exploration and annotation |
| Qwen3-VL-2B | not assumed continuous | selective only | bounded review candidate | yes | advisory evidence review |
| Qwen3-VL-4B | not assumed | not default | bounded review candidate | yes | stronger advisory review |
| Qwen3-VL-8B | no | no | selective if memory permits | yes | cloud/workstation review |
| SmolVLM2-500M | offline/low-rate research only | candidate | low-memory advisory candidate | yes | lower-bound video review |
| SmolVLM2-2.2B | not assumed continuous | selective | bounded review candidate | yes | compact advisory review |

## Landscape conclusion

The refresh adds useful candidates but does not change the architecture. YOLO26/YOLOE-26 are perception candidates, not policy engines. Qwen3-VL and SmolVLM2 are bounded review candidates, not authoritative compliance decision makers. Their license and model-card restrictions are part of selection, not post-selection paperwork.
