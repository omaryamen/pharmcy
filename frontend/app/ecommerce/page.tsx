"use client";

import React, { useState } from "react";
import { Store, Plus, Search, Truck, Pill, CheckCircle2, Clock, User, Eye } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";
import { formatCurrency } from "@/lib/utils";

export default function EcommercePage() {
  const { t, locale } = useI18n();
  const [search, setSearch] = useState("");

  const orders = [
    {
      id: "1",
      orderNo: "ECOM-2026-091",
      customer: locale === "ar" ? "د. نادية القحطاني (عيادة الجلدية)" : "Dr. Nadia Al-Qahtani (Dermatology)",
      tracking: "TRK-SA-889102",
      amount: 450.0,
      rxStatus: "verified",
      fulfillment: "dispatched",
    },
    {
      id: "2",
      orderNo: "ECOM-2026-092",
      customer: locale === "ar" ? "مجمع الروابي الطبي" : "Al-Rawabi Medical Complex",
      tracking: "TRK-SA-910442",
      amount: 1850.0,
      rxStatus: "verified",
      fulfillment: "delivered",
    },
    {
      id: "3",
      orderNo: "ECOM-2026-093",
      customer: locale === "ar" ? "يوسف الغامدي (طلب منزلي)" : "Yousef Al-Ghamdi (Home Delivery)",
      tracking: "TRK-SA-994112",
      amount: 85.0,
      rxStatus: "pending_verification",
      fulfillment: "processing",
    },
  ];

  return (
    <div className="space-y-6 font-sans">
      {/* Header & Customer Service Role Context */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="default" className="bg-purple-600 hover:bg-purple-700 text-[11px] gap-1 px-2.5 py-0.5">
              <Store className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "خدمة العملاء والطلبات الرقمية (B2B & Delivery)" : "Customer Service & Digital Orders"}</span>
            </Badge>
            <Badge variant="outline" className="text-[10px] text-muted-foreground">
              {locale === "ar" ? "كتالوج الأدوية الرقمي والتوصيل المنزلي" : "Digital Medicine Catalog & Courier Delivery"}
            </Badge>
          </div>
          <h1 className="text-2xl font-bold tracking-tight">{t("ecom.title")}</h1>
          <p className="text-sm text-muted-foreground">{t("ecom.subtitle")}</p>
        </div>

        <div className="flex items-center gap-2">
          <Button size="sm" className="gap-1.5 text-xs bg-purple-600 hover:bg-purple-700">
            <Plus className="h-3.5 w-3.5" />
            <span>{t("ecom.publish_prod")}</span>
          </Button>
        </div>
      </div>

      {/* Customer Service KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">{locale === "ar" ? "طلبات المتجر الرقمي اليوم" : "Today's Digital Orders"}</span>
          <p className="text-2xl font-bold mt-1 font-mono text-foreground">{formatCurrency(2385.0)}</p>
          <p className="text-[11px] text-emerald-600 mt-2 font-semibold">{locale === "ar" ? "3 طلبات جديدة اليوم" : "3 new orders today"}</p>
        </Card>

        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">{locale === "ar" ? "وصفات مرفوعة بانتظار التدقيق" : "Uploaded Rx Verification"}</span>
          <p className="text-2xl font-bold mt-1 font-mono text-amber-600">1</p>
          <div className="flex items-center gap-1.5 mt-2 text-[11px] text-amber-600 font-semibold">
            <Pill className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "بانتظار موافقة الصيدلي الإكلينيكي" : "Awaiting Pharmacist Sign-Off"}</span>
          </div>
        </Card>

        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">{locale === "ar" ? "طرود قيد الشحن والتوصيل" : "Parcels In Transit"}</span>
          <p className="text-2xl font-bold mt-1 font-mono text-primary">12</p>
          <p className="text-[11px] text-muted-foreground mt-2">{locale === "ar" ? "تتبع مباشر مع شركات الشحن" : "Live Courier GPS Tracking"}</p>
        </Card>

        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">{locale === "ar" ? "حسابات العملاء النشطة" : "Active Customer Profiles"}</span>
          <p className="text-2xl font-bold mt-1 font-mono text-emerald-600">450</p>
          <p className="text-[11px] text-muted-foreground mt-2">{locale === "ar" ? "سجلات طبية ومطالبات تأمين" : "Verified Patient Profiles"}</p>
        </Card>
      </div>

      {/* Orders Feed */}
      <Card>
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-3">
          <div>
            <CardTitle className="text-base font-bold">{locale === "ar" ? "طلبات التوصيل والعملاء المؤسسيين" : "Customer Orders & Deliveries"}</CardTitle>
            <CardDescription>{locale === "ar" ? "إدارة الشحنات، تتبع بوليصات الشحن، ومطابقة الوصفات الطبية المرفوعة." : "Order fulfillment, courier waybills, and prescription approval status."}</CardDescription>
          </div>
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-3 pointer-events-none" />
            <Input
              placeholder={locale === "ar" ? "بحث برقم الطلب، العميل..." : "Search Order #, customer..."}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 text-xs rtl:pl-3 rtl:pr-9"
            />
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-xs text-left rtl:text-right">
            <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
              <tr>
                <th className="p-3">{t("ecom.col_order_no")}</th>
                <th className="p-3">{locale === "ar" ? "العميل / المنشأة" : "Customer / Clinic"}</th>
                <th className="p-3">{t("ecom.col_tracking")}</th>
                <th className="p-3 text-right rtl:text-left">{locale === "ar" ? "القيمة" : "Amount"}</th>
                <th className="p-3">{t("ecom.col_rx_status")}</th>
                <th className="p-3">{t("ecom.col_fulfillment")}</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {orders.map((ord) => (
                <tr key={ord.id} className="hover:bg-muted/50">
                  <td className="p-3 font-semibold text-primary font-mono">{ord.orderNo}</td>
                  <td className="p-3 font-medium">{ord.customer}</td>
                  <td className="p-3 font-mono text-muted-foreground">{ord.tracking}</td>
                  <td className="p-3 text-right rtl:text-left font-bold font-mono text-emerald-600">{formatCurrency(ord.amount)}</td>
                  <td className="p-3">
                    <Badge variant={ord.rxStatus === "verified" ? "success" : "warning"}>
                      {ord.rxStatus === "verified" ? (locale === "ar" ? "وصفة معتمدة" : "Rx Approved") : (locale === "ar" ? "بانتظار الصيدلي" : "Pending Rx")}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <Badge variant={ord.fulfillment === "delivered" ? "success" : ord.fulfillment === "dispatched" ? "default" : "outline"}>
                      {ord.fulfillment === "delivered" ? t("status.delivered") : ord.fulfillment === "dispatched" ? t("status.dispatched") : (locale === "ar" ? "قيد التجهيز" : "Processing")}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
