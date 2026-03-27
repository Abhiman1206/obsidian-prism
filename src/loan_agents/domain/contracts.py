"""Shared request/response contracts for pipeline execution."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PipelineInput:
    applicant_id: str
    document_id: str
    mode: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PipelineInput":
        return cls(
            applicant_id=str(payload["applicant_id"]),
            document_id=str(payload["document_id"]),
            mode=str(payload["mode"]),
        )


@dataclass(frozen=True)
class StageResult:
    stage: str
    status: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PipelineResult:
    status: str
    decision: str
    mode: str
    stages: dict[str, Any]
    error: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "decision": self.decision,
            "mode": self.mode,
            "stages": self.stages,
            "error": self.error,
        }
