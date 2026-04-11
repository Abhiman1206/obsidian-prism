import type { Metadata } from "next";
import AppShell from "../components/layout/app-shell";
import { Suspense } from "react";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Predictive Engineering Intelligence",
  description: "Executive engineering risk intelligence platform",
};

type RootLayoutProps = {
  children: React.ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body>
        <Suspense fallback={<div />}>
          <AppShell>{children}</AppShell>
        </Suspense>
      </body>
    </html>
  );
}
