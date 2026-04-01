"""Credit stage logic for loan pipeline."""

from typing import Any

_SCORES: dict[str, int] = {
	"CUST-12345": 810,
	"CUST-99999": 550,
	"CUST-55555": 620,
}


def run_credit_stage(customer_id: str) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any] | None]:
	score = _SCORES.get(customer_id)
	if score is None:
		message = f"Customer not found: {customer_id}"
		stage = {
			"status": "failed",
			"provider": "mock",
			"artifact": {"reason": message},
		}
		error = {
			"code": "CREDIT_ERROR",
			"message": message,
			"failure_category": "invalid_document",
			"retry_count": 0,
			"stage": "credit",
		}
		return stage, error, None

	artifact = {"customer_id": customer_id, "credit_score": score}
	stage = {
		"status": "processed",
		"provider": "mock",
		"artifact": artifact,
	}
	return stage, None, artifact
