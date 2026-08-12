# Testing

## Toolchain

- GenVM runner dependency: pinned in the first contract line
- `genvm-linter==0.11.0`
- `genlayer-test[sim]==0.29.2`
- `pytest`
- `pyright`

Install:

```powershell
python -m pip install -r requirements.txt
```

## Static validation

```powershell
genvm-lint check contracts\BoundedSagaRecoveryGovernor.py --json
genvm-lint typecheck contracts\BoundedSagaRecoveryGovernor.py --json
```

## Direct suite

```powershell
pytest tests\direct -q
```

The direct suite covers:

- pinned runner and immutable canonical policy;
- conservative configuration-time and runtime UTF-8 prompt budgets, including exhaustive audit sizing for every registered plan candidate and both non-selection outcomes;
- controller-only workflow opening and adjudication;
- separately frozen, immutable controller context summaries;
- per-step caller authentication;
- unopened-reference and reporter storage-spam prevention;
- complete report coverage and partial-failure gating;
- structural recovery eligibility;
- unique, manual-halt, and ambiguous outcomes;
- schema-expansion attempts embedded in adversarial evidence (this proves output closure, not real-model injection resistance);
- malformed leader and validator responses;
- oversized raw and canonicalized LLM responses;
- AST regression coverage proving nondeterministic callbacks do not capture contract storage through `self`;
- independent validator acceptance/rejection paths;
- replay and append-only records;
- terminal decision/abandonment lifecycle and accurate status views;
- digest shape and bounded views;
- invalid catalog references/contradictions;
- native-value rejection and invisible-character filtering.

Direct mode executes the leader path and can invoke the stored validator function explicitly. It is not a substitute for network consensus.

Current-source v0.2.1 direct result: **47 passed**.

## Five-validator GLSim suite

Terminal 1:

```powershell
python tests\run_glsim.py --port 4000 --validators 5 --no-browser --seed 4242
```

Terminal 2:

```powershell
gltest tests\integration -v -s --network localnet
```

The suite deploys the real contract, freezes the summary in a separate transaction, submits writes from three distinct accounts, runs the recovery transaction through five mock validators, verifies the persisted decision, and verifies an unauthorized reporter cannot persist state.

The mocks are prompt-specific: the leader receives a bounded decision object and validators receive a bounded audit object. Version 0.2.1 passed all three GLSim tests with five explicit mock validators. Mocked GLSim never proves semantic accuracy across heterogeneous production models.

## StudioNet

The mock GLSim file must never be used as hosted-inference evidence. The hosted test is a separate opt-in file and deliberately supplies no `transaction_context`, mock validators, or canned model answers:

```powershell
$env:RUN_GENLAYER_HOSTED='1'
gltest tests\integration\test_bounded_saga_recovery_governor_hosted.py -v -s --network studionet
Remove-Item Env:RUN_GENLAYER_HOSTED
```

StudioNet may not produce the fixture's exact semantic result on every run. The hosted test accepts any valid bounded outcome and validates its plan-ID constraints.

Current-source v0.2.1 result: **1 passed** in 369.23 seconds. Contract `0x61a4a6aa81FD35Eac057244F7Cc8fD01167ECdfF` deployed with exact byte-for-byte source equality at SHA-256 `00050b640db0c2c944fdd7aeb2d70c1715eedd635272478314fa74ec0c9209a4`. Six setup writes were checked for finalized execution success. The governance receipt finalized `MAJORITY_AGREE` across three rounds with five committed/revealed votes: three `AGREE` and two `DISAGREE`. The persisted result was `PLAN_SELECTED / UNIQUE_RECOVERY_MATCH / REFUND_AND_RELEASE` with all three required step IDs. This is majority evidence, not unanimous agreement. The first test attempt hit the documented StudioNet RPC limit during receipt polling; the unchanged-contract retry passed. See [`deployments/studionet-2026-08-12-v0.2.1-proof.json`](deployments/studionet-2026-08-12-v0.2.1-proof.json).

Historical v0.2.0 evidence is retained for auditability. [`deployments/studionet-2026-08-12-current-proof.json`](deployments/studionet-2026-08-12-current-proof.json) records an exact-source v0.2.0 success at `0x63b9443113dD49213761aC6785FCD43268A8e3Af`; despite its legacy filename, it is superseded and submission-ineligible for the current source. [`deployments/studionet-2026-08-12-no-majority.json`](deployments/studionet-2026-08-12-no-majority.json) records a separate v0.2.0 contradictory-evidence run that finalized `MAJORITY_DISAGREE`, persisted no decision, and is also submission-ineligible.

## Bradbury

Add a testnet-only private key to an ignored `.env` file, configure the funded account according to the current GenLayer CLI/gltest documentation, then run:

```powershell
$env:RUN_GENLAYER_HOSTED='1'
gltest tests\integration\test_bounded_saga_recovery_governor_hosted.py -v -s --network testnet_bradbury
Remove-Item Env:RUN_GENLAYER_HOSTED
```

Never commit a private key or reuse a production wallet.

Current-source v0.2.1 exact deployment: **PASS**. Contract `0xA2DDebc4CC8Eb21bb8eB45214Bfad1A4dE7A26Fd` finalized with five `AGREE` votes and exact byte-for-byte equality to the 37,980-byte source at SHA-256 `00050b640db0c2c944fdd7aeb2d70c1715eedd635272478314fa74ec0c9209a4`. Four deterministic setup transactions executed successfully with unanimous five-vote agreement and were `ACCEPTED`, not finalized, when recorded.

Bradbury semantic smoke: **NO ACCEPTED DECISION**. Attempt 1 ended `VALIDATORS_TIMEOUT / TIMEOUT` with one `AGREE`, three `TIMEOUT`, and one `DETERMINISTIC_VIOLATION` vote. After latest-final reads confirmed `REPORTING`, zero decisions, and both immutable reports intact, the single govern-only retry ended `UNDETERMINED / NO_MAJORITY`. Its three rounds recorded: round 0, three `TIMEOUT` and two `DETERMINISTIC_VIOLATION`; round 1, six `AGREE` and one `TIMEOUT`; round 2, four `AGREE`, four `TIMEOUT`, and three `DETERMINISTIC_VIOLATION`. No decision was persisted.

Public replay traces for all retry rounds returned successfully with empty stdout/stderr, no storage warning, and no runtime error. They exposed one replay trace per round rather than separate validator execution logs and recorded zero provider calls, so this record does not claim that live LLM execution was independently established. See [`deployments/bradbury-2026-08-12-v0.2.1-deployment-and-smoke.json`](deployments/bradbury-2026-08-12-v0.2.1-deployment-and-smoke.json). The current-source StudioNet proof remains the positive no-mock semantic-consensus evidence.

[`deployments/bradbury-2026-08-12-deployment-proof.json`](deployments/bradbury-2026-08-12-deployment-proof.json) is a superseded v0.2.0 regression record. Its deployment at `0xFEc7EB1652279FE2e429A846947d5214de8C84b2` finalized with byte-exact v0.2.0 source, but `govern_recovery` then failed closed before any LLM call. The trace showed that nondeterministic execution indirectly read `self.workflow_id` through bound contract methods; GenVM does not support contract-storage reads in that mode. Five validators returned `DETERMINISTIC_VIOLATION`, and no decision state was written. Version 0.2.1 copies immutable workflow context to plain locals and calls storage-free module helpers, with a direct AST regression test ensuring neither nondeterministic callback captures `self`. The old address, deployment receipt, and failed smoke are historical and submission-ineligible for v0.2.1.
