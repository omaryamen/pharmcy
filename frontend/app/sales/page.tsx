"use client";

import React from "react";
import { Search, Plus, Filter, Download } from "lucide-react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";

export default function SalesPage() {
  const { t, locale } = useI18n();

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t("sales.title")}</h1>
          <p className="text-sm text-muted-foreground">{t("sales.subtitle")}</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="gap-2">
            <Download className="h-4 w-4" /> {t("sales.export_csv")}
          </Button>
          <Button className="gap-2">
            <Plus className="h-4 w-4" /> {t("sales.new_credit_inv")}
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between border-b">
          <div className="relative w-72">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-3" />
            <Input placeholder={t("header.search_placeholder")} className="pl-9 text-xs rtl:pl-3 rtl:pr-9" />
          </div>
          <Button variant="outline" size="sm" className="gap-2 text-xs">
            <Filter className="h-3 w-3" /> {locale === "ar" ? "تصفية الحالة" : "Filter Status"}
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-xs text-left rtl:text-right">
            <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
              <tr>
                <th className="p-3">{t("sales.col_number")}</th>
                <th className="p-3">{t("sales.col_customer")}</th>
                <th className="p-3">{t("sales.col_date")}</th>
                <th className="p-3">{t("sales.col_method")}</th>
                <th className="p-3 text-right rtl:text-left">{t("sales.col_net")}</th>
                <th className="p-3">{t("sales.col_status")}</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary font-mono">INV-2026-0091</td>
                <td className="p-3">{locale === "ar" ? "سارة المنصور (نقدي)" : "Sarah Al-Mansoor (Walk-in)"}</td>
                <td className="p-3 font-mono">2026-08-15 04:12</td>
                <td className="p-3">{locale === "ar" ? "نقداً (كاش)" : "Cash"}</td>
                <td className="p-3 text-right rtl:text-left font-bold font-mono">$45.00</td>
                <td className="p-3"><Badge variant="success">{t("status.completed")}</Badge></td>
              </tr>
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary font-mono">INV-2026-0090</td>
                <td className="p-3">{locale === "ar" ? "مجمع عيادات الأمل (آجل)" : "Al-Amal Clinic (B2B Credit)"}</td>
                <td className="p-3 font-mono">2026-08-15 03:30</td>
                <td className="p-3">{locale === "ar" ? "حساب آجل (ذمم مدينة)" : "Account Credit"}</td>
                <td className="p-3 text-right rtl:text-left font-bold font-mono">$1,200.00</td>
                <td className="p-3"><Badge variant="default">{t("status.posted")}</Badge></td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
