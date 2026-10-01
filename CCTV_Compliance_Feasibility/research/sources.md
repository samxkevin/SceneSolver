# Sources and Benchmark Conditions

Accessed/checked 2026-10-01. This is a curated technical source list, not a claim that every source is suitable for production licensing. Read licenses and model cards before use.

## SceneSolver repository evidence

| ID | Source | What it establishes | Limits |
|---|---|---|---|
| `R-SS-README` | [`../README.md`](../../README.md) | Describes staged AE -> TimeSformer binary/multiclass -> conditional YOLO -> audio -> tracking/behaviour -> fusion -> experimental RL/LLaVA -> report; says full notebooks expect GPU/checkpoints not stored. | Project documentation, not an independent benchmark. |
| `R-SS-TSB` | [`../../Timesformer/timesformer_binary_reslts.txt`](../../Timesformer/timesformer_binary_reslts.txt) | Test accuracy 0.9667 on support 30; per-class precision/recall/F1. | Test composition, split lineage, camera/site independence, calibration, latency and hardware are not recorded in the file. |
| `R-SS-TSM` | [`../../Timesformer/classification_report_TFM.json`](../../Timesformer/classification_report_TFM.json) | Seven-class report, accuracy 0.842857, macro F1 0.823514, weighted F1 0.839174, total support 140. | Not the full 13-class UCF-Crime task; conditions and independence are not fully recorded. |
| `R-SS-CONFIG` | [`../../Timesformer/training_config_binary_TFB.json`](../../Timesformer/training_config_binary_TFB.json) | Binary run records best_acc ≈0.9556, batch size 1 and grad accumulation 8. | No model size, device, data counts or latency. |
| `R-SS-INSIGHTS` | [`../../Insights.md`](../../Insights.md) | Documents 16–32 frame sampling, CLIP semantic curve, temporal windows, and non-destructive DatasetTools principles. | Design notes are not proof of deployment performance. |
| `R-SS-REPORT` | [`../../ReportGeneration/InferenceResults/results/cctv_analysis_results/analysis.json`](../../ReportGeneration/InferenceResults/results/cctv_analysis_results/analysis.json) | Sample report processed 320x240, 30 FPS, 3,366 frames/112.2 sec and emitted captions/labels/evidence paths. | It is a sample output with no labelled ground truth or alert-quality metric; caption anomalies are not a validated compliance detector. |
| `R-SS-AUDIO` | [`../../SpectrogramAnalysis/results/training_history.json`](../../SpectrogramAnalysis/results/training_history.json) | Audio CAE history includes 35 train epochs and best validation loss 0.020269. | Reconstruction loss is not event accuracy or an operating threshold. |
| `R-SS-CLIP` | [`../../UnrefinedCoreFuntionality/ExplorationsInCLIP/outputs/Abuse028_x264.json`](../../UnrefinedCoreFuntionality/ExplorationsInCLIP/outputs/Abuse028_x264.json) | Example prompt/keyframe anomaly curve and temporal candidate windows. | Candidate spikes are not owner-rule labels; prompt score calibration is unknown. |

## Primary papers and official runtime documentation

