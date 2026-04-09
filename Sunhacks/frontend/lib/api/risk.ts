import { RiskForecast } from "../contracts";

export type RiskDashboardSummary = {
  totalComponents: number;
  highRiskCount: number;
  averageConfidencePercent: number;
};

const HIGH_RISK_THRESHOLD = 0.6;

export async function getRiskForecasts(runId: string = "latest"): Promise<RiskForecast[]> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

  try {
    const response = await fetch(`${baseUrl}/api/risk-forecasts/${runId}`, {
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      return [];
    }

    const payload = (await response.json()) as RiskForecast[];
    if (!Array.isArray(payload)) {
      return [];
    }

    return [...payload].sort((left, right) => right.risk_probability - left.risk_probability);
  } catch {
    return [];
  }
}

export function buildRiskDashboardSummary(forecasts: RiskForecast[]): RiskDashboardSummary {
  if (forecasts.length === 0) {
    return {
      totalComponents: 0,
      highRiskCount: 0,
      averageConfidencePercent: 0,
    };
  }

  const totalConfidence = forecasts.reduce((sum, forecast) => sum + forecast.confidence, 0);

  return {
    totalComponents: forecasts.length,
    highRiskCount: forecasts.filter((forecast) => forecast.risk_probability >= HIGH_RISK_THRESHOLD).length,
    averageConfidencePercent: Math.round((totalConfidence / forecasts.length) * 100),
  };
}
