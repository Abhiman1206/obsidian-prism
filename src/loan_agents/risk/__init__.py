"""Risk stage logic for loan pipeline."""

from typing import Any


def _annual_income(income: str) -> int:
	numeric = "".join(ch for ch in income if ch.isdigit())
	if not numeric:
		return 0
	value = int(numeric)
	return value * 12 if "month" in income.lower() else value


def run_risk_stage(
	*,
	loan_amount: int,
	income: str,
	credit_score: int,
) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any] | None]:
	if credit_score < 600:
		artifact = {
			"risk_score": 9,
			"risk_level": "HIGH",
			"reason": "Credit score too low",
		}
		stage = {
			"status": "processed",
			"provider": "mock",
			"artifact": artifact,
		}
		return stage, None, artifact

	annual_income = _annual_income(income)
	risk_score = 1
	if credit_score < 720:
		risk_score += 2
	if annual_income > 0 and (loan_amount / annual_income) > 0.5:
		risk_score += 3

	bounded = min(risk_score, 10)
	artifact = {
		"risk_score": bounded,
		"risk_level": "HIGH" if bounded >= 8 else "LOW",
	}
	stage = {
		"status": "processed",
		"provider": "mock",
		"artifact": artifact,
	}
	return stage, None, artifact
