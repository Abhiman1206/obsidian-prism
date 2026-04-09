export type RunStatus = "queued" | "running" | "succeeded" | "failed";

export interface ComponentProfile {
  component_id: string;
  repository_id: string;
  language: string;
  ownership: string;
  last_modified_at: string;
}

export interface HealthScore {
  component_id: string;
  score: number;
  contributors: string[];
  measured_at: string;
}

export interface RiskForecast {
  component_id: string;
  horizon_days: number;
  risk_probability: number;
  confidence: number;
  top_signals: string[];
}

export interface ExecutiveReportSummary {
  report_id: string;
  run_id: string;
  executive_summary: string;
  cost_of_inaction_estimate: number;
  generated_at: string;
}
