"""Shared 4-stage domain pipeline used by all orchestration adapters."""

import time
from typing import Any

from loan_agents.compliance import run_compliance_stage
from loan_agents.credit import run_credit_stage
from loan_agents.document import run_document_stage
from loan_agents.orchestration.normalized import build_adapter_failure, build_success_result
from loan_agents.risk import run_risk_stage


def _duration_ms(started_at: float) -> int:
    return max(0, int((time.monotonic() - started_at) * 1000))


def _skipped_stage(reason: str) -> dict[str, Any]:
    return {
        "status": "skipped",
        "provider": "mock",
        "artifact": {"reason": reason},
        "duration_ms": 0,
    }


def execute_domain_pipeline(input_payload: dict[str, Any], mode: str) -> dict[str, Any]:
    stages: dict[str, Any] = {}

    started = time.monotonic()
    document_stage, error, doc = run_document_stage(str(input_payload["document_id"]))
    document_stage["duration_ms"] = _duration_ms(started)
    stages["document"] = document_stage
    if error is not None or doc is None:
        stages["credit"] = _skipped_stage("document stage failed")
        stages["risk"] = _skipped_stage("document stage failed")
        stages["compliance"] = _skipped_stage("document stage failed")
        return build_adapter_failure(
            mode=mode,
            code=error["code"],
            message=error["message"],
            failure_category=error["failure_category"],
            retry_count=error["retry_count"],
            stage=error["stage"],
            stages=stages,
        )

    started = time.monotonic()
    credit_stage, error, credit = run_credit_stage(doc["customer_id"])
    credit_stage["duration_ms"] = _duration_ms(started)
    stages["credit"] = credit_stage
    if error is not None or credit is None:
        stages["risk"] = _skipped_stage("credit stage failed")
        stages["compliance"] = _skipped_stage("credit stage failed")
        return build_adapter_failure(
            mode=mode,
            code=error["code"],
            message=error["message"],
            failure_category=error["failure_category"],
            retry_count=error["retry_count"],
            stage=error["stage"],
            stages=stages,
        )

    started = time.monotonic()
    risk_stage, error, risk = run_risk_stage(
        loan_amount=int(doc["loan_amount"]),
        income=str(doc["income"]),
        credit_score=int(credit["credit_score"]),
    )
    risk_stage["duration_ms"] = _duration_ms(started)
    stages["risk"] = risk_stage
    if error is not None or risk is None:
        stages["compliance"] = _skipped_stage("risk stage failed")
        return build_adapter_failure(
            mode=mode,
            code=error["code"],
            message=error["message"],
            failure_category=error["failure_category"],
            retry_count=error["retry_count"],
            stage=error["stage"],
            stages=stages,
        )

    started = time.monotonic()
    compliance_stage, error, compliance = run_compliance_stage(
        credit_history=str(doc["credit_history"]),
        risk_score=int(risk["risk_score"]),
    )
    compliance_stage["duration_ms"] = _duration_ms(started)
    stages["compliance"] = compliance_stage
    if error is not None or compliance is None:
        return build_adapter_failure(
            mode=mode,
            code=error["code"],
            message=error["message"],
            failure_category=error["failure_category"],
            retry_count=error["retry_count"],
            stage=error["stage"],
            stages=stages,
        )

    decision = "approve" if compliance["is_compliant"] and risk["risk_level"] == "LOW" else "review"
    return build_success_result(mode=mode, decision=decision, stages=stages)
