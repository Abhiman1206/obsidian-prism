export type RunStatus = "queued" | "running" | "succeeded" | "failed";

export type Provider = "github" | "gitlab";
export type AuthorizationReason =
  | "authorized_collaborator"
  | "missing_repo_access"
  | "token_invalid"
  | "rate_limited"
  | "transient_error"
  | "provider_error";

export interface ProviderAuthPayload {
  provider: Provider;
  access_token: string;
  scopes: string[];
}

export interface RepositoryRegistrationRequest {
  provider: Provider;
  repository_url: string;
  repository_name: string;
  auth: ProviderAuthPayload;
}

export interface RepositoryRegistrationResponse {
  repository_id: string;
  provider: Provider;
  repository_url: string;
  authorization_status: "authorized" | "pending" | "failed";
  authorization_reason: AuthorizationReason;
  run_ready: boolean;
  owner_user_id: string | null;
  token_owner_login: string | null;
}

export interface RepositoryRevalidateRequest {
  repository_id: string;
  provider: Provider;
}

export interface RepositoryRevalidateResponse {
  repository_id: string;
  provider: Provider;
  authorization_status: "authorized" | "pending" | "failed";
  authorization_reason: AuthorizationReason;
  run_ready: boolean;
  owner_user_id: string | null;
}

export interface CreateRunRequest {
  repository_id: string;
  provider: Provider;
  branch?: string | null;
}

export interface CreateRunResponse {
  run_id: string;
  status: RunStatus;
  created_at: string;
}

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
  run_id: string;
  repository_id: string;
  contributors: string[];
  factors: HealthFactor[];
  measured_at: string;
}

export interface HealthFactor {
  name: string;
  weight: number;
  raw_value: number;
  normalized_value: number;
  direction: "positive" | "negative";
}

export interface RiskForecast {
  component_id: string;
  horizon_days: number;
  risk_probability: number;
  confidence: number;
  top_signals: RiskSignal[];
}

export interface RiskSignal {
  signal_name: string;
  contribution_strength: number;
}

export interface TopRiskItem {
  component_id: string;
  expected_total_cost: number;
  expected_engineering_hours: number;
  expected_downtime_hours: number;
}

export interface CostOfInactionSection {
  expected_total_cost: number;
  summary: string;
}

export interface PriorityRecommendation {
  component_id: string;
  action: string;
  expected_total_cost: number;
}

export interface ExecutiveReportClaim {
  claim_id: string;
  claim_text: string;
  lineage_refs: string[];
}

export interface ExecutiveReportSummary {
  report_id: string;
  run_id: string;
  executive_summary: string;
  cost_of_inaction_estimate: number;
  top_risks: TopRiskItem[];
  cost_of_inaction: CostOfInactionSection;
  recommended_priorities: PriorityRecommendation[];
  claims: ExecutiveReportClaim[];
  generated_at: string;
}

export interface RepositoryLanguageStat {
  language: string;
  bytes: number;
  percentage: number;
}

export interface RepositoryCommitInsight {
  sha: string;
  message: string;
  author: string;
  committed_at: string;
  url: string;
}

export interface RepositoryHealthSummary {
  score: number;
  summary: string;
}

export interface RepositoryAnalysis {
  provider: Provider;
  repository_url: string;
  repository_name: string;
  description: string | null;
  default_branch: string;
  stars: number;
  forks: number;
  watchers: number;
  open_issues: number;
  contributor_count: number;
  archived: boolean;
  has_readme: boolean;
  file_count: number;
  repository_size_bytes: number;
  primary_language: string | null;
  languages: RepositoryLanguageStat[];
  topics: string[];
  recent_commits: RepositoryCommitInsight[];
  pushed_at: string | null;
  health: RepositoryHealthSummary;
}
