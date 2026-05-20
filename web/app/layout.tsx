import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { Providers } from "@/components/providers";
import { SiteHeader } from "@/components/site-header";

import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Review Intelligence — App Store insights",
  description:
    "Paste an App Store URL to fetch written reviews and generate a ranked insight report.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} h-full`}
      style={
        {
          "--font-sans":
            'var(--font-inter), -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", system-ui, sans-serif',
        } as React.CSSProperties
      }
    >
      <body className="min-h-full bg-background font-sans text-foreground">
        <Providers>
          <SiteHeader />
          <main className="min-h-[calc(100vh-var(--navbar-height))]">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
