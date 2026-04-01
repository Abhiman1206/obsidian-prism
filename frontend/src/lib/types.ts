export type PipelineMode = "crewai" | "langgraph";

export type PipelineInput = {
  applicant_id: string;
  document_id: string;
  mode: PipelineMode;
};

export type PipelineResult = {
  status: string;
  decision: string;
  mode: string;
  stages: Record<string, unknown>;
  error: {
    code: string;
    message: string;
    failure_category?: string;
    retry_count?: number;
    stage?: string;
    details?: Record<string, unknown>;
  } | null;
};

export type ValidationErrors = Partial<Record<keyof PipelineInput, string>>;

export type ValidationResult =
  | {
      ok: true;
      data: PipelineInput;
      errors: Record<string, never>;
    }
  | {
      ok: false;
      data: null;
      errors: ValidationErrors;
    };
