"use client";

import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useI18n } from "@/lib/i18n";

export default function SettingsPage() {
  const { t, locale } = useI18n();
  const [orgName, setOrgName] = useState(locale === "ar" ? "سلسلة صيدليات الأمل الحديثة" : "Al-Amal Modern Pharmacy Chain");
  const [crNumber, setCrNumber] = useState("1010889922");
  const [taxNumber, setTaxNumber] = useState("300998877600003");
  const [currency, setCurrency] = useState("USD ($)");

  return (
    <div className="space-y-6 font-sans">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{t("settings.title")}</h1>
        <p className="text-sm text-muted-foreground">{t("settings.subtitle")}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>{t("settings.company_info")}</CardTitle>
            <CardDescription>{locale === "ar" ? "البيانات الرسمية المطبوعة على فواتير المبيعات وسندات الصرف." : "Official organization identity rendered on tax invoices and receipts."}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            <div className="space-y-1">
              <label className="font-medium text-foreground">{t("settings.org_name")}</label>
              <Input value={orgName} onChange={(e) => setOrgName(e.target.value)} />
            </div>
            <div className="space-y-1">
              <label className="font-medium text-foreground">{t("settings.cr_number")}</label>
              <Input value={crNumber} onChange={(e) => setCrNumber(e.target.value)} className="font-mono" />
            </div>
            <div className="space-y-1">
              <label className="font-medium text-foreground">{t("settings.tax_number")}</label>
              <Input value={taxNumber} onChange={(e) => setTaxNumber(e.target.value)} className="font-mono" />
            </div>
            <div className="space-y-1">
              <label className="font-medium text-foreground">{t("settings.currency")}</label>
              <Input value={currency} onChange={(e) => setCurrency(e.target.value)} />
            </div>
          </CardContent>
          <CardFooter className="border-t pt-4 flex justify-end">
            <Button className="text-xs">{t("settings.save_btn")}</Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("settings.security_policies")}</CardTitle>
            <CardDescription>{locale === "ar" ? "قواعد تسجيل الدخول وسياسات انتهاء الجلسات." : "Session timeout rules and enterprise tenant policies."}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="p-3 rounded-lg border bg-muted/20 flex items-center justify-between">
              <div>
                <p className="font-semibold">{locale === "ar" ? "التحقق الثنائي الإلزامي (MFA)" : "Enforce Multi-Factor Authentication"}</p>
                <p className="text-[11px] text-muted-foreground">{locale === "ar" ? "إلزام الصيادلة والمحاسبين برمز OTP" : "Mandatory for pharmacists and accountants"}</p>
              </div>
              <span className="text-emerald-600 font-bold">{locale === "ar" ? "مفعل" : "Enabled"}</span>
            </div>

            <div className="p-3 rounded-lg border bg-muted/20 flex items-center justify-between">
              <div>
                <p className="font-semibold">{locale === "ar" ? "مهلة انتهاء الجلسة التلقائي" : "Automatic Session Inactivity Timeout"}</p>
                <p className="text-[11px] text-muted-foreground">{locale === "ar" ? "قفل شاشة نقطة البيع بعد 15 دقيقة خمول" : "Lock POS screen after 15 mins of idle time"}</p>
              </div>
              <span className="font-mono font-bold">15 {locale === "ar" ? "دقيقة" : "mins"}</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
