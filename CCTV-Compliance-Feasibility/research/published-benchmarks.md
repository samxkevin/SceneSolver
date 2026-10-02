# Published Benchmark Context (Not Deployment Claims)

Published results are included to understand capability and cost tradeoffs. They are not portable performance promises for CCTV. The benchmark task, data, sampling, resolution, hardware, precision and pipeline accounting must match before comparison.

| Family | Published result/context | What it supports | What it does not support |
|---|---|---|---|
| TimeSformer | The paper reports divided-space-time TimeSformer at 121.4M parameters, 78.0 top-1 on Kinetics-400 and 59.5 on Something-Something V2 in its reported evaluation table. It discusses multi-view inference and video-classification benchmarks. Source: [paper](https://arxiv.org/pdf/2102.05095). | Shows that space-time attention is a credible video-classification research baseline. | Does not establish CPU streaming, CCTV domain generalisation, exact boundary timing or owner-rule recall. |
| UCF-Crime / MIL anomaly setting | Sultani et al. introduce 128 hours, 1,900 long untrimmed videos, 13 anomaly categories plus normal activities and a weakly labelled anomaly-localisation setting. Source: [CVF paper](https://openaccess.thecvf.com/content_cvpr_2018/papers/Sultani_Real-World_Anomaly_Detection_CVPR_2018_paper.pdf). | Provides historical surveillance anomaly benchmark context and a dataset family used by SceneSolver. | Anomaly categories are not configurable owner rules; internet surveillance footage is not a site acceptance set. |
| VideoMAE | The paper reports self-supervised video pretraining findings including high tube-masking ratios and benchmark results under Kinetics-400, Something-Something V2, UCF101 and HMDB51 settings. Source: [NeurIPS paper](https://proceedings.neurips.cc/paper_files/paper/2022/file/416f9cb3276121c42eebb86352a4354a-Paper-Conference.pdf). | Supports testing self-supervised representation learning when labelled site video is scarce. | Does not imply a small, real-time, quantised compliance model; fine-tuning and target-domain evaluation remain required. |
| RT-DETR | The official implementation README reports RT-DETR-L 53.0 AP at 114 FPS on a T4 and RT-DETR-X 54.8 AP at 74 FPS under the authors' COCO/T4 benchmark context; it also reports an R50 variant. Source: [official implementation](https://github.com/lyuwenyu/RT-DETR). | Gives a detector comparison point and demonstrates that transformer detectors can be real-time under a specified GPU setup. | A T4 single-model benchmark is not CPU/edge capacity; AP is not recall for a custom CCTV class; preprocessing/postprocessing and concurrency may differ. |
| ByteTrack | The official repository describes association of low-score boxes and reports benchmark-specific MOT results/IDF1 improvements. Source: [official repository](https://github.com/FoundationVision/ByteTrack). | Justifies a simple tracker candidate that may preserve occluded tracks better than discarding low-score detections. | Tracker quality depends on detector, threshold, frame interval, camera density and target rule. Must measure zone/dwell outcomes. |
| OpenVINO / ONNX Runtime | Official deployment documentation describes export/runtime and INT8 calibration flows; it does not promise one speedup across models/devices. Sources: [OpenVINO quantisation](https://docs.openvino.ai/2025/openvino-workflow/model-optimization-guide/quantizing-models-post-training/basic-quantization-flow.html), [ONNX Runtime quantisation](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html). | Supports an empirical export/quantisation workstream. | Runtime support is not equivalent to operator coverage, accelerator execution, or lower end-to-end alert latency. |

## Reporting rule

When a future experiment quotes a published number, append:

```text
paper/source, model variant, task/dataset/split, input size/frames/views,
hardware, precision, batch/concurrency, whether decode/pre/postprocessing are included,
and whether the result is reproduced here.
```

If any field is unavailable, label the result `non-comparable` rather than putting it in a ranking table.
