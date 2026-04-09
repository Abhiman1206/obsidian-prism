from app.domain.ingestion.provider_signals import extract_cadence_signals



def test_extract_cadence_returns_counts_when_available() -> None:
    cadence = extract_cadence_signals(
        {
            "issue_opened_count": 8,
            "issue_closed_count": 5,
            "deployment_count": 3,
            "period_start": "2026-03-01",
            "period_end": "2026-03-31",
        }
    )

    assert cadence["issue_opened_count"] == 8
    assert cadence["issue_closed_count"] == 5
    assert cadence["deployment_count"] == 3
    assert cadence["period_start"] == "2026-03-01"
    assert cadence["period_end"] == "2026-03-31"



def test_extract_cadence_returns_zero_defaults_when_missing() -> None:
    cadence = extract_cadence_signals(None)

    assert cadence["issue_opened_count"] == 0
    assert cadence["issue_closed_count"] == 0
    assert cadence["deployment_count"] == 0
    assert cadence["period_start"] is None
    assert cadence["period_end"] is None