| ID | Source | Relevant use and conditions |
|---|---|---|
| `P-UCF` | [Sultani, Chen & Shah, CVPR 2018](https://openaccess.thecvf.com/content_cvpr_2018/papers/Sultani_Real-World_Anomaly_Detection_CVPR_2018_paper.pdf) | Introduces UCF-Crime: 128 hours, 1,900 long untrimmed surveillance videos, 13 anomaly categories plus normal; weakly labelled anomaly localization setting. This is a benchmark/reference, not a site-compliance dataset. |
| `P-TS` | [TimeSformer paper](https://arxiv.org/pdf/2102.05095) | Divided space-time attention video classification; paper reports model parameter counts and Kinetics/Something-Something conditions. Do not transfer its benchmark accuracy to CCTV compliance. |
| `P-VideoMAE` | [VideoMAE, NeurIPS 2022](https://proceedings.neurips.cc/paper_files/paper/2022/file/416f9cb3276121c42eebb86352a4354a-Paper-Conference.pdf) and [official code](https://github.com/MCG-NJU/VideoMAE) | Self-supervised video representation learning with tube masking; useful for pretraining/representation experiments, not a turnkey real-time rule engine. |
| `P-ByteTrack` | [Official ByteTrack repository/paper link](https://github.com/FoundationVision/ByteTrack) | Associates high- and low-score detection boxes to reduce missed/fragmented tracks; reported MOT results depend on detector and benchmark. Evaluate on target cameras. |
| `P-RTDETR` | [Official RT-DETR implementation](https://github.com/lyuwenyu/RT-DETR) and [Ultralytics reference](https://docs.ultralytics.com/models/rtdetr) | Transformer detector family with real-time claims under paper/vendor benchmark conditions; compare to small detector exports rather than assuming parity. |
| `D-ULTRA-EXPORT` | [Ultralytics export documentation](https://docs.ultralytics.com/modes/export) | Documents ONNX, OpenVINO, TensorRT and quantisation/export options. Vendor speedup claims require target-hardware reproduction. |
| `D-OPENVINO-SYS` | [OpenVINO system requirements](https://docs.openvino.ai/systemrequirements) | Documents supported CPU/GPU/NPU classes and driver requirements. Support does not guarantee operator coverage or target FPS. |
| `D-OPENVINO-Q` | [OpenVINO basic quantization flow](https://docs.openvino.ai/2025/openvino-workflow/model-optimization-guide/quantizing-models-post-training/basic-quantization-flow.html) | INT8 calibration workflow and target-device options; calibration data must represent the deployment domain. |
| `D-ORT-Q` | [ONNX Runtime quantization](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html) | Documents dynamic/static quantisation, QOperator/QDQ, and the general guidance that dynamic often fits transformers while static often fits CNNs. Validate exact graph/provider. |
| `D-JETSON` | [NVIDIA Jetson Orin Nano user guide](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/index.html) | Current guide lists up to 67 INT8 TOPS, 8GB and 7–25W for Orin Nano Super; theoretical AI throughput is not application FPS or available memory. |
| `D-INTEL` | [Intel Core Ultra edge brief](https://www.intel.com/content/dam/www/central-libraries/us/en/documents/2024-12/edge-intel-core-ultra-processor-series-2-h-u-sku-product-brief.pdf) and [OpenVINO requirements](https://docs.openvino.ai/systemrequirements) | Integrated CPU/GPU/NPU deployment context; vendor “up to” numbers require exact SKU/software/thermal test. |
| `P-LLaVA` | [LLaVA-1.5 model card](https://huggingface.co/llava-hf/llava-1.5-13b-hf), [LLaVA-NeXT-Video card](https://huggingface.co/lmms-lab/LLaVA-NeXT-Video-7B) | Model-card details show 13B/7B-class multimodal models and their intended usage; model cards and licenses matter. Use only as optional review candidates. |

## Privacy and governance references

| ID | Source | Use |
|---|---|---|
| `G-NIST-AI` | [NIST AI RMF 1.0](https://www.nist.gov/itl/ai-risk-management-framework) | Organises governance, mapping, measurement and management; use to separate technical evidence from legal/compliance decisions. |
| `G-NIST-PRIV` | [NIST Privacy Framework 1.0](https://www.nist.gov/privacy-framework) | Privacy risk management, data lifecycle, disassociated processing, minimisation and protection controls. |
| `G-NIST-FR` | [NIST/OSAC passive live facial recognition guidance](https://www.nist.gov/adlp/spo/organization-scientific-area-committees-forensic-science/framework-implementing-passive-0) | Illustrates privacy-by-design and human-review considerations for biometric systems; not a legal determination for this project. |
| `G-ICO` | [ICO video surveillance guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/cctv-and-video-surveillance/) | A jurisdiction-specific governance reference about surveillance, DPIA, retention, audio and biometrics. Consult the organisation's legal/privacy teams for applicable law. |

## Citation discipline

Published FPS/AP/accuracy numbers must always be copied with model variant, input size, dataset/split, hardware, precision, batch/concurrency and whether preprocessing/postprocessing are included. If any are absent, record the number as non-comparable and remeasure.
