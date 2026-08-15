"use client";

import React from "react";
import { Check } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";

export default function BillingPage() {
  const { t, locale } = useI18n();

  return (
    <div className="space-y-6 font-sans">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{t("billing.title")}</h1>
        <p className="text-sm text-muted-foreground">{t("billing.subtitle")}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 md:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">{t("billing.current_plan")}</span>
              <h3 className="text-xl font-bold text-foreground mt-0.5">{t("billing.plan_name")}</h3>
            </div>
            <Badge variant="success">{t("billing.active_badge")}</Badge>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-4 border-y text-xs">
            <div>
              <span className="text-muted-foreground">{t("billing.monthly_fee")}</span>
              <p className="font-bold text-foreground mt-0.5 font-mono">$299.00 / {locale === "ar" ? "شهر" : "mo"}</p>
            </div>
            <div>
              <span className="text-muted-foreground">{t("billing.branches_quota")}</span>
              <p className="font-bold text-foreground mt-0.5 font-mono">5 / 10</p>
            </div>
            <div>
              <span className="text-muted-foreground">{t("billing.users_quota")}</span>
              <p className="font-bold text-foreground mt-0.5 font-mono">18 / 25</p>
            </div>
            <div>
              <span className="text-muted-foreground">{t("billing.renewal_date")}</span>
              <p className="font-bold text-foreground mt-0.5 font-mono">2026-09-15</p>
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <Button variant="outline">{t("billing.change_plan")}</Button>
            <Button>{t("billing.manage_addons")}</Button>
          </div>
        </Card>

        <Card className="p-6 space-y-4">
          <h3 className="font-semibold text-sm">{locale === "ar" ? "الميزات والخصائص المشمولة" : "Included Entitlements"}</h3>
          <ul className="space-y-2 text-xs text-muted-foreground">
            <li className="flex items-center gap-2 text-foreground font-medium">
              <Check className="h-4 w-4 text-emerald-500 shrink-0" />
              <span>{locale === "ar" ? "نقاط بيع متزامنة لكافة الفروع" : "Multi-Branch POS & Cash Registers"}</span>
            </li>
            <li className="flex items-center gap-2 text-foreground font-medium">
              <Check className="h-4 w-4 text-emerald-500 shrink-0" />
              <span>{locale === "ar" ? "محرك القيود ودفتر الأستاذ المزدوج" : "Double-Entry General Ledger"}</span>
            </li>
            <li className="flex items-center gap-2 text-foreground font-medium">
              <Check className="h-4 w-4 text-emerald-500 shrink-0" />
              <span>{locale === "ar" ? "المتجر الإلكتروني وتطبيق الجوال" : "E-Commerce Digital Storefront"}</span>
            </li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
