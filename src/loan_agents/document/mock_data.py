"""Canonical mock document provider for deterministic test scenarios."""

import json


SCENARIOS: dict[str, str] = {
    "document_valid_123": json.dumps(
        {
            "customer_id": "CUST-12345",
            "loan_amount": 50000,
            "income": "USD 120000 a year",
            "credit_history": "7 years good standing",
        }
    ),
    "document_risky_789": json.dumps(
        {
            "customer_id": "CUST-99999",
            "loan_amount": 50000,
            "income": "USD 40000 a year",
            "credit_history": "Recent Missed Payments",
        }
    ),
    "document_invalid_456": json.dumps(
        {
            "customer_id": "CUST-55555",
            "loan_amount": 200000,
            "credit_history": "1 year",
        }
    ),
}


def get_document_content(document_id: str) -> str:
    return SCENARIOS.get(
        document_id,
        f"ERROR: unknown document_id={document_id}. Expected one of: {', '.join(sorted(SCENARIOS))}",
    )
