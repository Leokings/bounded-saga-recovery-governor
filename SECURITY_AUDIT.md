# Security Audit Record

Date: 2026-08-12  
Scope: `contracts/BoundedSagaRecoveryGovernor.py` and its direct/integration tests  
Status: local audit and current-source StudioNet validation complete; Bradbury validation pending

## Method

- manual architecture and trust-boundary review;
- storage, access-control, replay, and state-machine review;
- nondeterministic leader/validator and output-parser review;
- prompt-injection and fail-closed review;
- GenVM lint and SDK semantic validation;
- Pyright typecheck;
- direct negative/adversarial tests; and
- five-validator GLSim consensus tests.

## Findings fixed during implementation

| Severity | Finding | Resolution |
|---|---|---|
| High | A controller-supplied reporter label would not authenticate the source of a step effect | Replaced with separate `submit_step_report` calls authenticated by `gl.message.sender_address` against immutable per-step addresses |
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

Remediated finding groups: 17 total (1 High, 10 Medium, 6 Low).

The documented trust assumptions in `SECURITY.md` are product boundaries, not fixed vulnerabilities: reporters attest to effects, validators can share correlated errors, catalog quality matters, and plan execution remains external.

## Verification snapshot

Update only from captured command output:

```text
genvm-lint check: PASS
genvm-lint typecheck: PASS
pytest direct: 46 passed
five-validator GLSim for current source: PASSED 3/3 with five explicit mock validators
StudioNet: PASSED no-mock hosted smoke; exact source at 0x63b9443113dD49213761aC6785FCD43268A8e3Af; MAJORITY_AGREE 3/2
Bradbury: PENDING
current contract size: 37,710 bytes
current contract SHA-256: d739f2f75f68b73a5f5ead8e9aad867ef9272cbf260fb2415102d927716137fb
```

Verified tool versions: Python 3.13.9, `genvm-linter` 0.11.0, `genlayer-test` 0.29.2, pytest 8.4.2, and Pyright 1.1.410.

The current-source three-test GLSim run used five prompt-specific mock validators and proved consensus plumbing, result validation, storage transitions, and caller authorization. It did not prove heterogeneous real-model accuracy or prompt-injection resistance. The no-mock current-source StudioNet smoke finalized a bounded recovery decision by a three-agree/two-disagree majority and persisted the expected digest-linked state; it was not unanimous. The retained negative predecessor finalized `MAJORITY_DISAGREE` on a materially contradictory evidence corpus and persisted no decision. These two hosted records establish only their observed transactions, not general semantic accuracy or prompt-injection immunity.
