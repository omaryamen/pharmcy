"use client";

import React from "react";
import { Plus, ExternalLink } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";

export default function EcommercePage() {
  const { t, locale } = useI18n();

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t("ecom.title")}</h1>
          <p className="text-sm text-muted-foreground">{t("ecom.subtitle")}</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="gap-2">
            <ExternalLink className="h-4 w-4" /> {t("ecom.view_store")}
          </Button>
          <Button className="gap-2">
            <Plus className="h-4 w-4" /> {t("ecom.publish_prod")}
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="border-b">
          <CardTitle>{t("ecom.title")}</CardTitle>
          <CardDescription>{locale === "ar" ? "متابعة مباشرة لطلبات الأدوية والتوصيل السريع." : "Live B2C retail & B2B wholesale digital orders."}</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-xs text-left rtl:text-right">
            <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
              <tr>
                <th className="p-3">{t("ecom.col_order_no")}</th>
                <th className="p-3">{t("dashboard.col_customer")}</th>
                <th className="p-3">{t("ecom.col_tracking")}</th>
                <th className="p-3">{t("ecom.col_rx_status")}</th>
                <th className="p-3 text-right rtl:text-left">{t("dashboard.col_amount")}</th>
                <th className="p-3">{t("ecom.col_fulfillment")}</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary font-mono">ORD-2026-4412</td>
                <td className="p-3">{locale === "ar" ? "مجمع عيادات طارق (B2B)" : "Dr. Tarek Clinic (B2B)"}</td>
                <td className="p-3 font-mono">TRK-8899A</td>
                <td className="p-3"><Badge variant="outline">{locale === "ar" ? "لا تتطلب وصفة" : "N/A (OTC)"}</Badge></td>
                <td className="p-3 text-right rtl:text-left font-bold font-mono">$1,250.00</td>
                <td className="p-3"><Badge variant="default">{t("status.dispatched")}</Badge></td>
              </tr>
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary font-mono">ORD-2026-4410</td>
                <td className="p-3">{locale === "ar" ? "منى العمري (تطبيق الجوال)" : "Jane Retail (Mobile App)"}</td>
                <td className="p-3 font-mono">TRK-2211B</td>
                <td className="p-3"><Badge variant="success">{t("status.approved")}</Badge></td>
                <td className="p-3 text-right rtl:text-left font-bold font-mono">$25.00</td>
                <td className="p-3"><Badge variant="success">{t("status.delivered")}</Badge></td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
