# Portal submission draft

Current-source v0.2.1 evidence is captured below. StudioNet and Bradbury both supply finalized positive semantic-consensus results; the Bradbury proof also preserves three earlier failed-closed attempts.

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
Built an MIT-licensed Bounded Saga Recovery Governor for partially failed workflows. Registered step addresses submit authenticated statuses and bounded effects; reports, not controller prose, are authoritative. Deterministic code requires mixed success/failure and filters a closed recovery catalog before consensus returns PLAN_SELECTED, MANUAL_HALT, or AMBIGUOUS. It never executes callbacks, transfers, or model-generated actions. v0.2.1 adds storage-free callbacks, immutable reports, replay protection, abandonment, digests, prompt budgets, and capped responses. It passes GenVM checks, 47 direct tests, and 3 five-validator mocked GLSim tests. Byte-identical source passed no-mock StudioNet and finalized on Bradbury at 0xA2DDebc4CC8Eb21bb8eB45214Bfad1A4dE7A26Fd. After three disclosed nonaccepted attempts using underspecified evidence, a new explicit-evidence workflow finalized 4/5 AGREE and durably selected REFUND_CAPTURED_PAYMENT with UNIQUE_RECOVERY_MATCH.
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

### GitHub File - finalized Bradbury deployment and semantic-smoke proof

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
- Describe Bradbury as a finalized exact deployment plus a successful explicit-evidence semantic workflow, while retaining the three prior failed-closed attempts.
- Do not claim unanimity for the Bradbury governance decision: it received four `AGREE` and one rejecting vote.
- Do not claim exact model identities or per-validator provider calls.
- Do not use any v0.2.0 address or proof as current-source evidence.
- Do not claim model identities or general heterogeneous-model accuracy from the submission text.
- Do not claim the governor itself executes recovery actions.

## Historical evidence boundary

The retained v0.2.0 StudioNet success, StudioNet negative run, and Bradbury deployment/failed semantic record are superseded regression evidence only. They remain inspectable in the repository but should not be added as Portal evidence for v0.2.1.
