# Sources and Benchmark Conditions

Accessed/checked 2026-10-05. This is a curated technical source list, not a claim that every source is suitable for production licensing. Read licenses and model cards before use.

## SceneSolver repository evidence

| ID | Source | What it establishes | Limits |
|---|---|---|---|
| `R-SS-README` | [../README.md](../../README.md) | Describes staged AE -> TimeSformer binary/multiclass -> conditional YOLO -> audio -> tracking/behaviour -> fusion -> experimental RL/LLaVA -> report; says full notebooks expect GPU/checkpoints not stored. | Project documentation, not an independent benchmark. |
| `R-SS-TSB` | [Timesformer binary results](../../Timesformer/timesformer_binary_reslts.txt) | Test accuracy 0.9667 on support 30; per class precision/recall/F1. | Test composition, split lineage, camera/site independence, calibration, latency and hardware are not recorded in the file. |
| `R-SS-TSM` | [classification report](../../Timesformer/classification_report_TFM.json) | Seven class report, accuracy 0.842857, macro F1 0.823514, weighted F1 0.839174, total support 140. | Not the full 13 class UCF Crime task; conditions and independence are not fully recorded. |
| `R-SS-CONFIG` | [binary training config](../../Timesformer/training_config_binary_TFB.json) | Binary run records best_acc approximately 0.9556, batch size 1 and gradient accumulation 8. | No model size, device, data counts or latency. |

## Primary papers and runtime documentation

| ID | Source | Relevant use and conditions |
|---|---|---|
| `P-UCF` | Sultani, Chen and Shah, CVPR 2018 | Introduces UCF Crime: 128 hours, 1,900 long untrimmed surveillance videos, 13 anomaly categories plus normal. Benchmark/reference, not a site compliance dataset. |
| `P-TS` | TimeSformer paper and official repository | Divided space time attention video classification. Benchmark conditions must not be transferred to CCTV compliance. |
| `P-VideoMAE` | VideoMAE paper and official repository | Self supervised video representation learning. Useful for representation experiments, not a turnkey rule engine. |
| `P-ByteTrack` | Official ByteTrack repository | Detection association tracker. Reported MOT results depend on detector and benchmark. |
| `P-RTDETR` | Official RT-DETR repository | Transformer detector family. Compare real end to end deployment rather than assuming vendor FPS parity. |

## 2025 to 2026 model landscape

