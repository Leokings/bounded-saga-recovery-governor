# Bounded Saga Recovery Governor

A standalone, MIT-licensed GenLayer Intelligent Contract that turns a partially failed asynchronous workflow into one bounded, auditable recovery decision.

Distributed workflows routinely reach mixed states: inventory is reserved, payment is captured, but fulfillment fails. A conventional retry loop can observe status codes, yet it cannot safely interpret what the completed steps actually did. The controller first freezes one immutable context summary, then each pre-registered step reporter submits a bounded effect summary on-chain. Once every step has reported and the workflow contains both success and failure, GenLayer validators compare those observed effects against a closed catalog of recovery plans. Authenticated reports are the exclusive authoritative evidence; the controller summary cannot establish or override a fact.

The result is exactly one of:

- `PLAN_SELECTED` with one pre-registered `plan_id`;
- `MANUAL_HALT` when no safe plan is supported; or
- `AMBIGUOUS` when multiple plans remain plausible.

The contract deliberately **does not execute** the recovery plan. It never accepts an arbitrary target, method, calldata, transfer, or model-generated action. A consuming application may act on a finalized decision using its own deterministic authorization and replay controls.

## Why this needs GenLayer

Structural eligibility is deterministic: required successful steps, required failed steps, and forbidden successful steps are checked in contract code. The consensus-critical question is semantic and bounded:

> Do the authenticated observed effects clearly support exactly one eligible recovery plan?

The leader proposes a closed structured outcome. Validators independently audit the substance of that proposal against the same committed reports and recovery catalog. Only after consensus does the contract append an immutable decision and its digests.

This differs from an off-chain retry keeper. A keeper chooses and runs operational logic privately. This primitive records a shared validator-adjudicated recovery choice that other applications can inspect after finality.

## State model

```text
UNOPENED
   |
   | controller: open_workflow(reference)
   v
AWAITING_FAILURE_SUMMARY
   |
   | controller: freeze_failure_summary(reference, summary)
   v
REPORTING
   |
   | each registered step address: submit_step_report(...)
   | complete report set + at least one SUCCEEDED + at least one FAILED
   v
CONSENSUS ADJUDICATION
   |-- PLAN_SELECTED(plan_id)
   |-- MANUAL_HALT
   `-- AMBIGUOUS

All three outcomes are terminal for that request reference.
The controller may instead terminally mark an incomplete reference `ABANDONED`; an abandoned reference can never be reopened.
```

## Contract interface

### Constructor

```python
BoundedSagaRecoveryGovernor(
    workflow_id: str,
    workflow_version: str,
    step_catalog_json: str,
    recovery_catalog_json: str,
)
```

The controller is the deploying address. Configuration is canonicalized and immutable.

### Writes

```python
open_workflow(request_reference: str)

freeze_failure_summary(
    request_reference: str,
    failure_summary: str,
)

submit_step_report(
    request_reference: str,
    step_id: str,
    status: str,          # SUCCEEDED | FAILED | UNKNOWN
    effect_summary: str,
)

govern_recovery(
    request_reference: str,
) -> int

