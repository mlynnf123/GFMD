import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GFMD Email Automation Dashboard",
  description: "Real-time monitoring of law enforcement outreach campaigns",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
