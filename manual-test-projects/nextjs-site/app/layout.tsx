import type { ReactNode } from "react";

export const metadata = {
  title: "Manual Next.js Skill Resolution Test",
  description: "Minimal fixture for testing Codex skill stack detection.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
