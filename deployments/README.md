# Deployment records

Current-source StudioNet evidence is retained in `studionet-2026-08-12-current-proof.json`. It records exact deployed-source equality at `0x63b9443113dD49213761aC6785FCD43268A8e3Af` and a finalized `MAJORITY_AGREE` recovery decision with three agree and two disagree votes. This was majority agreement, not unanimity.

`studionet-2026-08-12-no-majority.json` preserves an earlier unchanged-contract run whose contradictory evidence corpus finalized `MAJORITY_DISAGREE`. It is negative, submission-ineligible evidence and must not be presented as a successful deployment decision. Bradbury remains pending.

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
