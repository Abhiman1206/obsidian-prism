"use client";

import React from "react";
import { FormEvent, useMemo, useState } from "react";

import { registerRepository, revalidateRepositoryAccess } from "../lib/api/repositories";
import { createRun } from "../lib/api/runs";
import { AuthorizationReason, Provider } from "../lib/contracts";

type Props = {
  defaultRepositoryUrl: string;
};

function deriveRepositoryName(url: string): string {
  const trimmed = url.trim();
  if (!trimmed) {
    return "";
  }

  const sanitized = trimmed.replace(/\.git$/i, "");
  const parts = sanitized.split("/").filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[parts.length - 2]}/${parts[parts.length - 1]}`;
  }
  return sanitized;
}

export function PrivateRepoConsole({ defaultRepositoryUrl }: Props) {
  const [provider, setProvider] = useState<Provider>("github");
  const [repositoryUrl, setRepositoryUrl] = useState(defaultRepositoryUrl);
  const [repositoryName, setRepositoryName] = useState(deriveRepositoryName(defaultRepositoryUrl));
  const [branch, setBranch] = useState("main");
  const [token, setToken] = useState("");
  const [scopesInput, setScopesInput] = useState("repo");
  const [repositoryId, setRepositoryId] = useState("");
  const [runReady, setRunReady] = useState(false);
  const [authorizationReason, setAuthorizationReason] = useState<AuthorizationReason | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const scopes = useMemo(
    () => scopesInput.split(",").map((scope) => scope.trim()).filter(Boolean),
    [scopesInput],
  );

  async function onRegister(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setStatusMessage(null);

    if (!token.trim() || !repositoryUrl.trim() || !repositoryName.trim()) {
      setErrorMessage("Repository URL, repository name, and access token are required.");
      return;
    }

    if (scopes.length === 0) {
      setErrorMessage("At least one scope is required.");
      return;
    }

    setIsSubmitting(true);
    const result = await registerRepository({
      provider,
      repository_url: repositoryUrl.trim(),
      repository_name: repositoryName.trim(),
      auth: {
        provider,
        access_token: token.trim(),
        scopes,
      },
    });
    setIsSubmitting(false);

    if (!result) {
      setErrorMessage("Failed to register repository. Verify provider token and try again.");
      return;
    }

    setRepositoryId(result.repository_id);
    setRunReady(result.run_ready);
    setAuthorizationReason(result.authorization_reason);
    if (result.run_ready) {
      setStatusMessage(
        `Repository registered: ${result.repository_id}. Collaborator access is authorized; ready for analysis run.`,
      );
      return;
    }

    setErrorMessage(
      `Repository registered, but collaborator access is not ready (${result.authorization_reason}). Add this user as collaborator and re-check access.`,
    );
  }

  async function onRecheckAccess() {
    setErrorMessage(null);
    setStatusMessage(null);

    if (!repositoryId.trim()) {
      setErrorMessage("Repository ID is required.");
      return;
    }

    setIsSubmitting(true);
    const result = await revalidateRepositoryAccess({
      repository_id: repositoryId.trim(),
      provider,
    });
    setIsSubmitting(false);

    if (!result) {
      setErrorMessage("Failed to re-check access. Ensure ownership and repository ID are correct.");
      return;
    }

    setRunReady(result.run_ready);
    setAuthorizationReason(result.authorization_reason);
    if (result.run_ready) {
      setStatusMessage("Collaborator access is now authorized. You can trigger the analysis run.");
      return;
    }

    setErrorMessage(`Access is still not ready (${result.authorization_reason}).`);
  }

  async function onTriggerRun() {
    setErrorMessage(null);
    setStatusMessage(null);

    if (!repositoryId.trim()) {
      setErrorMessage("Register a repository first, or paste a valid repository ID.");
      return;
    }

    if (!runReady) {
      setErrorMessage("Collaborator access is not authorized yet. Re-check access first.");
      return;
    }

    setIsSubmitting(true);
    const run = await createRun({
      repository_id: repositoryId.trim(),
      provider,
      branch: branch.trim() || undefined,
    });
    setIsSubmitting(false);

    if (!run) {
      setErrorMessage("Failed to trigger run. Please retry.");
      return;
    }

    const params = new URLSearchParams({
      run_id: run.run_id,
      repository_url: repositoryUrl.trim(),
    });
    window.location.assign(`/runs?${params.toString()}`);
  }

  return (
    <div className="glass-panel" style={{ padding: "1rem", marginBottom: "1rem" }}>
      <h2 style={{ marginTop: 0, marginBottom: "0.5rem" }}>Private Repository Connect and Analyze</h2>
      <p style={{ marginTop: 0, color: "var(--muted)", marginBottom: "1rem" }}>
        Register provider credentials, then manually trigger analysis and follow a real run ID.
      </p>

      <form onSubmit={onRegister} style={{ display: "grid", gap: "0.75rem" }}>
        <div style={{ display: "grid", gap: "0.5rem", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
          <label style={{ display: "grid", gap: "0.35rem" }}>
            <span>Provider</span>
            <select
              value={provider}
              onChange={(event) => setProvider(event.target.value as Provider)}
              style={{
                background: "rgba(0,0,0,0.2)",
                border: "1px solid var(--surface-border)",
                borderRadius: "8px",
                padding: "0.65rem 0.8rem",
                color: "var(--text)",
              }}
            >
              <option value="github">GitHub</option>
              <option value="gitlab">GitLab</option>
            </select>
          </label>

          <label style={{ display: "grid", gap: "0.35rem" }}>
            <span>Branch</span>
            <input
              value={branch}
              onChange={(event) => setBranch(event.target.value)}
              placeholder="main"
              style={{
                background: "rgba(0,0,0,0.2)",
                border: "1px solid var(--surface-border)",
                borderRadius: "8px",
                padding: "0.65rem 0.8rem",
                color: "var(--text)",
              }}
            />
          </label>
        </div>

        <label style={{ display: "grid", gap: "0.35rem" }}>
          <span>Repository URL</span>
          <input
            value={repositoryUrl}
            onChange={(event) => {
              const value = event.target.value;
              setRepositoryUrl(value);
              if (!repositoryName.trim()) {
                setRepositoryName(deriveRepositoryName(value));
              }
            }}
            placeholder="https://github.com/org/repo"
            style={{
              background: "rgba(0,0,0,0.2)",
              border: "1px solid var(--surface-border)",
              borderRadius: "8px",
              padding: "0.65rem 0.8rem",
              color: "var(--text)",
            }}
          />
        </label>

        <label style={{ display: "grid", gap: "0.35rem" }}>
          <span>Repository Name (owner/repo)</span>
          <input
            value={repositoryName}
            onChange={(event) => setRepositoryName(event.target.value)}
            placeholder="org/repo"
            style={{
              background: "rgba(0,0,0,0.2)",
              border: "1px solid var(--surface-border)",
              borderRadius: "8px",
              padding: "0.65rem 0.8rem",
              color: "var(--text)",
            }}
          />
        </label>

        <label style={{ display: "grid", gap: "0.35rem" }}>
          <span>Provider Token</span>
          <input
            type="password"
            value={token}
            onChange={(event) => setToken(event.target.value)}
            autoComplete="off"
            placeholder="Paste PAT/token"
            style={{
              background: "rgba(0,0,0,0.2)",
              border: "1px solid var(--surface-border)",
              borderRadius: "8px",
              padding: "0.65rem 0.8rem",
              color: "var(--text)",
            }}
          />
        </label>

        <label style={{ display: "grid", gap: "0.35rem" }}>
          <span>Token Scopes (comma separated)</span>
          <input
            value={scopesInput}
            onChange={(event) => setScopesInput(event.target.value)}
            placeholder={provider === "github" ? "repo,read:org" : "api,read_repository"}
            style={{
              background: "rgba(0,0,0,0.2)",
              border: "1px solid var(--surface-border)",
              borderRadius: "8px",
              padding: "0.65rem 0.8rem",
              color: "var(--text)",
            }}
          />
        </label>

        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <button type="submit" className="btn-primary" disabled={isSubmitting}>
            {isSubmitting ? "Registering..." : "Connect Private Repository"}
          </button>
          <button
            type="button"
            className="btn-primary"
            disabled={isSubmitting}
            onClick={onRecheckAccess}
            style={{ background: "linear-gradient(135deg, #0f7ed8, #19a5ff)" }}
          >
            {isSubmitting ? "Checking..." : "Re-check Collaborator Access"}
          </button>
          <button
            type="button"
            className="btn-primary"
            disabled={isSubmitting || !runReady}
            onClick={onTriggerRun}
            style={{ background: "linear-gradient(135deg, var(--accent), #13c4ff)" }}
          >
            {isSubmitting ? "Starting..." : "Trigger Analysis Run"}
          </button>
        </div>
      </form>

      <div style={{ marginTop: "0.9rem", display: "grid", gap: "0.4rem" }}>
        <label style={{ display: "grid", gap: "0.35rem" }}>
          <span>Repository ID</span>
          <input
            value={repositoryId}
            onChange={(event) => setRepositoryId(event.target.value)}
            placeholder="repo-your-project"
            style={{
              background: "rgba(0,0,0,0.2)",
              border: "1px solid var(--surface-border)",
              borderRadius: "8px",
              padding: "0.65rem 0.8rem",
              color: "var(--text)",
            }}
          />
        </label>

        {statusMessage ? <p style={{ margin: 0, color: "var(--success)" }}>{statusMessage}</p> : null}
        {authorizationReason ? (
          <p style={{ margin: 0, color: "var(--muted)" }}>Authorization reason: {authorizationReason}</p>
        ) : null}
        {errorMessage ? <p style={{ margin: 0, color: "#ef4444" }}>{errorMessage}</p> : null}
      </div>
    </div>
  );
}
