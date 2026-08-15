"use client";

import React from "react";
import { Download, BarChart3, PieChart } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";

export default function ReportsPage() {
  const { t, locale } = useI18n();

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t("reports.title")}</h1>
          <p className="text-sm text-muted-foreground">{t("reports.subtitle")}</p>
        </div>
        <Button variant="outline" className="gap-2">
          <Download className="h-4 w-4" /> {t("reports.download_pdf")}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-sm">{t("reports.sales_chart_title")}</h3>
            <BarChart3 className="h-4 w-4 text-primary" />
          </div>
          <div className="h-48 rounded-lg bg-muted/30 border flex items-center justify-center text-xs text-muted-foreground text-center p-4">
            {locale === "ar"
              ? "[رسم بياني تفاعلي لتحليلات المبيعات — مبيعات الكاش vs المتجر الإلكتروني vs التوريد B2B]"
              : "[Interactive Sales BI Bar Chart — POS vs Online Store vs B2B Wholesale]"}
          </div>
        </Card>

        <Card className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-sm">{t("reports.category_chart_title")}</h3>
            <PieChart className="h-4 w-4 text-primary" />
          </div>
          <div className="h-48 rounded-lg bg-muted/30 border flex items-center justify-center text-xs text-muted-foreground text-center p-4">
            {locale === "ar"
              ? "[توزيع مبيعات الأصناف — المضادات الحيوية (35%)، المسكنات (28%)، أدوية الأمراض المزمنة (22%)، منتجات العناية (15%)]"
              : "[Category Revenue Breakdown — Antibiotics (35%), Analgesics (28%), Chronic (22%), OTC (15%)]"}
          </div>
        </Card>
      </div>
    </div>
  );
}