abandon_workflow(request_reference: str)
```

`open_workflow`, `freeze_failure_summary`, `govern_recovery`, and `abandon_workflow` are controller-only. The summary must be frozen before reporting begins and cannot be replaced after a failed adjudication attempt. `submit_step_report` authenticates `gl.message.sender_address` against that step's immutable reporter address.

Every step intentionally requires a different nonzero reporter address. This identity-isolation invariant prevents one address from batching several step assertions into one authority. If one operational service owns multiple steps, give each step a distinct reporting IC or key rather than weakening the invariant.

### Views

```python
get_policy() -> dict
is_open(request_reference: str) -> bool
get_workflow_status(request_reference: str) -> str
get_frozen_failure_summary(request_reference: str) -> dict
get_step_report(request_reference: str, step_id: str) -> dict
get_decision_count() -> int
get_decision_id(request_reference: str) -> int
get_decision(decision_id: int) -> dict
```

## Catalog schemas

Step catalog:

```json
[
  {
    "id": "CHARGE_PAYMENT",
    "description": "Authorize or capture the customer's payment.",
    "reporter": "0x1111111111111111111111111111111111111111"
  }
]
```

Recovery catalog:

```json
[
  {
    "id": "REFUND_AND_RELEASE",
    "description": "Refund captured funds and release reserved inventory.",
    "when_effects": "Payment was captured, inventory remains held, and fulfillment failed.",
    "required_succeeded_steps": ["RESERVE", "CHARGE"],
    "required_failed_steps": ["FULFILL"],
    "forbidden_succeeded_steps": []
  }
]
```

See [examples/step-catalog.json](examples/step-catalog.json), [examples/recovery-catalog.json](examples/recovery-catalog.json), and [examples/README.md](examples/README.md).

## Safety properties

- pinned production runner dependency;
- immutable, bounded step and plan catalogs;
- deployment-time worst-case and runtime UTF-8 prompt-byte budgets, with validator-audit sizing across every registered `PLAN_SELECTED` candidate plus `MANUAL_HALT` and `AMBIGUOUS`;
- raw and canonicalized LLM-response character and UTF-8-byte caps;
- controller-opened workflow instances prevent reporter-created storage spam;
- an immutable controller context summary frozen before any report;
- caller-authenticated, append-only step reports;
- complete report coverage and a deterministic partial-failure gate;
- deterministic plan eligibility before any LLM judgment;
- no model-generated plan identifiers, methods, targets, calldata, or payments;
- explicit `MANUAL_HALT` and `AMBIGUOUS` fail-closed outcomes;
- independent semantic validator audit rather than format-only validation;
- storage-free nondeterministic callbacks: immutable workflow context is copied into plain locals before consensus and evaluated by module-level helpers;
- length-framed domain-separated config, report, request, and decision digests;
- one terminal decision or abandonment per request reference;
- native value rejected on every write path.

Read [ARCHITECTURE.md](ARCHITECTURE.md) and [SECURITY.md](SECURITY.md) before integrating.

## Testing

```powershell
genvm-lint check contracts\BoundedSagaRecoveryGovernor.py
genvm-lint typecheck contracts\BoundedSagaRecoveryGovernor.py
pytest tests\direct -q

# Start a five-validator local simulator in another terminal:
python tests\run_glsim.py --port 4000 --validators 5 --no-browser
gltest tests\integration -v -s --network localnet
```

Version 0.2.1 is 37,980 bytes at SHA-256 `00050b640db0c2c944fdd7aeb2d70c1715eedd635272478314fa74ec0c9209a4`. It passes GenVM lint and type checking, 47 direct tests, and all three five-validator GLSim tests with explicit prompt-specific mocks. A no-mock StudioNet run deployed byte-identical v0.2.1 source at `0x61a4a6aa81FD35Eac057244F7Cc8fD01167ECdfF` and finalized `PLAN_SELECTED / REFUND_AND_RELEASE` by `MAJORITY_AGREE` with three agree and two disagree votes across three rounds. This is majority evidence, not unanimity.

Bradbury finalized a second byte-identical v0.2.1 deployment at `0xA2DDebc4CC8Eb21bb8eB45214Bfad1A4dE7A26Fd`. Its deterministic setup transactions executed successfully and were accepted, but neither semantic attempt produced an accepted decision: the first ended `VALIDATORS_TIMEOUT`, and the one authorized govern-only retry ended `NO_MAJORITY` with final-round counts of four `AGREE`, four `TIMEOUT`, and three `DETERMINISTIC_VIOLATION`. Durable latest-final reads showed `REPORTING`, zero decisions, and both reports intact. Public replay traces returned successfully with no runtime or storage warning, but recorded zero provider calls; Bradbury is therefore exact-deployment evidence, not positive semantic-decision evidence. The StudioNet record remains the positive current-source semantic proof.

The older StudioNet and Bradbury records under [deployments/](deployments/) were produced by superseded version 0.2.0 and are historical only. In particular, the v0.2.0 Bradbury deployment finalized successfully, but its semantic call failed closed before inference because bound contract methods indirectly read storage during nondeterministic execution. Version 0.2.1 removes those reads by passing plain local values to module-level helpers. The older addresses and receipts must not be presented as current-source deployment evidence. See [TESTING.md](TESTING.md) for the exact evidence boundary.

## Reuse

Copy the single contract file, replace the example catalogs with a closed workflow-specific catalog, assign each step its actual reporting address, and deploy. Do not weaken the bounded output schema or let recovery descriptions become executable instructions.

## License

[MIT](LICENSE)
