# Privacy, Security and Compliance Review Checklist

Technical feasibility does not establish legal or organisational permission. In this study, compliance means adherence to owner-defined operational policies only. Legal, regulatory, privacy, security, employment/HR and governance compliance are separate review domains. Before a pilot or production deployment, route this checklist to legal, privacy, security, compliance, HR and relevant operational owners.

## Purpose and necessity

- What specific risk or operational need does each camera/rule address?
- Why is CCTV/AI necessary compared with a sensor, process control or human check?
- Is the least intrusive perception signal selected? Is face recognition actually necessary?
- What is the expected harm from false positives, false negatives and missed events?

## People and transparency

- Who may be recorded, including visitors, employees, contractors and bystanders?
- What notice/transparency is required, and where is it displayed?
- Is employee monitoring involved? Has HR/works council/staff consultation been considered?
- Is any output used for discipline, access denial, safety dispatch or other consequential action?
- Is human review, contestability and correction available before high-impact action?

## Sensitive signals

- Are faces, voice, gait, body shape, clothing, badges, plates or appearance embeddings used?
- Does any component uniquely identify a person or infer sensitive behavior?
- If biometric identification is contemplated, has specialist review and a DPIA/risk assessment occurred?
- Is audio off by default unless an evidenced need and approval exist?

## Data lifecycle

- What is collected, derived, transmitted, stored, viewed and deleted?
- Is the continuous stream retained, or only a bounded ring buffer/evidence package?
- Are retention periods purpose-specific and technically enforced?
- Can a data subject/access request, correction or deletion be supported where applicable?
- Are backups, caches, logs and model-training copies included in deletion scope?

## Security

- Are camera credentials, model files, rule configurations and keys protected?
- Is evidence encrypted at rest/in transit with rotation and access logging?
- Are edge devices patched, signed, physically protected and remotely revocable?
- Are cloud processors/subprocessors, regions, data residency and cross-border transfer reviewed?
- Can operators view raw video, redacted evidence and metadata according to least privilege?
- Are prompts, VLM outputs and exported embeddings included in threat modeling?

## AI assurance

- Are model cards, licenses, training data provenance and known limitations recorded?
- Are performance and calibration measured across camera conditions and relevant groups?
- Are thresholds selected by rule-specific cost and reviewed after drift?
- Are model/config changes versioned, approved, rolled back and audited?
- Does the system degrade safely when data is missing or confidence is low?

## Technical controls to demonstrate

- local-first data flow and egress tests;
- deterministic rule replay;
- immutable evidence manifest and hash verification;
- camera health and data-gap alerts;
- operator review/audit trail;
- retention deletion test;
- incident response for model drift, breach, camera loss and false alert;
- red-team tests for adversarial appearance/occlusion and prompt injection if VLM is used.

The ICO CCTV guidance and NIST AI/Privacy Frameworks are references for questions, not substitutes for jurisdiction-specific advice.
