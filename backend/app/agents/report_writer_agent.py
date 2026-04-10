"""Business Synthesis (Report Writer) Agent — translates risk into executive narratives.

PRD Role: Translates the predictive technical data into a CEO-friendly narrative.
Applies the Measuring Business Value pattern to convert technical metrics into
tangible business KPIs, calculating the projected financial cost of inaction.
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from app.agents.base_agent import BaseSpecialistAgent
from app.agents.shared_memory import EpistemicMemory
from app.domain.business.report_writer import write_executive_report
from app.domain.business.translation import translate_risk_to_business_impact

logger = logging.getLogger(__name__)


def _load_env(key: str) -> str | None:
    value = os.getenv(key)
    if value:
        return value
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return None
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == key:
            cleaned = v.strip().strip('"').strip("'")
            if cleaned:
                return cleaned
    return None


class ReportWriterAgent(BaseSpecialistAgent):
    name = "report_writer_agent"
    role_description = (
        "You are a Business Synthesis agent. Your job is to translate technical risk data "
        "into an executive-ready business impact report. Frame everything in terms of time "
        "and money. Avoid engineering jargon. The reader is a non-technical CEO who needs "
        "to understand the financial cost of inaction and which components to prioritize."
    )
    tools = []  # LLM used directly for narrative, not as a tool

    def execute_deterministic(self, memory: EpistemicMemory) -> dict[str, Any]:
        """Deterministic execution: translate risks, write report, optionally enhance with LLM."""
        forecasts = memory.read("forecasts", [])

        # Translate risk to business impact
        translated = translate_risk_to_business_impact(forecasts)

        # Write deterministic executive report
        report = write_executive_report(memory.run_id, translated)
        report["report_id"] = f"report-{uuid.uuid4().hex[:12]}"
        report["generated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Build evidence-linked claims
        claims = self._build_claims(memory.run_id, report)
        report["claims"] = claims

        # Try to enhance with LLM narrative
        llm_summary = self._generate_llm_summary(report, forecasts, translated)
        if llm_summary:
            report["executive_summary"] = llm_summary
            report["summary_source"] = "groq"
        else:
            report["summary_source"] = "deterministic"

        memory.write(self.name, "translated_rows", translated)
        memory.write(self.name, "report", report)

        return {
            "status": "complete",
            "agent": self.name,
            "mode": "deterministic",
            "cost_of_inaction": report.get("cost_of_inaction_estimate", 0),
            "summary_source": report.get("summary_source", "deterministic"),
            "claim_count": len(claims),
        }

    def _build_claims(self, run_id: str, report: dict) -> list[dict]:
        claims: list[dict] = []
        for index, item in enumerate(report.get("recommended_priorities", []), start=1):
            component_id = str(item.get("component_id", ""))
            claims.append(
                {
                    "claim_id": f"claim-{index}",
                    "claim_text": (
                        f"{component_id} is prioritized due to projected cost exposure of "
                        f"${float(item.get('expected_total_cost', 0.0)):,.2f}."
                    ),
                    "lineage_refs": [
                        f"{run_id}:{component_id}:risk-forecast",
                        f"{run_id}:risk_predictor_agent:forecast_component_risk",
                        f"{run_id}:health_analyst_agent:radon_analyze_files",
                    ],
                }
            )
        return claims

    def _generate_llm_summary(
        self,
        report: dict,
        forecasts: list[dict],
        translated: list[dict],
    ) -> str | None:
        groq_key = _load_env("GROQ_API_KEY")
        if not groq_key:
            return None

        model = _load_env("GROQ_MODEL") or "llama-3.3-70b-versatile"
        groq_base = (_load_env("GROQ_API_BASE") or "https://api.groq.com/openai/v1").rstrip("/")

        payload = {
            "model": model,
            "temperature": 0.2,
            "max_tokens": 400,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an engineering-finance analyst writing for a non-technical CEO. "
                        "Produce a concise executive summary in plain business language. "
                        "Include: (1) total cost exposure, (2) top 3 riskiest components, "
                        "(3) one concrete recommended action. No jargon."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Total cost-of-inaction: ${report.get('cost_of_inaction_estimate', 0):,.2f}.\n"
                        f"Top risk components: {translated[:5]}.\n"
                        f"Forecast signals: {forecasts[:5]}.\n"
                        "Write 3-4 sentences summarizing the risk posture and one prioritized action."
                    ),
                },
            ],
        }

        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(2):
            try:
                resp = httpx.post(f"{groq_base}/chat/completions", json=payload, headers=headers, timeout=25)
                resp.raise_for_status()
                body = resp.json()
                choices = body.get("choices", [])
                if isinstance(choices, list) and choices:
                    msg = choices[0].get("message", {})
                    content = msg.get("content") if isinstance(msg, dict) else None
                    if isinstance(content, str) and content.strip():
                        return content.strip()
            except Exception as exc:
                logger.warning("Groq summary attempt %d failed: %s", attempt + 1, exc)

        return None
