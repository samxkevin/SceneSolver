# Meaning of Compliance in This Study

## Operational definition

In this technical study, **compliance means adherence to an owner-defined operational policy**. A policy is a versioned rule describing an expected state, action, sequence, permission, timing or exception for a defined camera/site context.

Examples:

- a gate remains closed outside an approved schedule;
- a person without an active authorization token remains in a restricted zone for longer than the policy permits;
- a required operational action is completed before its deadline;
- an object is not left in a prohibited zone beyond the allowed dwell time.

The system therefore produces an operational policy decision such as `rule R confirmed`, `rule R not satisfied`, or `unable to verify`, with evidence and provenance.

## What this does not mean

The technical result is not by itself:

- legal or regulatory compliance;
- privacy compliance;
- employment or HR compliance;
- proof of misconduct or intent;
- biometric identity proof;
- a lawful basis for surveillance;
- an automatic basis for discipline, denial of access or other high-impact action.

Those questions require the organisation's legal, privacy, security, compliance and HR review. A technically correct rule evaluation can still be inappropriate to deploy or act upon.

## Consequences for architecture

- The rule engine evaluates owner policy, not law.
- A VLM cannot turn a policy result into a legal conclusion.
- Human review and appeal are policy controls, not model confidence thresholds.
- The report must label operational violations separately from governance review status.
- Rule metadata should include policy owner, purpose, scope, version, severity and approved action.
