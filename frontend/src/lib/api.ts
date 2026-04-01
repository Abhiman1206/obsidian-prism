import type { PipelineInput, PipelineResult } from "./types";
import { runtimeEnv } from "../config/env";

type ApiTransport = (input: PipelineInput) => Promise<PipelineResult>;

type RuntimeHealth = {
  status: string;
  service?: string;
};

type RuntimeReadiness = {
  status: string;
  checks: Record<string, boolean>;
};

type RuntimeErrorEnvelope = PipelineResult["error"];

const { runtimeApiUrl, useMock, requestTimeoutMs } = runtimeEnv;

function timeoutSignal(timeoutMs: number): {
  signal?: AbortSignal;
  clear: () => void;
} {
  if (typeof AbortController === "undefined") {
    return { clear: () => {} };
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort();
  }, timeoutMs);

  return {
    signal: controller.signal,
    clear: () => {
      clearTimeout(timeoutId);
    },
  };
}

function extractErrorEnvelope(payload: unknown, fallbackCode: string, fallbackMessage: string): RuntimeErrorEnvelope {
  if (typeof payload === "object" && payload !== null) {
    const envelope = payload as {
      error?: {
        code?: unknown;
        message?: unknown;
        failure_category?: unknown;
        retry_count?: unknown;
        stage?: unknown;
      };
      detail?: unknown;
    };

    if (envelope.error && typeof envelope.error === "object") {
      const code = typeof envelope.error.code === "string" ? envelope.error.code : fallbackCode;
      const message =
        typeof envelope.error.message === "string" ? envelope.error.message : fallbackMessage;

      return {
        code,
        message,
        failure_category:
          typeof envelope.error.failure_category === "string"
            ? envelope.error.failure_category
            : undefined,
        retry_count:
          typeof envelope.error.retry_count === "number"
            ? envelope.error.retry_count
            : undefined,
        stage: typeof envelope.error.stage === "string" ? envelope.error.stage : undefined,
      };
    }

    if (typeof envelope.detail === "string") {
      return {
        code: fallbackCode,
        message: envelope.detail,
      };
    }
  }

  return {
    code: fallbackCode,
    message: fallbackMessage,
  };
}

async function parseJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

async function callRuntime(path: string, init?: RequestInit): Promise<Response> {
  const timeout = timeoutSignal(requestTimeoutMs);
  try {
    return await fetch(`${runtimeApiUrl}${path}`, {
      ...init,
      signal: timeout.signal,
    });
  } finally {
    timeout.clear();
  }
}

function createMockResult(input: PipelineInput): PipelineResult {
  const shouldFail = input.document_id.toLowerCase().includes("fail");

  if (shouldFail) {
    return {
      status: "failure",
      decision: "declined",
      mode: input.mode,
      stages: {
        validation: { status: "ok" },
        credit: { status: "ok" },
        risk: { status: "failed" },
      },
      error: {
        code: "MISSION_REPORT",
        message: "Risk checks failed for submitted document.",
        details: {
          document_id: input.document_id,
        },
      },
    };
  }

  return {
    status: "success",
    decision: "approved",
    mode: input.mode,
    stages: {
      validation: { status: "ok" },
      credit: { status: "ok" },
      risk: { status: "ok" },
      compliance: { status: "ok" },
    },
    error: null,
  };
}

async function mockTransport(input: PipelineInput): Promise<PipelineResult> {
  await new Promise((resolve) => {
    setTimeout(resolve, 120);
  });
  return createMockResult(input);
}

async function networkTransport(input: PipelineInput): Promise<PipelineResult> {
  let response: Response;

  try {
    response = await callRuntime("/run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(input),
    });
  } catch {
    return {
      status: "failure",
      decision: "unknown",
      mode: input.mode,
      stages: {},
      error: {
        code: "NETWORK_ERROR",
        message: `Unable to reach runtime at ${runtimeApiUrl}.`,
      },
    };
  }

  const payload = await parseJson(response);

  if (!response.ok) {
    const error = extractErrorEnvelope(
      payload,
      "HTTP_ERROR",
      `Runtime request failed with status ${response.status}.`
    );

    return {
      status: "failure",
      decision: "unknown",
      mode: input.mode,
      stages: {},
      error,
    };
  }

  return payload as PipelineResult;
}

export async function fetchHealth(): Promise<RuntimeHealth> {
  let response: Response;
  try {
    response = await callRuntime("/health");
  } catch {
    return {
      status: "unreachable",
    };
  }
  const payload = await parseJson(response);

  if (!response.ok || typeof payload !== "object" || payload === null) {
    return {
      status: "unreachable",
    };
  }

  return payload as RuntimeHealth;
}

export async function fetchReadiness(): Promise<RuntimeReadiness> {
  let response: Response;
  try {
    response = await callRuntime("/readiness");
  } catch {
    return {
      status: "not_ready",
      checks: {
        runtime_api: false,
      },
    };
  }
  const payload = await parseJson(response);

  if (
    !response.ok ||
    typeof payload !== "object" ||
    payload === null ||
    typeof (payload as { status?: unknown }).status !== "string"
  ) {
    return {
      status: "not_ready",
      checks: {
        runtime_api: false,
      },
    };
  }

  const parsed = payload as RuntimeReadiness;
  return {
    status: parsed.status,
    checks: parsed.checks ?? { runtime_api: false },
  };
}

export async function submitPipeline(
  input: PipelineInput,
  transport?: ApiTransport
): Promise<PipelineResult> {
  const sender = transport ?? (useMock ? mockTransport : networkTransport);
  return sender(input);
}
