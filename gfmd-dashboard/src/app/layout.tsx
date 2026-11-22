import type { Metadata } from "next";
import "./globals.css";
import { NavHeader } from "@/components/nav-header";

export const metadata: Metadata = {
  title: "GFMD Email Automation Dashboard",
  description: "Real-time monitoring of outreach campaigns",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <NavHeader />
        {children}
      </body>
    </html>
  );
}
