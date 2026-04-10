"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import React from "react";

type AppShellProps = {
  children: ReactNode;
};

export default function AppShell({ children }: AppShellProps) {
  const pathname = usePathname() || '/';

  return (
    <div className="app-layout" data-testid="app-shell">
      <aside className="app-sidebar">
        <div className="app-sidebar__brand">
          <span className="brand-icon" aria-hidden="true">
            <svg viewBox="0 0 64 64" role="img" focusable="false">
              <path d="M32 4L53 18L59 44L35 60L10 46L6 33L15 19Z" fill="#f5f5f5" stroke="#050505" strokeWidth="4" strokeLinejoin="round" />
              <path d="M32 4L15 19L6 33L10 46L35 60Z" fill="#050505" />
              <path d="M22 21L17 31L26 26Z" fill="#f5f5f5" />
              <path d="M41 23L49 28" stroke="#050505" strokeWidth="3" strokeLinecap="round" />
              <path d="M44 26L51 31" stroke="#050505" strokeWidth="3" strokeLinecap="round" />
              <path d="M45 45L48 43" stroke="#050505" strokeWidth="3" strokeLinecap="round" />
              <path d="M40 31L44 35L41 40L36 41L34 36L36 31Z" fill="#050505" />
              <path d="M38 34L38 38L41 36Z" fill="#f5f5f5" />
            </svg>
          </span>
          Obsidian Prism
        </div>
        <nav className="app-sidebar__nav" aria-label="Primary">
          <div className="sidebar-group">
            <Link href="/" className={pathname === '/' ? 'active' : ''}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
              Dashboard
            </Link>
            <Link href="/runs" className={pathname === '/runs' ? 'active' : ''}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
              Activity Runs
            </Link>
            <Link href="/repository" className={pathname === '/repository' ? 'active' : ''}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>
              Repo Explorer
            </Link>
            <Link href="/reports" className={pathname === '/reports' ? 'active' : ''}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
              Detailed Reports
            </Link>
            <Link href="/insights" className={pathname === '/insights' ? 'active' : ''}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
              AI Insights
            </Link>
            <Link href="/team" className={pathname === '/team' ? 'active' : ''}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
              Team Hub
            </Link>
          </div>

          <div className="sidebar-subtitle">Tools</div>
          <div className="sidebar-group sidebar-group--tools" aria-label="Tools">
            <button type="button" className="sidebar-tool-btn">Chats</button>
            <button type="button" className="sidebar-tool-btn">Billing</button>
            <button type="button" className="sidebar-tool-btn">Documents</button>
            <button type="button" className="sidebar-tool-btn">Settings</button>
          </div>

          <button type="button" className="sidebar-logout-btn">Logout</button>
        </nav>
      </aside>
      <main className="app-main">
        <header className="top-nav glass-panel" role="banner">
          <div className="top-nav__search-wrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input type="search" placeholder="Search patients, visits, notes..." aria-label="Search" />
          </div>

          <div className="top-nav__tabs" role="tablist" aria-label="Filter tabs">
            <button type="button" className="top-tab is-active" role="tab" aria-selected="true">All</button>
            <button type="button" className="top-tab" role="tab" aria-selected="false">High Risk</button>
            <button type="button" className="top-tab" role="tab" aria-selected="false">Recent</button>
          </div>

          <div className="top-nav__actions" aria-label="Top bar actions">
            <button type="button" className="icon-btn" aria-label="Notifications">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
            </button>
            <button type="button" className="icon-btn" aria-label="Settings">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33h.01a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h.01a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v.01a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            </button>
            <button type="button" className="profile-chip" aria-label="Profile">
              <span className="profile-avatar">AP</span>
              <span>Profile</span>
            </button>
          </div>
        </header>
        <div className="app-main__content">{children}</div>
      </main>
    </div>
  );
}
