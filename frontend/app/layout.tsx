import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";
import { I18nProvider } from "@/lib/i18n";

export const metadata: Metadata = {
  title: "فارما كلاود — نظام إدارة الصيدليات السحابي المتكامل",
  description: "منظومة سحابية متطورة لإدارة الصيدليات وسلاسل الدواء المتعددة الفروع والمستودعات.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl" className="h-full">
      <body className="h-full antialiased font-sans bg-background text-foreground">
        <I18nProvider>
          <AppShell>{children}</AppShell>
        </I18nProvider>
      </body>
    </html>
  );
}
