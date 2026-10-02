# Edge, Cloud, Hybrid and Privacy Boundary

## Data classes

| Data | Privacy/security posture | Default handling |
|---|---|---|
| Continuous raw video | highly revealing; can identify people, activities and context | keep on camera/site; short encrypted ring buffer; strict access |
| Sampled raw frames | still personal data; lower volume is not anonymous | local by default; export only by rule/policy |
| Cropped person/object frames | may identify through face, clothing, body or context | same as image; redact where possible and validated |
| Short evidence clip | high value and high risk; contains surrounding people | local encrypted retention; event-based export only |
| Event metadata | can reveal movements, roles and behavior even without images | minimize fields, pseudonymise, encrypt, retain by purpose |
| Track IDs/trajectories | not a person identity but linkable behavior | camera-local scope; short retention; no casual cross-camera join |
| Embeddings/appearance features | can be linkable or invertible/abusable; not automatically anonymous | treat as sensitive derived data; avoid egress by default |
| Reports/narratives | may reproduce personal/contextual information and model errors | redact/minimize; access-control and retention |
| Audio/spectrograms | may contain speech and sensitive context | disabled unless justified; local processing preferred |

## Edge-only

```text
CCTV -> local decode/inference/state/rules -> local evidence and alert
```

**Advantages:** raw video does not cross the site boundary; low network dependency; deterministic decisions continue during WAN outage; smaller egress surface.
**Costs:** hardware fleet management, local storage/security, limited model capacity, on-site updates and monitoring.

Minimum controls: signed software/configuration, encrypted local storage, secure boot where available, least privilege, local audit logs, key rotation, retention enforcement, operator access review, camera health and model drift monitoring.

## Cloud-only

```text
CCTV -> encrypted transport -> cloud decode/inference/rule/evidence
```

**Advantages:** central scaling, larger models, fleet analytics and easier updates.
**Costs:** continuous data movement, cloud/provider/subprocessor exposure, WAN latency/outage, egress/storage cost, residency/cross-border questions and wider breach impact.

Cloud-only should be an explicit policy choice, not the default because a VLM is convenient.

## Hybrid recommended boundary

```text
CCTV -> site edge perception + tracking + rule engine
       -> local evidence and alert
       -> policy gateway
          {metadata only | redacted frames | selected clip | no export}
       -> cloud review/training/analytics where approved
```

The edge should normally retain:

- raw stream access and short ring buffer;
- local event evaluation and health state;
- the minimum evidence required to operate;
- local keys and camera credentials;
- identity/authorization joins where possible.

The cloud may receive, per rule/policy:

- aggregate health and counts;
- pseudonymous event metadata;
- redacted keyframes;
- selected short evidence clip;
- no raw data for rules that can be resolved locally.

## Policy gateway requirements

- deny-by-default egress policy per data class, camera and rule;
- explicit purpose, recipient, region, retention and deletion metadata;
- redaction before encryption/export and a record of redaction version;
- mutual authentication, encryption in transit and at rest;
- queue/ retry without blocking local rule evaluation;
- DLP/content checks and audit record of every disclosure;
- provider/model data-use terms and no-training settings reviewed by security/legal;
- export approval for high-impact/biometric candidate content.

## Privacy engineering questions

“Metadata only” may still expose a person's routine. A pseudonymous track can become identifying when joined to schedules or access records. Embeddings can support linkage or reconstruction. Redaction can fail under blur/occlusion. Therefore classify privacy risk by inference and linkage, not file type alone.

Use NIST Privacy Framework concepts (data lifecycle, disassociated processing, selective disclosure) as a design vocabulary. This is not legal advice; the organisation must define lawful basis, notice/consent, retention, rights and jurisdictional controls.
