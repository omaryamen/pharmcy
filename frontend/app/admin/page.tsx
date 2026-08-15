"use client";

import React from "react";
import { Activity, Server, ToggleRight } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { useI18n } from "@/lib/i18n";

export default function AdminPage() {
  const { t, locale } = useI18n();

  return (
    <div className="space-y-6 font-sans">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{t("admin.title")}</h1>
        <p className="text-sm text-muted-foreground">{t("admin.subtitle")}</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4 flex items-center gap-4">
          <div className="p-3 rounded-full bg-emerald-500/10 text-emerald-600">
            <Activity className="h-6 w-6" />
          </div>
          <div>
            <span className="text-xs text-muted-foreground font-medium">{t("admin.health_label")}</span>
            <p className="text-lg font-bold text-emerald-600">100% {locale === "ar" ? "يعمل بكفاءة" : "Operational"}</p>
          </div>
        </Card>

        <Card className="p-4 flex items-center gap-4">
          <div className="p-3 rounded-full bg-blue-500/10 text-blue-600">
            <Server className="h-6 w-6" />
          </div>
          <div>
            <span className="text-xs text-muted-foreground font-medium">{t("admin.tenants_count")}</span>
            <p className="text-lg font-bold text-foreground">42 {locale === "ar" ? "صيدلية" : "Organizations"}</p>
          </div>
        </Card>

        <Card className="p-4 flex items-center gap-4">
          <div className="p-3 rounded-full bg-purple-500/10 text-purple-600">
            <ToggleRight className="h-6 w-6" />
          </div>
          <div>
            <span className="text-xs text-muted-foreground font-medium">{t("admin.flags_count")}</span>
            <p className="text-lg font-bold text-foreground">8 {locale === "ar" ? "ميزات نشطة" : "Active Rollouts"}</p>
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader className="border-b">
          <CardTitle>{t("admin.audit_title")}</CardTitle>
          <CardDescription>{locale === "ar" ? "توثيق إجراءات مسؤولي المنصة مع ضمان عدم التعديل." : "Immutable tracking of privileged platform engineering actions."}</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-xs text-left rtl:text-right">
            <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
              <tr>
                <th className="p-3">{locale === "ar" ? "الإجراء" : "Action"}</th>
                <th className="p-3">{locale === "ar" ? "المسؤول" : "Operator"}</th>
                <th className="p-3">{locale === "ar" ? "المستأجر / الصيدلية" : "Target Tenant"}</th>
                <th className="p-3">{locale === "ar" ? "السبب" : "Reason"}</th>
                <th className="p-3">{t("dashboard.col_time")}</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold">{locale === "ar" ? "انتحال هوية لدعم الفني" : "Tenant Impersonation"}</td>
                <td className="p-3 font-mono">superadmin@pharmacloud.com</td>
                <td className="p-3 font-medium">{locale === "ar" ? "سلسلة صيدليات الأمل" : "Al-Amal Pharmacy Chain"}</td>
                <td className="p-3">{locale === "ar" ? "استكشاف أخطاء مزامنة نقطة البيع #T-992" : "Troubleshooting POS sync issue #T-992"}</td>
                <td className="p-3 text-muted-foreground font-mono">2026-08-15 01:22</td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
