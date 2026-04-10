from datetime import datetime

from pydantic import BaseModel, Field


class HealthFactor(BaseModel):
    name: str
    weight: float = Field(ge=0, le=1)
    raw_value: float
    normalized_value: float = Field(ge=0, le=1)
    direction: str = Field(pattern="^(positive|negative)$")


class HealthScore(BaseModel):
    component_id: str
    score: float = Field(ge=0, le=100)
    run_id: str
    repository_id: str
    contributors: list[str]
    factors: list[HealthFactor]
    measured_at: datetime
