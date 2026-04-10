import React from "react";
import { analyzeRepository } from "../../lib/api/repositories";

type InsightsPageProps = {
  searchParams?: Promise<{
    repository_url?: string | string[];
  }>;
};

function normalizeRepositoryUrl(raw: string | string[] | undefined): string | null {
  const value = Array.isArray(raw) ? raw[0] : raw;
  const trimmed = value?.trim();
  return trimmed && trimmed.length > 0 ? trimmed : null;
}

function buildFaultHeatmap(commitDates: string[]): number[] {
  const buckets = Array.from({ length: 25 }, () => 0);
  const now = Date.now();

  for (const dateValue of commitDates) {
    const parsed = new Date(dateValue);
    if (Number.isNaN(parsed.getTime())) {
      continue;
    }
    const days = Math.floor((now - parsed.getTime()) / (1000 * 60 * 60 * 24));
    if (days < 0 || days > 180) {
      continue;
    }
    const index = Math.min(24, Math.floor(days / 8));
    buckets[index] = Math.min(3, buckets[index] + 1);
  }

  return buckets;
}

function heatColor(level: number): string {
  if (level >= 3) {
    return "rgba(239, 68, 68, 0.6)";
  }
  if (level === 2) {
    return "rgba(249, 115, 22, 0.45)";
  }
  if (level === 1) {
    return "rgba(16, 185, 129, 0.3)";
  }
  return "rgba(255,255,255,0.08)";
}

function formatDate(value: string | null): string {
  if (!value) {
    return "unknown";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return "unknown";
  }
  return parsed.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export default async function InsightsHubPage({ searchParams }: InsightsPageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const repositoryUrl = normalizeRepositoryUrl(resolvedSearchParams.repository_url);
  const analysis = repositoryUrl ? await analyzeRepository(repositoryUrl) : null;

  if (!analysis) {
    return (
      <section>
        <div className="page-header">
          <h1>AI & Insights Hub</h1>
          <p>
            Deep-dive analytics and <span className="text-neon">Conversational Intelligence</span>.
          </p>
        </div>
        <div className="glass-panel" style={{ padding: "1rem" }}>
          <p style={{ margin: 0 }}>
            {repositoryUrl
              ? "Insights are unavailable because repository analysis could not be loaded from backend."
              : "Provide a repository URL to load insights for your repository of choice."}
          </p>
        </div>
      </section>
    );
  }

  const commitDates = analysis.recent_commits
    .map((commit) => commit.committed_at)
    .filter((value): value is string => Boolean(value));
  const heatmapLevels = buildFaultHeatmap(commitDates);
  const integrity = analysis.health.score;
  const debtPercent = Math.max(0, 100 - integrity);

  const topLanguage = analysis.languages[0]?.language ?? "unknown";
  const topLanguagePct = analysis.languages[0]?.percentage ?? 0;
  const newestCommit = analysis.recent_commits[0];

  return (
    <section>
      <div className="page-header">
        <h1>AI & Insights Hub</h1>
        <p>
          Deep-dive analytics and <span className="text-neon">Conversational Intelligence</span> for {analysis.repository_name}.
        </p>
      </div>

      <div style={{ display: 'flex', gap: '1.5rem', minHeight: '65vh' }}>
        
        {/* Left Side: Deep Dive Analytics */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ margin: '0 0 1rem 0', fontWeight: 600 }}>System Integrity</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: `conic-gradient(var(--success) ${integrity}%, rgba(255,255,255,0.1) 0)`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ background: 'var(--bg-start)', width: '64px', height: '64px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>{integrity}%</div>
              </div>
              <div style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>
                Repository health score is {integrity}%. Estimated technical debt signal is {debtPercent}% based on current health model.
              </div>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '1.5rem', flex: 1 }}>
            <h3 style={{ margin: '0 0 1rem 0', fontWeight: 600 }}>Predictive Heatmap</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '4px' }}>
              {heatmapLevels.map((level, i) => (
                <div key={i} style={{ aspectRatio: '1', background: heatColor(level), borderRadius: '4px' }}></div>
              ))}
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--muted)', marginTop: '1rem', textAlign: 'center' }}>
              Projected fault distribution from recent commit recency.
            </p>
          </div>
        </div>

        {/* Right Side: Conversational UI */}
        <div className="glass-panel" style={{ flex: 2, display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--surface-border)' }}>
            <h3 style={{ margin: 0, fontWeight: 600 }}>Copilot Assistant</h3>
          </div>
          
          <div style={{ flex: 1, padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', overflowY: 'auto' }}>
            {/* Chat Bubble AI */}
            <div style={{ alignSelf: 'flex-start', maxWidth: '80%', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', padding: '1rem', borderRadius: '12px 12px 12px 0' }}>
              <p style={{ margin: 0, fontSize: '0.9rem', lineHeight: '1.5' }}>
                I analyzed <span className="text-neon">{analysis.repository_name}</span>. The strongest language signal is {topLanguage} ({topLanguagePct.toFixed(2)}%).
                Current health score is {analysis.health.score}/100.
              </p>
            </div>
            
            {/* Chat Bubble User */}
            <div style={{ alignSelf: 'flex-end', maxWidth: '80%', background: 'var(--surface-hover)', border: '1px solid var(--surface-border)', padding: '1rem', borderRadius: '12px 12px 0 12px', color: 'var(--muted)' }}>
              <p style={{ margin: 0, fontSize: '0.9rem', lineHeight: '1.5' }}>
                Show me the most recent repository activity and what it implies for engineering risk.
              </p>
            </div>
            
             {/* Chat Bubble AI */}
             <div style={{ alignSelf: 'flex-start', maxWidth: '80%', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', padding: '1rem', borderRadius: '12px 12px 12px 0' }}>
              <p style={{ margin: 0, fontSize: '0.9rem', lineHeight: '1.5' }}>
                Latest commit: <code>{newestCommit?.message ?? 'No recent commit available'}</code> by <code>{newestCommit?.author ?? 'unknown'}</code> on <code>{formatDate(newestCommit?.committed_at ?? null)}</code>. <br /><br />
                Last repository push was <code>{formatDate(analysis.pushed_at)}</code> with {analysis.open_issues} open issues and {analysis.contributor_count} contributors.
              </p>
            </div>
          </div>
          
          {/* Chat Input */}
          <div style={{ padding: '1rem', borderTop: '1px solid var(--surface-border)' }}>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input 
                type="text" 
                placeholder="Ask about project risks, code health, or team velocity..." 
                style={{ flex: 1, background: 'rgba(0,0,0,0.2)', border: '1px solid var(--surface-border)', borderRadius: '8px', padding: '0.8rem 1rem', color: 'white', outline: 'none' }} 
              />
              <button className="btn-primary" style={{ padding: '0.8rem 1.5rem' }}>Send</button>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
