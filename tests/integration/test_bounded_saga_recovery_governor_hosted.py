"""Opt-in hosted-network smoke test with real network-selected inference."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from gltest import create_accounts, get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus


pytestmark = [
    pytest.mark.hosted,
    pytest.mark.skipif(
        os.environ.get("RUN_GENLAYER_HOSTED") != "1",
        reason="set RUN_GENLAYER_HOSTED=1 only for StudioNet or Bradbury",
    ),
]


def _compact(value):
    return json.dumps(value, separators=(",", ":"))


def test_hosted_real_inference_smoke():
    accounts = create_accounts(3)
    steps = [
        {
            "id": "RESERVE_SEAT",
            "description": "Reserve the requested seat with the inventory service.",
            "reporter": accounts[0].address,
        },
        {
            "id": "CHARGE_PAYMENT",
            "description": "Authorize or capture the customer's payment with the payment service.",
            "reporter": accounts[1].address,
        },
        {
            "id": "ISSUE_TICKET",
            "description": "Issue the final ticket after inventory and payment steps succeed.",
            "reporter": accounts[2].address,
        },
    ]
    plans = [
        {
            "id": "REFUND_AND_RELEASE",
            "description": "Refund captured funds and release the reserved seat after ticket issuance fails.",
            "when_effects": "Payment was captured and remains refundable, a seat remains reserved, and no ticket was issued.",
            "required_succeeded_steps": ["RESERVE_SEAT", "CHARGE_PAYMENT"],
            "required_failed_steps": ["ISSUE_TICKET"],
            "forbidden_succeeded_steps": [],
        },
        {
            "id": "VOID_AUTH_AND_RELEASE",
            "description": "Void a payment authorization and release the reserved seat after ticket issuance fails.",
            "when_effects": "Payment was only authorized, no funds were captured, and no ticket was issued.",
            "required_succeeded_steps": ["RESERVE_SEAT", "CHARGE_PAYMENT"],
            "required_failed_steps": ["ISSUE_TICKET"],
            "forbidden_succeeded_steps": [],
        },
    ]
    path = Path(__file__).resolve().parents[2] / "contracts" / "BoundedSagaRecoveryGovernor.py"
    contract = get_contract_factory(contract_file_path=path).deploy(
        args=["FLIGHT-BOOKING-SAGA", "WORKFLOW-V2", _compact(steps), _compact(plans)],
        account=accounts[0],
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    assert contract.get_policy(args=[]).call()["contract_version"] == "0.2.1"
    reference = "SAGA-HOSTED-001"
    open_receipt = contract.open_workflow(args=[reference]).transact(
        wait_transaction_status=TransactionStatus.FINALIZED
    )
    assert tx_execution_succeeded(open_receipt), open_receipt
    freeze_receipt = contract.freeze_failure_summary(
        args=[
            reference,
            "Payment was captured and remains refundable, inventory remains held, and ticket issuance failed.",
        ]
    ).transact(wait_transaction_status=TransactionStatus.FINALIZED)
    assert tx_execution_succeeded(freeze_receipt), freeze_receipt

    reports = [
        (
            accounts[0],
            "RESERVE_SEAT",
            "SUCCEEDED",
            "Seat 12A is reserved and remains held for this booking.",
        ),
        (
            accounts[1],
            "CHARGE_PAYMENT",
            "SUCCEEDED",
            "The customer's card was charged, funds were captured, and the payment service reports the capture remains refundable.",
        ),
        (
            accounts[2],
            "ISSUE_TICKET",
            "FAILED",
            "Ticket issuance failed before any ticket identifier was created.",
        ),
    ]
    for account, step_id, status, effect in reports:
        receipt = contract.connect(account).submit_step_report(
            args=[reference, step_id, status, effect]
        ).transact(wait_transaction_status=TransactionStatus.FINALIZED)
        assert tx_execution_succeeded(receipt), receipt

    # Deliberately no transaction_context: network-selected validators and models
    # must produce and audit the semantic result.
    govern_receipt = contract.govern_recovery(args=[reference]).transact(
        wait_transaction_status=TransactionStatus.FINALIZED
    )
    assert tx_execution_succeeded(govern_receipt), govern_receipt
    decision = contract.get_decision(args=[1]).call()
    assert decision["status"] in {"PLAN_SELECTED", "MANUAL_HALT", "AMBIGUOUS"}
    if decision["status"] == "PLAN_SELECTED":
        assert decision["plan_id"] in {"REFUND_AND_RELEASE", "VOID_AUTH_AND_RELEASE"}
    else:
        assert decision["plan_id"] == ""
    assert contract.get_workflow_status(args=[reference]).call() == "DECIDED"
    print(f"hosted_contract_address={contract.address}")
    print(f"hosted_govern_receipt={govern_receipt}")
    print("hosted_decision=" + _compact(decision))
