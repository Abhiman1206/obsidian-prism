from pydantic import BaseModel, Field


class RiskSignal(BaseModel):
    signal_name: str
    contribution_strength: float = Field(ge=0, le=1)


class RiskForecast(BaseModel):
    component_id: str
    horizon_days: int = Field(gt=0)
    risk_probability: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    top_signals: list[RiskSignal]
