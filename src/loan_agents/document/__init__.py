"""Document stage logic for loan pipeline."""

import json
from typing import Any

from loan_agents.document.mock_data import get_document_content

REQUIRED_FIELDS = ("customer_id", "loan_amount", "income", "credit_history")


def run_document_stage(document_id: str) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any] | None]:
	content = get_document_content(document_id)
	if content.startswith("ERROR:"):
		stage = {
			"status": "failed",
			"provider": "mock",
			"artifact": {"reason": content},
		}
		error = {
			"code": "DOCUMENT_ERROR",
			"message": content,
			"failure_category": "invalid_document",
			"retry_count": 0,
			"stage": "document",
		}
		return stage, error, None

	try:
		data = json.loads(content)
	except json.JSONDecodeError:
		stage = {
			"status": "failed",
			"provider": "mock",
			"artifact": {"reason": "Invalid JSON document payload"},
		}
		error = {
			"code": "DOCUMENT_ERROR",
			"message": "Invalid JSON document payload",
			"failure_category": "invalid_document",
			"retry_count": 0,
			"stage": "document",
		}
		return stage, error, None

	missing = [field for field in REQUIRED_FIELDS if field not in data]
	if missing:
		message = f"Missing fields: {', '.join(missing)}"
		stage = {
			"status": "failed",
			"provider": "mock",
			"artifact": {"reason": message, "missing_fields": missing},
		}
		error = {
			"code": "DOCUMENT_ERROR",
			"message": message,
			"failure_category": "invalid_document",
			"retry_count": 0,
			"stage": "document",
		}
		return stage, error, None

	artifact = {
		"customer_id": str(data["customer_id"]),
		"loan_amount": int(data["loan_amount"]),
		"income": str(data["income"]),
		"credit_history": str(data["credit_history"]),
	}
	stage = {
		"status": "processed",
		"provider": "mock",
		"artifact": artifact,
	}
	return stage, None, artifact
