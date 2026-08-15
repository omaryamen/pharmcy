"use client";

import React from "react";
import { Plus } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";

export default function AccountingPage() {
  const { t, locale } = useI18n();

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t("acc.title")}</h1>
          <p className="text-sm text-muted-foreground">{t("acc.subtitle")}</p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" /> {t("acc.new_journal")}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">{t("acc.cash_accounts")}</span>
          <p className="text-xl font-bold mt-1 text-foreground font-mono">$128,450.00</p>
        </Card>
        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">{t("acc.ar_accounts")}</span>
          <p className="text-xl font-bold mt-1 text-foreground font-mono">$34,200.00</p>
        </Card>
        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">{t("acc.ap_accounts")}</span>
          <p className="text-xl font-bold mt-1 text-destructive font-mono">$18,900.00</p>
        </Card>
      </div>

      <Card>
        <CardHeader className="border-b">
          <CardTitle>{t("acc.journal_logs")}</CardTitle>
          <CardDescription>{locale === "ar" ? "القيود المحاسبية الآلية الناتجة عن حركات البيع، المشتريات، وفواتير الاشتراكات." : "Automated double-entry journals posted from POS, Purchasing, and SaaS billing."}</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-xs text-left rtl:text-right">
            <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
              <tr>
                <th className="p-3">{t("acc.col_journal_no")}</th>
                <th className="p-3">{t("acc.col_desc")}</th>
                <th className="p-3">{t("acc.col_debit")}</th>
                <th className="p-3">{t("acc.col_credit")}</th>
                <th className="p-3 text-right rtl:text-left">{t("acc.col_amount")}</th>
                <th className="p-3">{t("acc.col_status")}</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary font-mono">JRN-2026-0089</td>
                <td className="p-3">{locale === "ar" ? "إقفال مبيعات نقطة البيع اليومية (INV-8891)" : "POS Cash Sales Daily Close (INV-8891)"}</td>
                <td className="p-3 font-mono">1010 - {locale === "ar" ? "نقدية الصندوق" : "Cash on Hand"}</td>
                <td className="p-3 font-mono">4000 - {locale === "ar" ? "إيراد مبيعات الأدوية" : "Sales Revenue"}</td>
                <td className="p-3 text-right rtl:text-left font-bold font-mono">$12,450.80</td>
                <td className="p-3"><Badge variant="success">{t("status.posted")}</Badge></td>
              </tr>
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary font-mono">JRN-2026-0088</td>
                <td className="p-3">{locale === "ar" ? "استلام بضاعة مشتريات مخزنية (GRN-041)" : "Inventory Purchase Goods Receipt (GRN-041)"}</td>
                <td className="p-3 font-mono">1300 - {locale === "ar" ? "أصول المخزون السلعي" : "Inventory Asset"}</td>
                <td className="p-3 font-mono">2000 - {locale === "ar" ? "الذمم الدائنة (الموردين)" : "Accounts Payable"}</td>
                <td className="p-3 text-right rtl:text-left font-bold font-mono">$14,500.00</td>
                <td className="p-3"><Badge variant="success">{t("status.posted")}</Badge></td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
