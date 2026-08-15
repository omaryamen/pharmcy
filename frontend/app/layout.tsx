import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "PharmaCloud ERP — Enterprise Pharmacy Platform",
  description: "Next-generation multi-tenant cloud ERP for enterprise pharmacies and chains.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" dir="ltr" className="h-full">
      <body className="h-full antialiased font-sans bg-background text-foreground">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
