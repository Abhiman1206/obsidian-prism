import type {
  PipelineInput,
  PipelineMode,
  ValidationErrors,
  ValidationResult,
} from "./types";

const ALLOWED_MODES: PipelineMode[] = ["crewai", "langgraph"];

function normalizeText(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

export function validatePipelineInput(raw: {
  applicant_id: unknown;
  document_id: unknown;
  mode: unknown;
}): ValidationResult {
  const errors: ValidationErrors = {};
  const applicantId = normalizeText(raw.applicant_id);
  const documentId = normalizeText(raw.document_id);
  const mode = normalizeText(raw.mode);

  if (!applicantId) {
    errors.applicant_id = "Applicant ID is required.";
  }

  if (!documentId) {
    errors.document_id = "Document ID is required.";
  }

  if (!mode) {
    errors.mode = "Mode is required.";
  } else if (!ALLOWED_MODES.includes(mode as PipelineMode)) {
    errors.mode = "Mode must be either crewai or langgraph.";
  }

  if (Object.keys(errors).length > 0) {
    return {
      ok: false,
      data: null,
      errors,
    };
  }

  return {
    ok: true,
    data: {
      applicant_id: applicantId,
      document_id: documentId,
      mode: mode as PipelineMode,
    },
    errors: {},
  };
}

export function emptyValidationErrors(): ValidationErrors {
  return {};
}

export function toInitialInput(): PipelineInput {
  return {
    applicant_id: "",
    document_id: "",
    mode: "crewai",
  };
}
