"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Building2,
  Users,
  GitBranch,
  FileCheck2,
  TrendingUp,
  Receipt,
  ShoppingCart,
  Pill,
  Package,
  DollarSign,
  ShieldCheck,
  ArrowRight,
  Calendar,
  AlertTriangle,
  Clock,
  CheckCircle2,
  ArrowUpRight,
  Layers,
  Search,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";
import { formatCurrency } from "@/lib/utils";

export default function PharmacyAdminAppPage() {
  const { t, locale } = useI18n();
  const [dateFilter, setDateFilter] = useState<"today" | "week" | "month">("today");

  const businessKpis = {
    todaySales: 12450.8,
    monthlySales: 342000.0,
    grossProfitRate: "28.4%",
    inventoryValuation: 142850.0,
    lowStockCount: 8,
    nearExpiryCount: 12,
    pendingRxCount: 3,
    receivables: 18400.0,
    payables: 32150.0,
  };

  const branchPerformances = [
    { id: "1", name: locale === "ar" ? "الفرع الرئيسي (العليا)" : "Main Branch (Al-Olaya)", sales: 6850.5, rxCount: 42, stockValue: 85000, status: "active" },
    { id: "2", name: locale === "ar" ? "فرع 2 (الملز)" : "Branch #2 (Al-Malaz)", sales: 4350.3, rxCount: 28, stockValue: 42000, status: "active" },
    { id: "3", name: locale === "ar" ? "المستودع المركزي اللوجستي" : "Central Logistics Warehouse", sales: 1250.0, rxCount: 0, stockValue: 15850, status: "active" },
  ];

  return (
    <div className="space-y-6 font-sans">
      {/* Executive Header & Organization Identity */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="default" className="bg-emerald-600 hover:bg-emerald-700 text-[11px] gap-1 px-2.5 py-0.5">
              <Building2 className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "بوابة إدارة الصيدلية والمنشأة (Management Portal)" : "Pharmacy Management Portal"}</span>
            </Badge>
            <Badge variant="outline" className="text-[10px] text-muted-foreground">
              {locale === "ar" ? "سلسلة صيدليات الأمل الحديثة المحدودة" : "Al-Amal Modern Pharmacy Chain LLC"}
            </Badge>
          </div>
          <h1 className="text-2xl font-bold tracking-tight">
            {locale === "ar" ? "لوحة الإدارة التنفيذية والتشغيلية" : "Executive Operational Management Center"}
          </h1>
          <p className="text-sm text-muted-foreground">
            {locale === "ar"
              ? "مؤشرات الأداء المالي الموحدة، أرصدة المخزون، مبيعات الفروع، وإدارة الكادر الصيدلاني."
              : "Consolidated enterprise sales, inventory valuation, multi-branch performance, and RBAC governance."}
          </p>
        </div>

        {/* Date Filter & Quick Actions */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center bg-muted/60 p-1 rounded-lg border text-xs">
            <Button
              variant={dateFilter === "today" ? "default" : "ghost"}
              size="sm"
              onClick={() => setDateFilter("today")}
              className="h-7 text-xs px-2.5"
            >
              {locale === "ar" ? "اليوم" : "Today"}
            </Button>
            <Button
              variant={dateFilter === "week" ? "default" : "ghost"}
              size="sm"
              onClick={() => setDateFilter("week")}
              className="h-7 text-xs px-2.5"
            >
              {locale === "ar" ? "هذا الأسبوع" : "This Week"}
            </Button>
            <Button
              variant={dateFilter === "month" ? "default" : "ghost"}
              size="sm"
              onClick={() => setDateFilter("month")}
              className="h-7 text-xs px-2.5"
            >
              {locale === "ar" ? "هذا الشهر" : "This Month"}
            </Button>
          </div>

          <Link href="/settings">
            <Button size="sm" className="gap-1.5 text-xs">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "الإعدادات والصلاحيات" : "Settings & RBAC"}</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Financial & Operational Executive KPI Matrix */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{locale === "ar" ? "مبيعات اليوم الإجمالية" : "Today's Total Sales"}</span>
            <TrendingUp className="h-4 w-4 text-emerald-600" />
          </div>
          <p className="text-2xl font-bold mt-1 font-mono text-foreground">{formatCurrency(businessKpis.todaySales)}</p>
          <div className="flex items-center justify-between text-[11px] mt-2">
            <span className="text-emerald-600 font-semibold">+14.2% {locale === "ar" ? "نمو عن الأمس" : "vs yesterday"}</span>
            <span className="text-muted-foreground">{locale === "ar" ? "هامش الربح:" : "Margin:"} {businessKpis.grossProfitRate}</span>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{locale === "ar" ? "إجمالي تقييم المخزون (FEFO)" : "Inventory Valuation"}</span>
            <Package className="h-4 w-4 text-blue-600" />
          </div>
          <p className="text-2xl font-bold mt-1 font-mono text-foreground">{formatCurrency(businessKpis.inventoryValuation)}</p>
          <div className="flex items-center gap-2 text-[11px] mt-2">
            <Badge variant="warning" className="text-[10px] px-1 py-0">{businessKpis.nearExpiryCount} {locale === "ar" ? "يقترب من الانتهاء" : "Near Expiry"}</Badge>
            <Badge variant="destructive" className="text-[10px] px-1 py-0">{businessKpis.lowStockCount} {locale === "ar" ? "منخفض" : "Low"}</Badge>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{locale === "ar" ? "الذمم المدينة للعملاء (AR)" : "Accounts Receivable"}</span>
            <DollarSign className="h-4 w-4 text-emerald-600" />
          </div>
          <p className="text-2xl font-bold mt-1 font-mono text-foreground">{formatCurrency(businessKpis.receivables)}</p>
          <p className="text-[11px] text-muted-foreground mt-2">{locale === "ar" ? "مطالبات عيادات وشركات تأمين" : "Clinic & Insurance Claims"}</p>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{locale === "ar" ? "الذمم الدائنة للموردين (AP)" : "Accounts Payable"}</span>
            <Receipt className="h-4 w-4 text-amber-600" />
          </div>
          <p className="text-2xl font-bold mt-1 font-mono text-foreground">{formatCurrency(businessKpis.payables)}</p>
          <p className="text-[11px] text-amber-600 font-semibold mt-2">{locale === "ar" ? "فواتير موردين مستحقة الأسبوع" : "Due This Week"}</p>
        </Card>
      </div>

      {/* Operational Modules & Branch Comparison Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Branch Performance Comparison (Left 2 Cols) */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between border-b pb-3">
            <div>
              <CardTitle className="text-base font-bold">{locale === "ar" ? "مقارنة أداء شبكة الفروع والمستودعات" : "Multi-Branch & Warehouse Performance"}</CardTitle>
              <CardDescription>{locale === "ar" ? "حجم المبيعات، صرف الوصفات، وقيمة المخزون لكل فرع على حدة." : "Real-time sales, dispensed prescriptions, and localized stock balances."}</CardDescription>
            </div>
            <Link href="/reports">
              <Button variant="outline" size="sm" className="text-xs gap-1">
                <span>{locale === "ar" ? "التقرير الشامل" : "Full Analytics"}</span>
                <ArrowUpRight className="h-3 w-3 rtl:rotate-180" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-xs text-left rtl:text-right">
              <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
                <tr>
                  <th className="p-3">اسم الفرع / المنشأة</th>
                  <th className="p-3">مبيعات اليوم</th>
                  <th className="p-3">الوصفات المصروفة</th>
                  <th className="p-3">قيمة مخزون الرفوف</th>
                  <th className="p-3">الحالة</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {branchPerformances.map((b) => (
                  <tr key={b.id} className="hover:bg-muted/50">
                    <td className="p-3 font-semibold text-foreground">{b.name}</td>
                    <td className="p-3 font-bold font-mono text-emerald-600">{formatCurrency(b.sales)}</td>
                    <td className="p-3 font-mono">{b.rxCount} {locale === "ar" ? "وصفة" : "Rx"}</td>
                    <td className="p-3 font-mono">{formatCurrency(b.stockValue)}</td>
                    <td className="p-3"><Badge variant="success">نشط ومتصل</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>

        {/* Quick Operational Management Actions (Right Col) */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="border-b pb-3">
              <CardTitle className="text-sm font-bold">{locale === "ar" ? "إجراءات الإدارة السريعة" : "Executive Quick Actions"}</CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-2">
              <Link href="/pos" className="block">
                <Button variant="outline" size="sm" className="w-full justify-start gap-2 text-xs">
                  <ShoppingCart className="h-4 w-4 text-emerald-600" />
                  <span>{locale === "ar" ? "فتح نقطة البيع (POS Terminal)" : "Open POS Terminal"}</span>
                </Button>
              </Link>
              <Link href="/prescriptions" className="block">
                <Button variant="outline" size="sm" className="w-full justify-start gap-2 text-xs">
                  <Pill className="h-4 w-4 text-blue-600" />
                  <span>{locale === "ar" ? "مراجعة الوصفات السريرية (3 معلقة)" : "Review Rx Queue (3 pending)"}</span>
                </Button>
              </Link>
              <Link href="/inventory" className="block">
                <Button variant="outline" size="sm" className="w-full justify-start gap-2 text-xs">
                  <Package className="h-4 w-4 text-purple-600" />
                  <span>{locale === "ar" ? "فحص حركات المخزون والتشغيلات" : "Inspect Stock & Batches"}</span>
                </Button>
              </Link>
              <Link href="/accounting" className="block">
                <Button variant="outline" size="sm" className="w-full justify-start gap-2 text-xs">
                  <TrendingUp className="h-4 w-4 text-amber-600" />
                  <span>{locale === "ar" ? "دفتر الأستاذ والقيود اليومية" : "General Ledger & Journals"}</span>
                </Button>
              </Link>
              <Link href="/settings" className="block">
                <Button variant="outline" size="sm" className="w-full justify-start gap-2 text-xs">
                  <Users className="h-4 w-4 text-primary" />
                  <span>{locale === "ar" ? "طاقم العمل ومصفوفة الصلاحيات" : "Staff & RBAC Permissions"}</span>
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Operational Alerts Card */}
          <Card className="p-4 bg-amber-500/10 border-amber-500/20 text-amber-900 dark:text-amber-300">
            <div className="flex items-center gap-2 font-bold text-xs">
              <AlertTriangle className="h-4 w-4 text-amber-600" />
              <span>{locale === "ar" ? "تنبيهات تشغيلية بحاجة للمتابعة" : "Operational Action Items"}</span>
            </div>
            <ul className="text-[11px] space-y-1.5 mt-2 list-disc list-inside">
              <li>{locale === "ar" ? "12 صنف دواء يقترب من الانتهاء خلال 30 يوم (FEFO)" : "12 batches approaching expiry in 30 days"}</li>
              <li>{locale === "ar" ? "فاتورة مورد واحدة بانتظار المطابقة الثلاثية 3-Way Match" : "1 supplier invoice awaiting 3-way match"}</li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
}
