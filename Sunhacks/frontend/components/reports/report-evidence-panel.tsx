"use client";

import React, { useMemo, useState } from "react";

import { ExecutiveReportClaim } from "../../lib/contracts";

type ReportEvidencePanelProps = {
  claims: ExecutiveReportClaim[];
};

export function ReportEvidencePanel({ claims }: ReportEvidencePanelProps) {
  const [expandedClaimId, setExpandedClaimId] = useState<string | null>(null);

  const activeClaim = useMemo(
    () => claims.find((claim) => claim.claim_id === expandedClaimId) ?? null,
    [claims, expandedClaimId],
  );

  return (
    <section aria-label="Report evidence panel" className="report-evidence-panel">
      <h2>Evidence and Lineage</h2>
      {claims.length === 0 ? (
        <p>No claim evidence is available for this report.</p>
      ) : (
        <div>
          <ul>
            {claims.map((claim) => (
              <li key={claim.claim_id}>
                <button
                  type="button"
                  aria-label={`Toggle evidence for ${claim.claim_id}`}
                  onClick={() => {
                    setExpandedClaimId((current) => (current === claim.claim_id ? null : claim.claim_id));
                  }}
                >
                  {claim.claim_id}
                </button>
              </li>
            ))}
          </ul>

          {activeClaim ? (
            <article>
              <h3>{activeClaim.claim_id}</h3>
              <p>{activeClaim.claim_text}</p>
              <ul>
                {activeClaim.lineage_refs.map((reference) => (
                  <li key={reference}>{reference}</li>
                ))}
              </ul>
            </article>
          ) : null}
        </div>
      )}
    </section>
  );
}
