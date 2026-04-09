from datetime import datetime

from pydantic import BaseModel


class TopRiskItem(BaseModel):
    component_id: str
    expected_total_cost: float
    expected_engineering_hours: float
    expected_downtime_hours: float


class CostOfInactionSection(BaseModel):
    expected_total_cost: float
    summary: str


class PriorityRecommendation(BaseModel):
    component_id: str
    action: str
    expected_total_cost: float


class ExecutiveReportSummary(BaseModel):
    report_id: str
    run_id: str
    executive_summary: str
    cost_of_inaction_estimate: float
    top_risks: list[TopRiskItem]
    cost_of_inaction: CostOfInactionSection
    recommended_priorities: list[PriorityRecommendation]
    generated_at: datetime
