from datetime import datetime

from pydantic import BaseModel


class ExecutiveReportSummary(BaseModel):
    report_id: str
    run_id: str
    executive_summary: str
    cost_of_inaction_estimate: float
    generated_at: datetime
