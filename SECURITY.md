# Security

## Threat model

The contract treats catalog text, effect summaries, failure summaries, and LLM output as untrusted. It assumes the deploying controller and registered reporter addresses are the intended workflow identities, but it does not assume that their natural-language claims are automatically true.

## Controls

### Closed authority

- The deployer becomes the immutable controller.
- Only the controller can open or adjudicate a workflow reference.
- Every step has a distinct nonzero reporter address; only that exact address can report the step.
- The controller context summary is frozen in a separate transaction before reports and cannot change across adjudication retries.
- An opened reference, step report, and final decision cannot be overwritten.

### Closed recovery surface

The model cannot return a target address, method, arguments, amount, message, or new plan. `PLAN_SELECTED` accepts only a plan ID already committed at deployment and already found structurally eligible by deterministic code.

### Fail-closed behavior

- incomplete reports revert;
- configurations whose conservative worst-case prompt exceeds the UTF-8 byte budget fail deployment; validator-audit sizing checks every registered plan candidate plus both non-selection outcomes;
- workflows without both success and failure revert;
- malformed or expansive model output reverts, with caps applied both before and after canonical JSON serialization;
- leader errors are rejected by validators;
- no unique safe match becomes `MANUAL_HALT`;
- multiple plausible matches become `AMBIGUOUS`; and
- every decision or controller abandonment consumes the reference, preventing repeated shopping for a preferred verdict.

### Prompt injection

Prompts explicitly delimit all workflow content as quoted data. They identify authenticated reports as the exclusive authoritative evidence and prohibit the frozen controller summary from adding or overriding facts. Output fields and identifiers are closed and revalidated. Injection text may still influence a model's reasoning, which is why validators independently audit the substance and the safe outcomes remain bounded. The mocked local schema-injection test proves output closure, not real-model injection resistance. Integrators must red-team their own catalog and report vocabulary with heterogeneous models.

## Trust and limitations

1. **Reporter authentication is not physical truth.** The contract proves which configured address submitted a report. It does not prove that the external effect occurred. Use reporting ICs that derive their state from appropriate evidence, or choose reporters whose assertions fit the application's trust model.
2. **Consensus is not infallibility.** Correlated models can share errors. High-value recovery should retain an appeal/manual escalation path and should not execute before finality.
3. **No automatic recovery occurs.** The decision is a recommendation bound to an immutable catalog. A separate consumer must map plan IDs to audited deterministic actions.
4. **Reports are intentionally immutable.** A mistaken report requires a new request reference; it cannot be edited in place.
5. **No built-in timeout exists.** The contract never guesses missing reports. Applications must decide off-chain when to use the controller's terminal `abandon_workflow` path.
6. **Upstream finality is an integration requirement.** The contract authenticates a reporter but cannot prove that its source transaction is finalized. Reporting ICs must use `emit(on="finalized")`; accepted-state messages can survive an appeal and poison an immutable reference.
7. **Reporter identity isolation is intentional.** One address cannot be configured for multiple steps and there is no batch-report API. Use distinct reporting ICs or keys when one operator owns multiple steps.
8. **Catalog quality matters.** Overlapping `when_effects` rules may produce `AMBIGUOUS`; underspecified rules may produce `MANUAL_HALT`. Test catalogs before using them with consequential actions.

## Integration checklist

- Deploy from the intended immutable controller.
- Pin every reporter to the correct EOA or IC address.
- For an IC reporter, wait for source finality and emit only with `on="finalized"`.
- Keep plans mutually distinguishable and operationally bounded.
- Never interpret descriptions as executable code.
- Consume only finalized decisions from the expected deployment/config digest.
- Make downstream plan execution idempotent and replay-protected.
- Cap the financial consequence independently of model output.
- Test multi-model agreement and appeal reversals before production.

## Reporting a vulnerability

Do not disclose exploitable issues publicly before the maintainer has time to respond. Include the affected contract version, reproduction, impact, and proposed mitigation in a private GitHub security advisory for the repository.
