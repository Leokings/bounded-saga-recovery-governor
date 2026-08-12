# Architecture

## Responsibility boundary

| Component | Owns |
|---|---|
| Application/controller | Opens workflow instances, freezes one bounded context summary before reporting, waits for finality, and deterministically decides whether to consume a result |
| Step reporters | Submit one caller-authenticated status and observed-effect summary for their configured step |
| GenLayer contract | Canonicalization, authorization, structural eligibility, semantic consensus, replay prevention, immutable decisions, and digests |
| Recovery executor | Any actual compensation, retry, refund, release, or downstream IC message; it is intentionally outside this contract |

The contract does not promise synchronous atomicity across Intelligent Contracts. GenLayer IC write messages are asynchronous. Reporting ICs **must** emit `submit_step_report` with `on="finalized"`, after the source effect itself is final. Accepted-state messages are unsafe here because an appeal can invalidate an already emitted message and immutable report replays are rejected. The governor cannot verify upstream finality on-chain; this is an integration requirement. A recovery consumer must act only on a finalized governor transaction.

## Deployment configuration

The constructor commits to:

- a workflow identifier and version;
- 2–12 closed step definitions;
- one unique, nonzero configured address per step;
- 1–12 recovery plans;
- deterministic structural conditions for every plan; and
- semantic `description` and `when_effects` text for bounded adjudication.

The canonical configuration and deployment domain produce `config_digest`.
The constructor also computes conservative worst-case leader and validator-audit prompts using maximum UTF-8-byte report and summary values. Audit sizing evaluates every registered plan as a possible `PLAN_SELECTED` candidate, plus `MANUAL_HALT` and `AMBIGUOUS`, and retains the largest encoded prompt. Deployments whose leader or exhaustive audit worst case exceeds `MAX_PROMPT_BYTES` are rejected before they can accept a reference.

## Workflow lifecycle

1. The controller calls `open_workflow(reference)`.
2. The controller separately calls `freeze_failure_summary(reference, summary)` and waits for that transaction to finalize. This must happen before any report; the frozen summary cannot change across retries.
3. Each configured reporter address calls `submit_step_report` once for its step and reference using a finalized message.
4. Reports are immutable. A caller cannot replace a status or effect summary.
5. The controller calls `govern_recovery(reference)` after every configured step has reported.
6. Deterministic code requires at least one `SUCCEEDED` and one `FAILED` report.
7. Deterministic code filters the recovery catalog using required/forbidden step statuses.
8. The leader semantically compares the authenticated observed effects with only those structurally eligible plans. The controller summary is non-evidentiary context and cannot override a report.
9. A validator independently audits the proposed substantive result under the same evidence hierarchy.
10. Consensus appends one terminal decision and binds it to report, summary, request, config, and decision digests.

Before a decision, the controller may call `abandon_workflow(reference)`. `ABANDONED` is terminal, rejects later reports/adjudication, and retains the ever-opened marker so the reference cannot be reused.

## Hybrid deterministic–semantic design

Deterministic code owns:

- input bounds and canonicalization;
- configuration-time and runtime UTF-8 prompt-byte budgets;
- raw and canonicalized LLM-response character and UTF-8-byte caps;
- exact caller authorization;
- immutable summary commitment before reports;
- report completeness and uniqueness;
- partial-failure classification;
- structural plan eligibility;
- closed status/reason/plan schemas;
- terminal decision/abandonment state and replay prevention; and
- all digest derivation.

GenLayer consensus owns only:

- whether the observed effects clearly match one eligible plan;
- whether no plan is safe; or
- whether multiple plans remain plausible.

This separation prevents the LLM from creating operational powers. Even a `PLAN_SELECTED` result is only an immutable plan identifier.

## Equivalence principle

The contract uses `gl.vm.run_nondet_unsafe` with a custom non-comparative validator:

- leader output is defensively parsed into four exact fields;
- raw and canonicalized leader/validator payloads must fit fixed character and UTF-8-byte caps;
- a selected `plan_id` must already be structurally eligible;
- a selected plan must cite every required successful and failed step;
- non-selection outcomes must use an empty `plan_id`;
- citations must be exact configured step IDs; and
- the validator re-evaluates substance and returns only `{"accept": true|false}`.

Validators do not accept a result merely because it is valid JSON.

## Digest construction

Digests are Keccak-256 over domain-separated, length-framed strings:

```text
CONFIG   = network + contract + controller + immutable catalogs + policy version
SUMMARY  = config digest + reference + frozen controller context summary
REPORTS  = config digest + canonical authenticated reports
REQUEST  = config digest + controller + reference + reports digest + summary digest
DECISION = config digest + ordinal + request digest + bounded result fields
```

Length framing prevents concatenation ambiguity. Contract address and chain ID prevent cross-deployment replay.

## Consumption pattern

A consumer should verify at minimum:

- expected governor address;
- expected `config_digest` and `policy_version`;
- expected request reference and request digest;
- expected frozen failure-summary digest;
- finalized transaction status;
- unused `decision_digest` or local nonce;
- `status == PLAN_SELECTED`; and
- `plan_id` belongs to its own hard-coded action map.

The consumer—not this governor—performs the action and handles retries or idempotency.
