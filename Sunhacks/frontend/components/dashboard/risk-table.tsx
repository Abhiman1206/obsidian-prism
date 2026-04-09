import React from "react";

import { RiskForecast } from "../../lib/contracts";

type RiskTableProps = {
  forecasts: RiskForecast[];
};

export function RiskTable({ forecasts }: RiskTableProps) {
  return (
    <div className="dashboard-risk-table-wrap">
      <table className="dashboard-risk-table" aria-label="Ranked risk components">
        <thead>
          <tr>
            <th scope="col">Component</th>
            <th scope="col">Risk Probability</th>
            <th scope="col">Confidence</th>
            <th scope="col">Top Signal</th>
          </tr>
        </thead>
        <tbody>
          {forecasts.map((forecast) => (
            <tr key={forecast.component_id}>
              <td>{forecast.component_id}</td>
              <td>{Math.round(forecast.risk_probability * 100)}%</td>
              <td>{Math.round(forecast.confidence * 100)}%</td>
              <td>{forecast.top_signals[0]?.signal_name ?? "No supporting signal"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
