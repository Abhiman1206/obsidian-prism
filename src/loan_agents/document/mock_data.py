"""Canonical mock document provider for deterministic test scenarios."""

SCENARIOS: dict[str, str] = {
    "document_valid_123": """Applicant name: Jane Doe\nIncome: 96000\nRequested loan: 250000\nEmployment: Full-time""",
    "document_risky_789": """Applicant name: John Smith\nIncome: 43000\nRequested loan: 320000\nEmployment: Contract""",
    "document_invalid_456": """Applicant name: Missing\nIncome: N/A\nRequested loan: unknown\nEmployment: unknown""",
}


def get_document_content(document_id: str) -> str:
    return SCENARIOS.get(
        document_id,
        f"ERROR: unknown document_id={document_id}. Expected one of: {', '.join(sorted(SCENARIOS))}",
    )
