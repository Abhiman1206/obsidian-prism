"use client";

import React from "react";
import { useEffect, useMemo, useState } from "react";

type ReportPdfGeneratorProps = {
  technicalPdfUrl: string;
  nonTechnicalPdfUrl: string;
  fallbackPdfUrl: string;
};

type GeneratedPdfUrls = {
  technicalUrl: string;
  nonTechnicalUrl: string;
};

function triggerPdfDownload(url: string, filename: string) {
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.rel = "noopener";
  anchor.style.display = "none";
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
}

async function fetchPdfBlobUrl(url: string): Promise<string> {
  const response = await fetch(url, {
    method: "GET",
    cache: "no-store",
    headers: {
      Accept: "application/pdf",
    },
  });

  if (!response.ok) {
    throw new Error("Unable to generate PDF from report service.");
  }

  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

export function ReportPdfGenerator({
  technicalPdfUrl,
  nonTechnicalPdfUrl,
  fallbackPdfUrl,
}: ReportPdfGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [generatedUrls, setGeneratedUrls] = useState<GeneratedPdfUrls | null>(null);

  const technicalSource = useMemo(
    () => technicalPdfUrl || fallbackPdfUrl,
    [technicalPdfUrl, fallbackPdfUrl],
  );
  const nonTechnicalSource = useMemo(
    () => nonTechnicalPdfUrl || fallbackPdfUrl,
    [nonTechnicalPdfUrl, fallbackPdfUrl],
  );

  useEffect(() => {
    return () => {
      if (generatedUrls?.technicalUrl) {
        URL.revokeObjectURL(generatedUrls.technicalUrl);
      }
      if (generatedUrls?.nonTechnicalUrl) {
        URL.revokeObjectURL(generatedUrls.nonTechnicalUrl);
      }
    };
  }, [generatedUrls]);

  async function handleGeneratePdf() {
    setIsGenerating(true);
    setErrorMessage(null);

    try {
      if (generatedUrls?.technicalUrl) {
        URL.revokeObjectURL(generatedUrls.technicalUrl);
      }
      if (generatedUrls?.nonTechnicalUrl) {
        URL.revokeObjectURL(generatedUrls.nonTechnicalUrl);
      }

      const [technicalUrl, nonTechnicalUrl] = await Promise.all([
        fetchPdfBlobUrl(technicalSource),
        fetchPdfBlobUrl(nonTechnicalSource),
      ]);

      // A single generate action should provide both files immediately.
      triggerPdfDownload(technicalUrl, "technical-report.pdf");
      triggerPdfDownload(nonTechnicalUrl, "non-technical-report.pdf");

      setGeneratedUrls({
        technicalUrl,
        nonTechnicalUrl,
      });
    } catch {
      setErrorMessage("PDF generation failed. Verify backend API is running and try again.");
      setGeneratedUrls(null);
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <section className="report-pdf-section" aria-label="Executive report PDF">
      <h2>Generate Report PDFs</h2>
      <div className="report-pdf-actions">
        <button
          type="button"
          className="btn-primary report-pdf-primary-action"
          onClick={handleGeneratePdf}
          disabled={isGenerating}
          aria-busy={isGenerating}
        >
          {isGenerating ? "Generating PDFs..." : "Generate PDFs"}
        </button>

        {generatedUrls ? (
          <>
            <a href={generatedUrls.technicalUrl} target="_blank" rel="noreferrer" className="report-pdf-link">
              Open Technical PDF
            </a>
            <a href={generatedUrls.nonTechnicalUrl} target="_blank" rel="noreferrer" className="report-pdf-link">
              Open Non-Technical PDF
            </a>
            <a href={generatedUrls.nonTechnicalUrl} download="non-technical-report.pdf" className="report-pdf-link">
              Download Non-Technical PDF
            </a>
          </>
        ) : null}
      </div>

      {errorMessage ? <p>{errorMessage}</p> : null}

      {generatedUrls ? (
        <iframe
          src={generatedUrls.nonTechnicalUrl}
          title="Non-technical report PDF preview"
          className="report-pdf-frame"
        />
      ) : null}
    </section>
  );
}