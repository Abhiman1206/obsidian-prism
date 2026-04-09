import Link from "next/link";
import { ReactNode } from "react";
import React from "react";

type AppShellProps = {
  children: ReactNode;
};

export default function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-shell" data-testid="app-shell">
      <header className="app-shell__header">
        <div className="app-shell__brand">Predictive Engineering Intelligence</div>
        <nav className="app-shell__nav" aria-label="Primary">
          <Link href="/">Home</Link>
          <Link href="/runs">Runs</Link>
          <Link href="/reports">Reports</Link>
        </nav>
      </header>
      <main className="app-shell__main">{children}</main>
    </div>
  );
}
