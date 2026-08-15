"use client";

import React from "react";
import Link from "next/link";
import {
  TrendingUp,
  Package,
  AlertTriangle,
  Pill,
  ShoppingCart,
  ArrowUpRight,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";

export default function DashboardPage() {
  const { t, locale } = useI18n();

  return (
    <div className="space-y-6">
      {/* Top Header & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t("dashboard.title")}</h1>
          <p className="text-sm text-muted-foreground">{t("dashboard.subtitle")}</p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/pos">
            <Button className="gap-2">
              <ShoppingCart className="h-4 w-4" /> {t("dashboard.open_pos")}
            </Button>
          </Link>
          <Link href="/prescriptions">
            <Button variant="outline" className="gap-2">
              <Pill className="h-4 w-4" /> {t("dashboard.review_rx")} (4)
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">{t("dashboard.sales_today")}</CardTitle>
            <TrendingUp className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono">$12,450.80</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <span className="text-emerald-500 font-medium">{t("dashboard.sales_trend")}</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">{t("dashboard.pending_rx")}</CardTitle>
            <Pill className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{locale === "ar" ? "7 وصفات" : "7 Awaiting"}</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <Badge variant="warning" className="text-[10px] px-1 py-0">
                {t("dashboard.controlled_rx_alert")}
              </Badge>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">{t("dashboard.stock_on_hand")}</CardTitle>
            <Package className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono">18,940</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              {t("dashboard.stock_valuation")} <span className="font-semibold text-foreground font-mono">$142,850.00</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">{t("dashboard.alerts_title")}</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{locale === "ar" ? "12 صنف" : "12 Items"}</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <span className="text-destructive font-medium">{t("dashboard.near_expiry_alert")}</span>
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Grid: Live Orders / Clinical Queues */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Live Sales & Orders */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>{t("dashboard.recent_sales")}</CardTitle>
              <CardDescription>{locale === "ar" ? "متابعة مباشرة لعمليات البيع عبر نقاط البيع والمتجر الإلكتروني." : "Live real-time feed of multi-channel transactions."}</CardDescription>
            </div>
            <Link href="/sales" className="text-xs text-primary hover:underline flex items-center gap-1">
              {t("dashboard.view_all")} <ArrowUpRight className="h-3 w-3 rtl:rotate-180" />
            </Link>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left rtl:text-right">
                <thead className="border-b bg-muted/40 font-medium text-muted-foreground">
                  <tr>
                    <th className="p-3">{t("dashboard.col_invoice")}</th>
                    <th className="p-3">{t("dashboard.col_customer")}</th>
                    <th className="p-3">{t("dashboard.col_branch")}</th>
                    <th className="p-3">{t("dashboard.col_amount")}</th>
                    <th className="p-3">{t("dashboard.col_status")}</th>
                    <th className="p-3">{t("dashboard.col_time")}</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  <tr className="hover:bg-muted/50">
                    <td className="p-3 font-semibold text-primary font-mono">INV-2026-8891</td>
                    <td className="p-3">{locale === "ar" ? "سارة المنصور (نقدي)" : "Sarah Al-Mansoor (Walk-in)"}</td>
                    <td className="p-3">{locale === "ar" ? "الفرع الرئيسي" : "Main Branch"}</td>
                    <td className="p-3 font-bold font-mono">$45.00</td>
                    <td className="p-3"><Badge variant="success">{t("status.completed")}</Badge></td>
                    <td className="p-3 text-muted-foreground">{locale === "ar" ? "منذ دقيقتين" : "2 mins ago"}</td>
                  </tr>
                  <tr className="hover:bg-muted/50">
                    <td className="p-3 font-semibold text-primary font-mono">ORD-2026-4412</td>
                    <td className="p-3">{locale === "ar" ? "مجمع عيادات الأمل (B2B)" : "Al-Amal Clinic (B2B)"}</td>
                    <td className="p-3">{locale === "ar" ? "المستودع المركزي" : "Central Warehouse"}</td>
                    <td className="p-3 font-bold font-mono">$1,250.00</td>
                    <td className="p-3"><Badge variant="default">{t("status.dispatched")}</Badge></td>
                    <td className="p-3 text-muted-foreground">{locale === "ar" ? "منذ 15 دقيقة" : "15 mins ago"}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Right Col: Quick Clinical & Operational Actions */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("dashboard.rx_queue_title")}</CardTitle>
              <CardDescription>{t("dashboard.rx_queue_subtitle")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-3 rounded-lg border bg-muted/30 flex items-center justify-between">
                <div className="flex flex-col">
                  <span className="text-xs font-semibold">{locale === "ar" ? "وصفة #RX-091 - أوجمنتين 1 جم" : "Rx #RX-091 - Augmentin 1g"}</span>
                  <span className="text-[10px] text-muted-foreground">{locale === "ar" ? "المريض: ياسمين نور | د. خالد نادر" : "Patient: Yasmin Noor | Dr. K. Nader"}</span>
                </div>
                <Badge variant="warning">{t("status.review")}</Badge>
              </div>

              <Link href="/prescriptions" className="block w-full">
                <Button variant="outline" className="w-full text-xs">{t("dashboard.open_rx_queue")}</Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t("dashboard.system_status_title")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-xs">
              <div className="flex items-center justify-between py-1 border-b">
                <span className="text-muted-foreground">{t("dashboard.system_engine")}</span>
                <span className="font-semibold text-emerald-600">v1.37.0 Enterprise</span>
              </div>
              <div className="flex items-center justify-between py-1 border-b">
                <span className="text-muted-foreground">{t("dashboard.stock_engine")}</span>
                <span className="font-semibold text-emerald-600">{t("status.active")}</span>
              </div>
              <div className="flex items-center justify-between py-1">
                <span className="text-muted-foreground">{t("dashboard.gl_integration")}</span>
                <span className="font-semibold text-emerald-600">{t("status.posted")}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
