# Deployment records

Current-source StudioNet evidence is retained in `studionet-2026-08-12-v0.2.1-proof.json`. It records exact equality with the 37,980-byte v0.2.1 source at SHA-256 `00050b640db0c2c944fdd7aeb2d70c1715eedd635272478314fa74ec0c9209a4` and address `0x61a4a6aa81FD35Eac057244F7Cc8fD01167ECdfF`, plus a finalized `MAJORITY_AGREE` recovery decision with three agree and two disagree votes across three rounds. This was majority agreement, not unanimity.

`studionet-2026-08-12-current-proof.json` is retained but explicitly marked superseded. It covers the 37,710-byte v0.2.0 source and is not current-source submission evidence.

`studionet-2026-08-12-no-majority.json` preserves a separate v0.2.0 run whose contradictory evidence corpus finalized `MAJORITY_DISAGREE`. It is negative, submission-ineligible evidence and must not be presented as a successful deployment decision.

`bradbury-2026-08-12-v0.2.1-deployment-and-smoke.json` is the current-source Bradbury record. It proves a finalized, five-vote-agree, byte-identical deployment at `0xA2DDebc4CC8Eb21bb8eB45214Bfad1A4dE7A26Fd`. The deterministic setup transactions executed successfully and were accepted, but the first semantic attempt ended `VALIDATORS_TIMEOUT` and the one govern-only retry ended `NO_MAJORITY`; no decision was written. Final-round retry counts were four `AGREE`, four `TIMEOUT`, and three `DETERMINISTIC_VIOLATION`. Public replay traces showed no runtime or storage warning and zero provider calls, so the record is submission-eligible for exact deployment only, not as a successful Bradbury semantic decision.

`bradbury-2026-08-12-deployment-proof.json` is a superseded v0.2.0 regression record. Its deployment at `0xFEc7EB1652279FE2e429A846947d5214de8C84b2` finalized with byte-exact v0.2.0 source. Its semantic `govern_recovery` call then failed closed before inference because bound methods indirectly read contract storage during nondeterministic execution; five validators recorded `DETERMINISTIC_VIOLATION`, and no decision state was written. Version 0.2.1 fixes that functional defect by copying immutable values to plain locals and using storage-free module helpers. Neither the address nor receipt is current-source submission evidence.

Use only the opt-in no-mock hosted test described in `TESTING.md` to create hosted evidence. The prompt-specific GLSim suite is local consensus-plumbing evidence and must never be recorded as heterogeneous or real-inference validation.

After a finalized StudioNet or Bradbury smoke test, add a JSON record containing:

- network and chain ID;
- contract address;
- deploy transaction hash;
- smoke-test transaction hashes;
- deployment UTC timestamp;
- contract source SHA-256;
- constructor arguments or their canonical digest;
- observed decision and validator agreement; and
- explorer URL.

Never store private keys here.
