# Security Audit Record

Date: 2026-08-12  
Scope: `contracts/BoundedSagaRecoveryGovernor.py` and its direct/integration tests  
Status: v0.2.1 local audit, StudioNet validation, and finalized Bradbury semantic-smoke review complete

## Method

- manual architecture and trust-boundary review;
- storage, access-control, replay, and state-machine review;
- nondeterministic leader/validator and output-parser review;
- prompt-injection and fail-closed review;
- GenVM lint and SDK semantic validation;
- Pyright typecheck;
- direct negative/adversarial tests, including an AST guard against callback storage capture; and
- five-validator GLSim consensus tests.

## Findings fixed during implementation

| Severity | Finding | Resolution |
|---|---|---|
| High | A controller-supplied reporter label would not authenticate the source of a step effect | Replaced with separate `submit_step_report` calls authenticated by `gl.message.sender_address` against immutable per-step addresses |
| High | Bound contract methods used as nondeterministic callbacks indirectly read `self.workflow_id`; Bradbury v0.2.0 therefore failed before inference because GenVM forbids contract-storage reads in nondeterministic mode | Version 0.2.1 copies the immutable workflow ID into a plain local before consensus, uses storage-free module-level leader/validator helpers, and adds an AST regression test proving neither callback captures `self` |
| Medium | Authorized reporters could create unlimited unopened request-reference storage | Added controller-only `open_workflow`; reports for unopened references fail before storage mutation |
| Medium | A semantic model could otherwise select a plan whose deterministic status prerequisites do not hold | Only structurally eligible plans enter the prompt; returned plan IDs are checked against that filtered set |
| Medium | Individually valid catalogs and reports could exceed the prompt ceiling and strand an immutable reference | Added UTF-8 byte limits, conservative constructor-time worst-case leader/audit budgets, stored budget evidence, and runtime prompt checks |
| Medium | A controller could alter its failure narrative across failed adjudication retries or use it to override authenticated reports | Added a separate immutable pre-report summary freeze, summary digest, and an explicit reports-only evidence hierarchy in leader and validator prompts |
| Medium | The documented StudioNet command still injected mock validators and canned answers | Split prompt-specific GLSim tests from an opt-in no-mock hosted test file |
| Medium | The unauthorized-persistence integration test caught its own failed assertion | Replaced the vacuous try/except with an external `pytest.raises` assertion and reran the five-validator suite |
| Medium | Accepted-state IC reports could survive an upstream appeal and poison an immutable reference | Integration documentation now requires source finality and `emit(on="finalized")` for reporting ICs |
| Medium | Zero or malformed reporter addresses could create an unusable immutable deployment or an unclassified parse error | Added exact hexadecimal prevalidation, deterministic expected errors, and zero-address rejection |
| Low | `is_open` stayed true after a terminal decision | Added explicit closed workflow states and derives openness from nonterminal states only |
| Low | A selected plan could cite a known but irrelevant step | Selected plans must cite every deterministic successful/failed prerequisite |
| Low | Incomplete workflows had no terminal close path | Added controller-only `ABANDONED`, retained the ever-opened marker, and prohibited reopening |
| Low | Bounds measured code points rather than encoded payload size | Semantic fields, JSON payloads, reports, and prompts now enforce UTF-8 byte limits |
| Medium | Returning SDK `Address` objects in generic dictionaries was not portable through GLSim view serialization | Public views now return canonical lowercase address strings |
| Low | Incrementing an absent `TreeMap` counter raised instead of using an implicit zero | Added explicit first-write initialization |
| Low | Raw or parsed LLM output could exceed the intended bounded-result envelope before strict schema validation | Added character and UTF-8-byte caps to raw strings and canonicalized JSON objects on both leader and validator paths |
| Medium | Constructor audit budgeting could understate the maximum validator prompt when a different registered plan or non-selection outcome serialized larger than the sampled candidate | Exhaustive deployment-time sizing now evaluates every registered `PLAN_SELECTED` candidate plus `MANUAL_HALT` and `AMBIGUOUS`, retaining the largest UTF-8 prompt size |

## Open severity findings

| Critical | High | Medium | Low |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 |

Remediated finding groups: 18 total (2 High, 10 Medium, 6 Low).

The documented trust assumptions in `SECURITY.md` are product boundaries, not fixed vulnerabilities: reporters attest to effects, validators can share correlated errors, catalog quality matters, and plan execution remains external.

## Verification snapshot

Update only from captured command output:

```text
genvm-lint check: PASS
genvm-lint typecheck: PASS
pytest direct: 47 passed
five-validator GLSim for current source: PASSED 3/3 with five explicit mock validators
StudioNet v0.2.1: PASSED no-mock hosted smoke; exact source at 0x61a4a6aa81FD35Eac057244F7Cc8fD01167ECdfF; MAJORITY_AGREE 3/2 across three rounds
Bradbury v0.2.1: exact deployment PASS at 0xA2DDebc4CC8Eb21bb8eB45214Bfad1A4dE7A26Fd; explicit-evidence workflow FINALIZED 4/5 AGREE and persisted REFUND_CAPTURED_PAYMENT
current contract size: 37,980 bytes
current contract SHA-256: 00050b640db0c2c944fdd7aeb2d70c1715eedd635272478314fa74ec0c9209a4
```

Verified tool versions: Python 3.13.9, `genvm-linter` 0.11.0, `genlayer-test` 0.29.2, pytest 8.4.2, and Pyright 1.1.410.

The v0.2.1 three-test GLSim run used five prompt-specific mock validators and proved consensus plumbing, result validation, storage transitions, caller authorization, and the storage-free callback shape. It did not prove heterogeneous real-model accuracy or prompt-injection resistance. The no-mock current-source StudioNet smoke finalized a bounded recovery decision by a three-agree/two-disagree majority across three rounds and persisted the expected digest-linked state; it was not unanimous. The retained configured validator slots show configured model/provider diversity, but policy-router aliases prevent a claim about the exact backend that executed every validation.

The current-source Bradbury deployment finalized with five `AGREE` votes and exact source equality. Three governance attempts for the first evidence reference failed closed and wrote no decision: `VALIDATORS_TIMEOUT`, `NO_MAJORITY`, and finalized `DISAGREE`. A new explicit-evidence reference then finalized four setup writes unanimously and finalized governance with four `AGREE` votes and one `DETERMINISTIC_VIOLATION`. Latest-final state is `DECIDED` with decision `1`, `PLAN_SELECTED / UNIQUE_RECOVERY_MATCH / REFUND_CAPTURED_PAYMENT`, and digest-linked authenticated reports. This establishes positive current-source Bradbury semantic behavior while truthfully preserving the negative attempts. Public receipts do not expose every validator's private provider log, so no exact model identity or per-validator LLM-call claim is made.

All other retained hosted records describe superseded v0.2.0. The older positive StudioNet record and separate contradictory-evidence negative record establish only their historical transactions. The v0.2.0 Bradbury deployment finalized, but its semantic transaction failed closed before inference with five `DETERMINISTIC_VIOLATION` votes and no decision write, exposing the nondeterministic storage-read finding fixed in v0.2.1. None of those v0.2.0 records is submission evidence for the current source.
