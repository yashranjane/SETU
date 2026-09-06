import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SETU | Innovation Procurement OS",
  description:
    "Smart India Hackathon Innovation Procurement OS bridging government challenges with breakthrough startup solutions.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 antialiased">{children}</body>
    </html>
  );
}
