# Example

The example models a three-step ticket-booking saga. Replace all placeholder reporter addresses before deployment.

1. Deploy with `workflow_id = FLIGHT-BOOKING-SAGA`, `workflow_version = WORKFLOW-V1`, and compact JSON from the two catalog files.
2. The controller opens `BOOKING-123`.
3. The controller freezes one context summary before reporting begins.
4. Each configured reporter submits its own step result. Reporting ICs must emit with `on="finalized"` after their source effects are final.
5. If reservation and captured payment succeed while ticket issuance fails, the governor distinguishes `REFUND_AND_RELEASE` from `VOID_AUTH_AND_RELEASE` using the observed payment effect. The frozen controller summary cannot override those reports.
6. A separate deterministic executor may consume the finalized plan ID.

The example is illustrative. It does not implement payment, ticketing, refunds, or seat release.
