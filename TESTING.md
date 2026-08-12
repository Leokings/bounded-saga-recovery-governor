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
- independent validator acceptance/rejection paths;
- replay and append-only records;
- terminal decision/abandonment lifecycle and accurate status views;
- digest shape and bounded views;
- invalid catalog references/contradictions;
- native-value rejection and invisible-character filtering.

Direct mode executes the leader path and can invoke the stored validator function explicitly. It is not a substitute for network consensus.

Current-source direct result: **46 passed**.

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

The mocks are prompt-specific: the leader receives a bounded decision object and validators receive a bounded audit object. The frozen current source passed all three GLSim tests with five explicit mock validators. Mocked GLSim never proves semantic accuracy across heterogeneous production models.

## StudioNet

The mock GLSim file must never be used as hosted-inference evidence. The hosted test is a separate opt-in file and deliberately supplies no `transaction_context`, mock validators, or canned model answers:

```powershell
$env:RUN_GENLAYER_HOSTED='1'
gltest tests\integration\test_bounded_saga_recovery_governor_hosted.py -v -s --network studionet
Remove-Item Env:RUN_GENLAYER_HOSTED
```

StudioNet may not produce the fixture's exact semantic result on every run. The hosted test accepts any valid bounded outcome and validates its plan-ID constraints.

Current-source result: **1 passed** in 358.20 seconds. Contract `0x63b9443113dD49213761aC6785FCD43268A8e3Af` deployed with exact byte-for-byte source equality at SHA-256 `d739f2f75f68b73a5f5ead8e9aad867ef9272cbf260fb2415102d927716137fb`. Six setup writes were checked for finalized execution success. The governance receipt finalized `MAJORITY_AGREE` in one round with five committed/revealed votes: three `AGREE` and two `DISAGREE`. The persisted result was `PLAN_SELECTED / UNIQUE_RECOVERY_MATCH / REFUND_AND_RELEASE` with all three required step IDs. This is majority evidence, not unanimous agreement. See [`deployments/studionet-2026-08-12-current-proof.json`](deployments/studionet-2026-08-12-current-proof.json).

An earlier unchanged-contract run used the contradictory phrase that captured funds were irreversible while asking the catalog to select a refund plan. It finalized `MAJORITY_DISAGREE`, persisted no decision, and left the workflow in `REPORTING`. That failed run is deliberately retained as submission-ineligible negative evidence in [`deployments/studionet-2026-08-12-no-majority.json`](deployments/studionet-2026-08-12-no-majority.json).

## Bradbury

Add a testnet-only private key to an ignored `.env` file, configure the funded account according to the current GenLayer CLI/gltest documentation, then run:

```powershell
$env:RUN_GENLAYER_HOSTED='1'
gltest tests\integration\test_bounded_saga_recovery_governor_hosted.py -v -s --network testnet_bradbury
Remove-Item Env:RUN_GENLAYER_HOSTED
```

Never commit a private key or reuse a production wallet.

Current-source Bradbury deployment and smoke-test evidence: **pending**.
