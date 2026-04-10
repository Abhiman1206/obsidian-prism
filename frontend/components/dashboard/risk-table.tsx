import React from "react";

import { RiskForecast } from "../../lib/contracts";

type RiskTableProps = {
  forecasts: RiskForecast[];
};

function getProbabilityLabel(prob: number) {
  if (prob > 0.7) return { label: "High", className: "pill high" };
  if (prob > 0.4) return { label: "Medium", className: "pill medium" };
  return { label: "Low", className: "pill low" };
}

export function RiskTable({ forecasts }: RiskTableProps) {
  return (
    <div className="table-container">
      <table className="glass-table" aria-label="Ranked risk components">
        <thead>
          <tr>
            <th scope="col">Component</th>
            <th scope="col">Risk Level</th>
            <th scope="col">Confidence</th>
            <th scope="col">Top Signal</th>
          </tr>
        </thead>
        <tbody>
          {forecasts.map((forecast) => {
            const prob = getProbabilityLabel(forecast.risk_probability);
            return (
              <tr key={forecast.component_id}>
                <td style={{ fontWeight: 500, color: 'var(--text)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: prob.className.includes('high') ? 'var(--danger)' : prob.className.includes('medium') ? 'var(--accent)' : 'var(--success)' }}></div>
                    {forecast.component_id}
                  </div>
                </td>
                <td>
                  <span className={prob.className}>
                    {prob.label} ({Math.round(forecast.risk_probability * 100)}%)
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ flex: 1, height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', width: '60px' }}>
                      <div style={{ width: `${forecast.confidence * 100}%`, height: '100%', background: 'var(--primary)', borderRadius: '2px' }}></div>
                    </div>
                    <span>{Math.round(forecast.confidence * 100)}%</span>
                  </div>
                </td>
                <td style={{ color: 'var(--muted)' }}>
                  {forecast.top_signals[0]?.signal_name ?? "No supporting signal"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
