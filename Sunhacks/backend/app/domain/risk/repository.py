from __future__ import annotations


class RiskForecastRepository:
    def __init__(self) -> None:
        self._records: list[dict] = []

    def add_many(self, records: list[dict]) -> None:
        self._records.extend(records)

    def get_ranked_by_run(self, run_id: str) -> list[dict]:
        filtered = [record for record in self._records if record.get("run_id") == run_id]
        return sorted(
            filtered,
            key=lambda record: (
                -float(record.get("risk_probability", 0.0)),
                str(record.get("component_id", "")),
            ),
        )


RISK_FORECAST_REPOSITORY = RiskForecastRepository()