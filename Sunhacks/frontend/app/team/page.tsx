import React from "react";
import { analyzeRepository } from "../../lib/api/repositories";

type TeamPageProps = {
  searchParams?: Promise<{
    repository_url?: string | string[];
  }>;
};

function normalizeRepositoryUrl(raw: string | string[] | undefined): string | null {
  const value = Array.isArray(raw) ? raw[0] : raw;
  const trimmed = value?.trim();
  return trimmed && trimmed.length > 0 ? trimmed : null;
}

function toTitleCase(value: string): string {
  if (!value) {
    return "Unknown";
  }
  return value
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}

function inferRole(author: string): string {
  const normalized = author.toLowerCase();
  if (normalized.includes("bot")) {
    return "Automation";
  }
  if (normalized.includes("security")) {
    return "Security Contributor";
  }
  return "Repository Contributor";
}

function formatDate(value: string | null): string {
  if (!value) {
    return "Unknown";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return "Unknown";
  }
  return parsed.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function daysSince(value: string | null): number | null {
  if (!value) {
    return null;
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  const diffMs = Date.now() - parsed.getTime();
  return Math.max(0, Math.floor(diffMs / (1000 * 60 * 60 * 24)));
}

function contributorHealth(score: number): "Optimal" | "Warning" {
  return score >= 70 ? "Optimal" : "Warning";
}

function buildVelocityGrid(commitDates: string[]): number[] {
  const levels: number[] = Array.from({ length: 90 }, () => 0);
  const now = Date.now();

  for (const dateValue of commitDates) {
    const parsed = new Date(dateValue);
    if (Number.isNaN(parsed.getTime())) {
      continue;
    }

    const diffDays = Math.floor((now - parsed.getTime()) / (1000 * 60 * 60 * 24));
    if (diffDays < 0 || diffDays >= 90) {
      continue;
    }

    const index = 89 - diffDays;
    levels[index] = Math.min(3, levels[index] + 1);
  }

  return levels;
}

function velocityColor(level: number): string {
  if (level >= 3) {
    return "var(--neon)";
  }
  if (level === 2) {
    return "var(--primary)";
  }
  if (level === 1) {
    return "rgba(59, 130, 246, 0.35)";
  }
  return "rgba(255,255,255,0.06)";
}

export default async function TeamHubPage({ searchParams }: TeamPageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const repositoryUrl = normalizeRepositoryUrl(resolvedSearchParams.repository_url);
  const analysis = repositoryUrl ? await analyzeRepository(repositoryUrl) : null;

  if (!analysis) {
    return (
      <section>
        <div className="page-header">
          <h1>Team Collaboration Hub</h1>
          <p>
            Project overview focused on <span className="text-neon">Team Health & Velocity</span>.
          </p>
        </div>

        <div className="glass-panel" style={{ padding: "1rem" }}>
          <p style={{ margin: 0 }}>
            {repositoryUrl
              ? "Team analytics could not be generated from repository analysis. Verify the repository is reachable and backend API is running."
              : "Provide a repository URL to load team analytics for your selected repository."}
          </p>
        </div>
      </section>
    );
  }

  const commitCounts = new Map<string, number>();
  for (const commit of analysis.recent_commits) {
    const key = commit.author?.trim() || "Unknown";
    commitCounts.set(key, (commitCounts.get(key) ?? 0) + 1);
  }

  const teamMembers = Array.from(commitCounts.entries())
    .map(([name, commits]) => ({
      name,
      role: inferRole(name),
      commits,
      health: contributorHealth(analysis.health.score),
      avatar: name.charAt(0).toUpperCase() || "?",
    }))
    .sort((left, right) => right.commits - left.commits);

  const commitDates = analysis.recent_commits
    .map((commit) => commit.committed_at)
    .filter((value): value is string => Boolean(value));
  const velocityLevels = buildVelocityGrid(commitDates);

  const pushAge = daysSince(analysis.pushed_at);
  const recentPush = pushAge !== null && pushAge <= 14;

  return (
    <section>
      <div className="page-header">
        <h1>Team Collaboration Hub</h1>
        <p>Project overview focused on <span className="text-neon">Team Health & Velocity</span>.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '1.5rem', marginBottom: '1.5rem' }}>
        
        {/* Active Members */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ margin: '0 0 1.5rem 0', fontWeight: 600 }}>Active Members</h3>
          {teamMembers.length === 0 ? (
            <p style={{ margin: 0, color: 'var(--muted)' }}>No contributor activity found in recent commits.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {teamMembers.map((m, i) => (
                <div key={m.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '1rem', borderBottom: i !== teamMembers.length - 1 ? '1px solid var(--surface-border)' : 'none' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--primary), var(--neon))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                      {m.avatar}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600 }}>{toTitleCase(m.name)}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>{m.role}</div>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 'bold' }}>{m.commits} Commits</div>
                    <div style={{ fontSize: '0.8rem', color: m.health === 'Optimal' ? 'var(--success)' : 'var(--accent)' }}>{m.health}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Milestone Timeline */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ margin: '0 0 1.5rem 0', fontWeight: 600 }}>Project Milestones</h3>
          <div style={{ position: 'relative', paddingLeft: '1.5rem' }}>
            {/* Context Line */}
            <div style={{ position: 'absolute', left: '6px', top: '0', bottom: '0', width: '2px', background: 'linear-gradient(180deg, var(--success) 0%, var(--primary) 50%, var(--surface-border) 100%)' }}></div>
            
            {/* Timeline Items */}
            <div style={{ position: 'relative', marginBottom: '2rem' }}>
              <div style={{ position: 'absolute', left: '-1.85rem', top: '0.2rem', width: '14px', height: '14px', borderRadius: '50%', background: 'var(--success)', border: '3px solid var(--bg-start)', boxShadow: '0 0 10px var(--success)' }}></div>
              <h4 style={{ margin: '0 0 0.25rem 0' }}>Repository Analysis Connected</h4>
              <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--muted)' }}>
                Active source: {analysis.repository_name}.
              </p>
            </div>
            
            <div style={{ position: 'relative', marginBottom: '2rem' }}>
              <div style={{ position: 'absolute', left: '-1.85rem', top: '0.2rem', width: '14px', height: '14px', borderRadius: '50%', background: 'var(--primary)', border: '3px solid var(--bg-start)', boxShadow: '0 0 10px var(--primary)' }}></div>
              <h4 style={{ margin: '0 0 0.25rem 0' }}>Repository Health Tracking</h4>
              <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text)' }}>
                Health score {analysis.health.score}/100. Last push: {formatDate(analysis.pushed_at)}.
              </p>
            </div>
            
            <div style={{ position: 'relative' }}>
              <div style={{ position: 'absolute', left: '-1.85rem', top: '0.2rem', width: '14px', height: '14px', borderRadius: '50%', background: recentPush ? 'var(--success)' : 'var(--surface-border)', border: '3px solid var(--bg-start)' }}></div>
              <h4 style={{ margin: '0 0 0.25rem 0', color: recentPush ? 'var(--text)' : 'var(--muted)' }}>
                Commit Velocity Window
              </h4>
              <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--muted)' }}>
                {recentPush ? 'Recent activity detected within the last 14 days.' : 'No very recent push detected; monitor activity trend.'}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Activity Heatmap */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 style={{ margin: '0 0 1.5rem 0', fontWeight: 600 }}>Velocity Heatmap</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(30, 1fr)', gap: '4px' }}>
          {velocityLevels.map((level, i) => {
            const bg = velocityColor(level);
            return (
              <div key={i} style={{ aspectRatio: '1', background: bg, borderRadius: '2px' }}></div>
            );
          })}
        </div>
        <p style={{ fontSize: '0.8rem', color: 'var(--muted)', marginTop: '1rem', textAlign: 'center' }}>Last 90 Days</p>
      </div>

    </section>
  );
}
