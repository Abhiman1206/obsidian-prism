from pydantic import BaseModel, Field


class LineageRecord(BaseModel):
    lineage_id: str
    run_id: str
    repository_id: str
    artifact_type: str = Field(pattern="^(commit|churn|cadence)$")
    artifact_id: str
    source_provider: str = Field(pattern="^(github|gitlab|pydriller)$")
    source_locator: str
    claim_ref: str
    created_at: str
