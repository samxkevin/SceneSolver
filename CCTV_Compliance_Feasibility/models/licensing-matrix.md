# Model and Dependency Licensing Matrix

**Purpose:** make licensing a first-class model-selection gate. This is technical procurement/review material, not legal advice. The exact license attached to the code, checkpoint, fine-tuned weights, dataset, text encoder, runtime and distribution channel must be captured at the time of use.

| Candidate/family | Code/repository license evidence | Weights/model license evidence | Commercial/deployment concerns | Attribution/redistribution | Compatibility decision |
|---|---|---|---|---|---|
| Ultralytics YOLOv8/YOLO11/YOLO26 | Ultralytics documents community AGPL-3.0 and an Enterprise path | Ultralytics states trained YOLO models are covered by AGPL-3.0 by default, with Enterprise licensing available | Vendor states Enterprise is required for proprietary/internal, commercial, SaaS, embedded and private deployment where the project is not open-sourced under AGPL-3.0. Confirm exact terms with legal/vendor | Preserve AGPL notices if using that route; Enterprise contract may impose separate terms; record modifications and model provenance | Research evaluation is possible; production use is blocked pending license decision |
| YOLOE-26 | Same Ultralytics package and documentation family | Verify exact YOLOE-26 checkpoint terms, expected to follow Ultralytics licensing, before use | Text encoder, checkpoint and package dependencies must all be reviewed; offline deployment must include all assets | Preserve notices and any prompt/text-encoder license terms | Candidate only pending license manifest and approved deployment path |
| RT-DETR official implementation | Official `lyuwenyu/RT-DETR` repository labels Apache-2.0 | Check each pretrained checkpoint and upstream dataset/weights terms independently | Apache-2.0 is generally compatible with proprietary use, subject to notices, patent and third-party terms | Retain license and NOTICE, mark modifications where required | Licensing candidate, still subject to weight and dependency audit |
| ByteTrack | Official repository labels MIT | Tracker code is not a neural weight package, but detector/appearance dependencies have separate terms | MIT is permissive; no license decision should be inferred for a paired detector or re-identification encoder | Retain copyright and MIT text | Strong licensing candidate for association logic |
| TimeSformer | Official implementation is majority CC-BY-NC-4.0; parts have separate terms; Hugging Face checkpoint cards also identify non-commercial terms for relevant checkpoints | Check each checkpoint card and pretrained weight source | Non-commercial restriction is a production blocker for a proprietary/commercial compliance service unless separately cleared | Attribution and component notices required; do not assume an architecture name grants weight rights | Research comparison only until commercial clearance or a separately licensed reimplementation/weight is found |
| VideoMAE | Official MCG-NJU repository identifies majority CC-BY-NC-4.0, with Apache/MIT portions | Check MCG-NJU and Hugging Face checkpoint license separately | Non-commercial restriction can block commercial training/inference or redistribution; verify terms | Retain CC-BY-NC and third-party notices; track pretrained data terms | Research comparison only pending clearance |
| Qwen3-VL-2B/4B/8B | Official Qwen3-VL repository states Apache-2.0 for the project | Verify the exact model card's license file and any quantisation/adapter artifact before release | Apache-2.0 is a candidate for proprietary use, but model-specific terms, safety policy, dependencies, and jurisdictional review remain required | Retain Apache license, copyright and NOTICE; document base model, adapter and modifications | Promising licensing candidate for bounded review, pending exact manifest and legal review |
| SmolVLM2-500M/2.2B | Hugging Face model card and supporting code identify Apache-2.0 for checkpoints | Exact checkpoint card states Apache-2.0 | Model card has high-stakes and critical-decision limitations; licence permissiveness does not remove those use restrictions or privacy duties | Retain Apache notices and base-model attribution; audit SigLIP/SmolLM2 terms | Candidate for advisory review only, not automatic high-impact decisions |
| Hugging Face Transformers/runtime | Official repository labels Apache-2.0 | Runtime is separate from every checkpoint | Check CUDA, flash-attention, tokenizer, video decoder and quantisation dependency licenses | Retain notices and dependency inventory | Usually compatible, but dependency SBOM required |
| Existing SceneSolver `ultralytics` usage | Existing code/notebooks use Ultralytics; repository is MIT but dependency license is separate | Existing `yolov8n.pt`/custom weights require provenance audit | SceneSolver's repository license does not grant a commercial license for third-party YOLO assets | Add a dependency and weights manifest before reuse | Do not treat existing repository MIT license as clearance |

## Required license manifest per candidate

```yaml
candidate_id: exact-model-and-revision
code_repository: url-and-commit
code_license: SPDX-or-custom-name
weights_url: url-and-revision
weights_license: SPDX-or-custom-name
training_data_license: known-or-unknown
runtime_dependencies:
  - name: exact-version
    license: SPDX-or-custom-name
commercial_use: approved|conditional|blocked|unknown
redistribution: approved|conditional|blocked|unknown
attribution_required: true
notice_files: []
model_card_restrictions: []
patent_or_trademark_notes: []
legal_review_reference: null
```

## Selection rule

A candidate cannot enter a production shortlist until the license manifest is complete, the deployment mode is compatible, required notices/attribution are implementable, and legal/security review has accepted the residual risk. A higher measured score does not override a blocked license.
