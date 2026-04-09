from datetime import datetime

from pydantic import BaseModel, Field


class HealthScore(BaseModel):
    component_id: str
    score: float = Field(ge=0, le=100)
    contributors: list[str]
    measured_at: datetime
