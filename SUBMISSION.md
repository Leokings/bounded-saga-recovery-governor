# Portal submission draft

Current-source StudioNet evidence is captured below. Replace GitHub and Bradbury placeholders only with frozen-source evidence before submission; Bradbury is not yet claimed.

## Title

```text
Bounded Saga Recovery Governor — Reusable Intelligent Contract
```

## Notes / Description

```text
Built an MIT-licensed Bounded Saga Recovery Governor for partially failed asynchronous workflows. Registered step addresses commit authenticated statuses and bounded effects; those reports, not controller prose, are authoritative. Deterministic code requires a mixed success/failure state and filters a closed recovery catalog before GenLayer consensus returns only PLAN_SELECTED, MANUAL_HALT, or AMBIGUOUS. The contract never executes callbacks, transfers, or model-generated actions. It includes immutable reports, replay protection, terminal abandonment, digest-linked decisions, deployment/runtime prompt budgets, capped LLM responses, 46 direct tests, and 3 five-validator mocked GLSim tests. A no-mock StudioNet run deployed byte-identical source at 0x63b9443113dD49213761aC6785FCD43268A8e3Af and finalized REFUND_AND_RELEASE by MAJORITY_AGREE with 3 agree and 2 disagree votes. A prior contradictory-evidence run is retained as negative MAJORITY_DISAGREE evidence.
```

## Evidence entries

### GitHub Repository

```text
<PRIVATE_REPOSITORY_URL_PENDING_PUBLICATION>
```

### GitHub File — exact contract source

```text
<CURRENT_SOURCE_PUBLIC_REPOSITORY_URL_PENDING>/blob/main/contracts/BoundedSagaRecoveryGovernor.py
```

### GitHub File — architecture and consensus design

```text
<CURRENT_SOURCE_PUBLIC_REPOSITORY_URL_PENDING>/blob/main/ARCHITECTURE.md
```

### GitHub File — security audit

```text
<CURRENT_SOURCE_PUBLIC_REPOSITORY_URL_PENDING>/blob/main/SECURITY_AUDIT.md
```

### GenLayer StudioNet Contract Address

```text
0x63b9443113dD49213761aC6785FCD43268A8e3Af
```

### GenLayer Explorer Contract — Bradbury

```text
<CURRENT_SOURCE_BRADBURY_EXPLORER_URL_PENDING>
```

### GitHub File — finalized StudioNet deployment proof

```text
<CURRENT_SOURCE_PUBLIC_REPOSITORY_URL_PENDING>/blob/main/deployments/studionet-2026-08-12-current-proof.json
```

### GitHub File — retained negative StudioNet evidence

```text
<CURRENT_SOURCE_PUBLIC_REPOSITORY_URL_PENDING>/blob/main/deployments/studionet-2026-08-12-no-majority.json
```

## Category

```text
Intelligent Contracts
```

## Pre-submission truth check

- Make the repository public only when ready to submit.
- Replace every placeholder.
- Confirm the explorer contract source hash matches the repository source.
- Change test counts only from fresh captured output.
- The current StudioNet result is majority agreement (3/2), not unanimity.
- Add finalized Bradbury evidence before claiming Bradbury.
- Do not claim model identities or general heterogeneous-model accuracy from the submission text.
- Do not claim the governor itself executes recovery actions.
