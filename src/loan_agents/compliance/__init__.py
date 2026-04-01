"""Compliance stage logic for loan pipeline."""

from typing import Any


def run_compliance_stage(
	*,
	credit_history: str,
	risk_score: int,
) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any] | None]:
	if risk_score >= 8:
		artifact = {
			"is_compliant": False,
			"reason": f"Risk Score {risk_score} exceeds limit of 7.",
			"credit_history": credit_history,
		}
	else:
		artifact = {
			"is_compliant": True,
			"reason": "Compliant.",
			"credit_history": credit_history,
		}

	stage = {
		"status": "processed",
		"provider": "mock",
		"artifact": artifact,
	}
	return stage, None, artifact
