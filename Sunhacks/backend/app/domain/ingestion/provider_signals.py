def extract_cadence_signals(raw_cadence: dict | None) -> dict:
    if not raw_cadence:
        return {
            "issue_opened_count": 0,
            "issue_closed_count": 0,
            "deployment_count": 0,
            "period_start": None,
            "period_end": None,
        }

    return {
        "issue_opened_count": int(raw_cadence.get("issue_opened_count", 0)),
        "issue_closed_count": int(raw_cadence.get("issue_closed_count", 0)),
        "deployment_count": int(raw_cadence.get("deployment_count", 0)),
        "period_start": raw_cadence.get("period_start"),
        "period_end": raw_cadence.get("period_end"),
    }
