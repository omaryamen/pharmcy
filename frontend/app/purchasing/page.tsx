"use client";

import React from "react";
import { Plus, Search } from "lucide-react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";

export default function PurchasingPage() {
  const { t, locale } = useI18n();

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t("purchasing.title")}</h1>
          <p className="text-sm text-muted-foreground">{t("purchasing.subtitle")}</p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" /> {t("purchasing.new_po")}
        </Button>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between border-b">
          <div className="relative w-72">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-3" />
            <Input placeholder={t("header.search_placeholder")} className="pl-9 text-xs rtl:pl-3 rtl:pr-9" />
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-xs text-left rtl:text-right">
            <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
              <tr>
                <th className="p-3">{t("purchasing.col_po")}</th>
                <th className="p-3">{t("purchasing.col_supplier")}</th>
                <th className="p-3">{t("purchasing.col_order_date")}</th>
                <th className="p-3 text-right rtl:text-left">{t("purchasing.col_total")}</th>
                <th className="p-3">{t("purchasing.col_status")}</th>
                <th className="p-3">{t("purchasing.col_matching")}</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary font-mono">PO-2026-0041</td>
                <td className="p-3">{locale === "ar" ? "شركة نوفارتس للأدوية" : "Novartis Pharma Distribution"}</td>
                <td className="p-3 font-mono">2026-08-14</td>
                <td className="p-3 text-right rtl:text-left font-bold font-mono">$14,500.00</td>
                <td className="p-3"><Badge variant="success">{t("status.received")}</Badge></td>
                <td className="p-3"><Badge variant="default">{t("status.matched")}</Badge></td>
              </tr>
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary font-mono">PO-2026-0042</td>
                <td className="p-3">{locale === "ar" ? "فايزر العالمية للتوزيع" : "Pfizer Global Supply"}</td>
                <td className="p-3 font-mono">2026-08-15</td>
                <td className="p-3 text-right rtl:text-left font-bold font-mono">$8,200.00</td>
                <td className="p-3"><Badge variant="warning">{locale === "ar" ? "بانتظار الاستلام" : "Pending GRN"}</Badge></td>
                <td className="p-3"><Badge variant="outline">{locale === "ar" ? "معلق" : "Pending"}</Badge></td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
