"""Five-validator GLSim consensus tests for BoundedSagaRecoveryGovernor."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gltest import create_accounts, get_contract_factory, get_validator_factory
from gltest.assertions import tx_execution_failed, tx_execution_succeeded
from gltest.types import TransactionStatus


TEST_DATETIME = "2026-08-12T12:00:00Z"
DECISION_PROMPT_KEY = "CONSENSUS-CRITICAL RECOVERY PLAN"
AUDIT_PROMPT_KEY = "Independently audit a consensus-critical bounded saga recovery result"


def _compact(value):
    return json.dumps(value, separators=(",", ":"))


def _catalogs(accounts):
    alice, bob, charlie = accounts
    steps = [
        {
            "id": "RESERVE_SEAT",
            "description": "Reserve the requested seat with the inventory service.",
            "reporter": alice.address,
        },
        {
            "id": "CHARGE_PAYMENT",
            "description": "Authorize or capture the customer's payment with the payment service.",
            "reporter": bob.address,
        },
        {
            "id": "ISSUE_TICKET",
            "description": "Issue the final ticket after inventory and payment steps succeed.",
            "reporter": charlie.address,
        },
    ]
    plans = [
        {
            "id": "REFUND_AND_RELEASE",
            "description": "Refund captured funds and release the reserved seat after ticket issuance fails.",
            "when_effects": "Payment was captured, a seat remains reserved, and no ticket was issued.",
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
    return steps, plans


def _deploy():
    accounts = create_accounts(3)
    steps, plans = _catalogs(accounts)
    path = Path(__file__).resolve().parents[2] / "contracts" / "BoundedSagaRecoveryGovernor.py"
    factory = get_contract_factory(contract_file_path=path)
    contract = factory.deploy(
        args=["FLIGHT-BOOKING-SAGA", "WORKFLOW-V1", _compact(steps), _compact(plans)],
        account=accounts[0],
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    print(f"contract_address={contract.address}")
    return contract, accounts


def _submit_reports(contract, accounts, reference="SAGA-GLSIM-001"):
    open_receipt = contract.open_workflow(args=[reference]).transact(
        wait_transaction_status=TransactionStatus.FINALIZED
    )
    assert tx_execution_succeeded(open_receipt), open_receipt
    freeze_receipt = contract.freeze_failure_summary(
        args=[
            reference,
            "Payment completed and inventory remains held, but ticket issuance failed.",
        ]
    ).transact(wait_transaction_status=TransactionStatus.FINALIZED)
    assert tx_execution_succeeded(freeze_receipt), freeze_receipt
    calls = [
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
            "The customer's card was charged and funds were captured irreversibly.",
        ),
        (
            accounts[2],
            "ISSUE_TICKET",
            "FAILED",
            "Ticket issuance failed before any ticket identifier was created.",
        ),
    ]
    for account, step_id, status, effect in calls:
        receipt = contract.connect(account).submit_step_report(
            args=[reference, step_id, status, effect]
        ).transact(wait_transaction_status=TransactionStatus.FINALIZED)
        assert tx_execution_succeeded(receipt), receipt


def _validator_context(candidate):
    validators = get_validator_factory().batch_create_mock_validators(
        5,
        mock_llm_response={
            "nondet_exec_prompt": {
                DECISION_PROMPT_KEY: _compact(candidate),
                AUDIT_PROMPT_KEY: _compact({"accept": True}),
            }
        },
    )
    return {
        "validators": [validator.to_dict() for validator in validators],
        "genvm_datetime": TEST_DATETIME,
    }


def test_glsim_deployment_exposes_bounded_immutable_policy():
    contract, accounts = _deploy()
    policy = contract.get_policy().call()

    assert policy["policy_version"] == "BOUNDED_SAGA_RECOVERY_V2"
    assert policy["workflow_id"] == "FLIGHT-BOOKING-SAGA"
    assert len(json.loads(policy["step_catalog_json"])) == 3
    assert len(json.loads(policy["recovery_catalog_json"])) == 2
    assert policy["controller"].lower() == accounts[0].address.lower()
    assert len(policy["config_digest"]) == 64
    assert policy["worst_case_leader_prompt_bytes"] <= policy["max_prompt_bytes"]
    assert policy["worst_case_audit_prompt_bytes"] <= policy["max_prompt_bytes"]


def test_glsim_five_validators_finalize_unique_recovery_decision():
    contract, accounts = _deploy()
    _submit_reports(contract, accounts)
    candidate = {
        "status": "PLAN_SELECTED",
        "reason_code": "UNIQUE_RECOVERY_MATCH",
        "plan_id": "REFUND_AND_RELEASE",
        "matched_step_ids": ["CHARGE_PAYMENT", "ISSUE_TICKET", "RESERVE_SEAT"],
    }
    receipt = contract.govern_recovery(
        args=["SAGA-GLSIM-001"]
    ).transact(
        transaction_context=_validator_context(candidate),
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    assert tx_execution_succeeded(receipt), receipt

    decision = contract.get_decision(args=[1]).call()
    assert decision["status"] == "PLAN_SELECTED"
    assert decision["reason_code"] == "UNIQUE_RECOVERY_MATCH"
    assert decision["plan_id"] == "REFUND_AND_RELEASE"
    assert contract.get_decision_count().call() == 1
    assert contract.get_decision_id(args=["SAGA-GLSIM-001"]).call() == 1
    assert len(decision["decision_digest"]) == 64
    assert len(decision["failure_summary_digest"]) == 64
    assert contract.get_workflow_status(args=["SAGA-GLSIM-001"]).call() == "DECIDED"
    assert contract.is_open(args=["SAGA-GLSIM-001"]).call() is False


def test_glsim_unauthenticated_step_report_fails_without_state():
    contract, accounts = _deploy()
    open_receipt = contract.open_workflow(args=["SAGA-GLSIM-BAD"]).transact(
        wait_transaction_status=TransactionStatus.FINALIZED
    )
    assert tx_execution_succeeded(open_receipt), open_receipt
    freeze_receipt = contract.freeze_failure_summary(
        args=[
            "SAGA-GLSIM-BAD",
            "Payment completed and inventory remains held, but ticket issuance failed.",
        ]
    ).transact(wait_transaction_status=TransactionStatus.FINALIZED)
    assert tx_execution_succeeded(freeze_receipt), freeze_receipt
    receipt = contract.connect(accounts[1]).submit_step_report(
        args=[
            "SAGA-GLSIM-BAD",
            "RESERVE_SEAT",
            "SUCCEEDED",
            "A non-configured caller attempts to report this inventory effect.",
        ]
    ).transact(wait_transaction_status=TransactionStatus.FINALIZED)
    assert tx_execution_failed(receipt), receipt

    with pytest.raises(Exception):
        contract.get_step_report(args=["SAGA-GLSIM-BAD", "RESERVE_SEAT"]).call()