| ID | Source | Relevant use and conditions |
|---|---|---|
| `D-TAPNET` | [Google DeepMind TAPNet](https://github.com/google-deepmind/tapnet) | Official Tracking Any Point implementation containing TAPNext, TAPNext++, TAPIR, BootsTAPIR, TAPVid and TAPVid-3D evaluation code. |
| `D-TAPNEXT` | [TAPNet README](https://github.com/google-deepmind/tapnet/blob/main/README.md) | TAPNext is described as the latest TAP tracker, formulated as next token prediction. |
| `D-TAPNEXTPP` | [TAPNet repository](https://github.com/google-deepmind/tapnet) and current VOTSp2026 code | TAPNext++ adds long stable tracking, occlusion handling and redetection; current repository includes 512 by 512 VOTSp2026 material. |
| `D-COTRACKER3` | [Facebook CoTracker](https://github.com/facebookresearch/co-tracker) | Official CoTracker3 online and offline point tracking implementation and checkpoints. |
| `D-SPATIALTRACKER` | [SpatialTracker implementation](https://github.com/RR-2000/SpaTracker_Datagen) | CVPR 2024 3D point tracking reference; official implementation reports an RTX A6000 setup and about 22 GB GPU memory for dense tracking of around 10,000 points. |
| `D-SPATIALTRACKERV2` | [SpatialTrackerV2 project](https://github.com/Zarad0X/SpatialTrackerV2) | ICCV 2025 successor producing depth, camera poses and pixel wise 3D tracking. |
| `D-SAM3` | [Meta SAM3](https://github.com/facebookresearch/sam3) | Unified promptable segmentation for images and videos with text and visual prompts, open vocabulary concept segmentation, detection and tracking. Current repository includes SAM3.1. |
| `D-DINOV3` | [Meta DINOv3](https://github.com/facebookresearch/dinov3) | 2025 visual foundation model family with dense features, ViT and ConvNeXt variants, downstream adapters, and released evaluation/training code. |
| `D-QWEN3VL-REPO` | [Qwen3 VL](https://github.com/QwenLM/Qwen3-VL) | Current Qwen vision language family with dense and MoE models, image/video understanding, spatial capabilities and multiple model sizes. |
| `D-INTERNVL` | [OpenGVLab InternVL](https://github.com/OpenGVLab/InternVL) | Official InternVL family repository including InternVL3 and InternVL3.5 releases. |
| `D-NVILA` | [NVIDIA VILA](https://github.com/NVlabs/VILA) | NVIDIA VILA/NVILA family repository for efficient multimodal and video understanding. |
| `D-COSMOS3` | [NVIDIA Cosmos](https://github.com/NVIDIA/Cosmos) | Cosmos 3 is NVIDIA's current world model family for physical AI, including reasoner and generator surfaces and an Edge 4B tier. |
| `D-DA3` | [ByteDance Depth Anything 3](https://github.com/ByteDance-Seed/depth-anything-3) | 2025 visual geometry model supporting spatially consistent geometry from arbitrary visual inputs. |
| `D-YOLO26` | [Ultralytics YOLO26](https://github.com/ultralytics/ultralytics/blob/main/docs/en/models/yolo26.md) | 2026 real time detection family and task variants. Vendor benchmark conditions are separate from CCTV results. |
| `D-YOLOE26` | [Ultralytics YOLOE](https://github.com/ultralytics/ultralytics/blob/main/docs/en/models/yoloe.md) | 2026 open vocabulary detection and segmentation with text, visual and prompt free modes. |
| `D-YOLOWORLD` | [Tencent YOLO World](https://github.com/AILab-CVC/YOLO-World) | YOLO World V2.1 2025 update with zero shot and image prompt capabilities. Non Ultralytics reference. |

## Licensing sources

| ID | Source | Relevant use and conditions |
|---|---|---|
| `L-TAPNET` | [TAPNet LICENSE](https://github.com/google-deepmind/tapnet/blob/main/LICENSE) | Official repository states released TAP software and TAPNext related checkpoints are Apache 2.0. TAPVid-3D has separate terms. |
| `L-DINOV3` | [DINOv3 LICENSE](https://github.com/facebookresearch/dinov3) | DINOv3 code and weights use the DINOv3 License. It is a custom license and therefore requires explicit production review. |
| `L-SAM3` | [SAM3 LICENSE](https://github.com/facebookresearch/sam3/blob/main/LICENSE) | SAM3 uses the SAM License. Exact checkpoint and dataset terms must be recorded before deployment. |
| `L-COSMOS3` | [Cosmos license](https://github.com/NVIDIA/Cosmos) | NVIDIA states Cosmos source and models are released under OpenMDW 1.1, with custom licensing available from NVIDIA. |
| `L-DINOV3-ACCESS` | [DINOv3 model access discussion](https://github.com/facebookresearch/dinov3/issues/108) | Model access requires accepting the relevant license agreement and account review through the published distribution flow. |
| `L-QWEN3VL` | [Qwen3 VL repository](https://github.com/QwenLM/Qwen3-VL) | Repository is Apache 2.0. Exact checkpoint and dependency terms still require a manifest. |
| `L-INTERNVL` | [InternVL repository](https://github.com/OpenGVLab/InternVL) | Exact model and component licenses must be recorded per checkpoint and dependency. |
| `L-YOLOWORLD` | [YOLO World LICENSE](https://github.com/AILab-CVC/YOLO-World/blob/master/LICENSE) | Official repository identifies GPL v3. Commercial licensing considerations must be preserved. |

## Current license and deployment warnings

DINOv3 is not documented as Apache 2.0 in its official repository. It uses a custom DINOv3 License Agreement, and access to released weights is gated by acceptance of that agreement. Do not describe it as simply Apache licensed.

SAM3 is released under a custom SAM License and its official installation requires a CUDA compatible GPU with a current CUDA stack. It is therefore a research candidate, not an assumed edge baseline.

Cosmos 3 is not a CCTV detector. Its current official repository positions it as an omnimodal physical AI world model with Reasoner and Generator surfaces. The 2026 Cosmos3 Edge tier is nevertheless relevant to our simulation and edge feasibility questions.

## Citation discipline

Published FPS, AP or accuracy numbers must always be copied with model variant, input size, dataset/split, hardware, precision, batch/concurrency and whether preprocessing/postprocessing are included. If any are absent, record the number as non comparable and remeasure.

Arena measurements must be stored separately from all published numbers.
