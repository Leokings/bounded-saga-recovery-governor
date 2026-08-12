# Portal submission draft

Current-source v0.2.1 evidence is captured below. StudioNet supplies the positive semantic-consensus result. Bradbury supplies a finalized byte-identical deployment, while its semantic retry ended `NO_MAJORITY` and persisted no decision.

## Contribution Date

```text
08/12/2026
```

## Title

```text
Bounded Saga Recovery Governor - Reusable Intelligent Contract
```

## Notes / Description

```text
Built an MIT-licensed Bounded Saga Recovery Governor for partially failed workflows. Registered step addresses submit authenticated statuses and bounded effects; reports, not controller prose, are authoritative. Code requires mixed success/failure and filters a closed recovery catalog before consensus returns PLAN_SELECTED, MANUAL_HALT, or AMBIGUOUS. It never executes callbacks, transfers, or model-generated actions. v0.2.1 uses storage-free callbacks, immutable reports, replay protection, abandonment, digests, prompt budgets, and capped responses. It passes GenVM checks, 47 direct tests, and 3 five-validator mocked GLSim tests. A no-mock StudioNet run deployed byte-identical source at 0x61a4a6aa81FD35Eac057244F7Cc8fD01167ECdfF and finalized REFUND_AND_RELEASE by MAJORITY_AGREE: 3 agree, 2 disagree, 3 rounds. Bradbury finalized another byte-identical deployment at 0xA2DDebc4CC8Eb21bb8eB45214Bfad1A4dE7A26Fd; its semantic retry ended NO_MAJORITY and persisted no decision.
```

## Evidence entries

### GitHub Repository

```text
https://github.com/Leokings/bounded-saga-recovery-governor
```

### GitHub File - exact contract source

```text
https://github.com/Leokings/bounded-saga-recovery-governor/blob/main/contracts/BoundedSagaRecoveryGovernor.py
```

### GitHub File - architecture and consensus design

```text
https://github.com/Leokings/bounded-saga-recovery-governor/blob/main/ARCHITECTURE.md
```

### GitHub File - security audit

```text
https://github.com/Leokings/bounded-saga-recovery-governor/blob/main/SECURITY_AUDIT.md
```

### GenLayer StudioNet Contract Address

```text
0x61a4a6aa81FD35Eac057244F7Cc8fD01167ECdfF
```

### GenLayer Explorer Contract - Bradbury

```text
https://explorer-bradbury.genlayer.com/address/0xA2DDebc4CC8Eb21bb8eB45214Bfad1A4dE7A26Fd
```

### GitHub File - finalized StudioNet deployment proof

```text
https://github.com/Leokings/bounded-saga-recovery-governor/blob/main/deployments/studionet-2026-08-12-v0.2.1-proof.json
```

### GitHub File - Bradbury deployment and nonaccepted semantic-smoke proof

```text
https://github.com/Leokings/bounded-saga-recovery-governor/blob/main/deployments/bradbury-2026-08-12-v0.2.1-deployment-and-smoke.json
```

## Category

```text
Intelligent Contracts
```

## Pre-submission truth check

- Make the repository public only when ready to submit.
- Confirm the explorer contract source hash matches the repository source.
- Change test counts only from fresh captured output.
- The current StudioNet result is majority agreement (3/2), not unanimity.
- Describe Bradbury only as a finalized exact deployment plus a nonaccepted semantic smoke; do not claim a successful Bradbury decision or independently established live LLM calls.
- Do not use any v0.2.0 address or proof as current-source evidence.
- Do not claim model identities or general heterogeneous-model accuracy from the submission text.
- Do not claim the governor itself executes recovery actions.

## Historical evidence boundary

The retained v0.2.0 StudioNet success, StudioNet negative run, and Bradbury deployment/failed semantic record are superseded regression evidence only. They remain inspectable in the repository but should not be added as Portal evidence for v0.2.1.
