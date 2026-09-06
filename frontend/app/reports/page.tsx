"use client";

import React, { useState } from "react";
import {
  Download,
  BarChart3,
  PieChart,
  TrendingUp,
  Calendar,
  FileText,
  Filter,
  Printer,
  X,
  CheckCircle2,
  DollarSign,
  Package,
  Activity,
  ArrowUpRight,
  ShieldCheck,
  Building2,
  Percent,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";
import { formatCurrency } from "@/lib/utils";

type ReportPeriod = "month" | "quarter" | "year";

export default function ReportsPage() {
  const { t, locale } = useI18n();
  const [period, setPeriod] = useState<ReportPeriod>("month");
  const [isPdfModalOpen, setIsPdfModalOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Dynamic Metrics based on selected Period
  const periodData = {
    month: {
      labelAr: "تقرير شهر أغسطس 2026",
      grossRevenue: 342000.0,
      cogs: 244872.0,
      grossProfit: 97128.0,
      operatingExpenses: 28500.0,
      netProfit: 68628.0,
      marginPercent: 28.4,
      totalInvoices: 4120,
      avgBasket: 83.0,
      channels: [
        { name: "نقاط البيع المباشرة (POS)", amount: 245000.0, percent: 71, color: "bg-primary" },
        { name: "المبيعات المؤسسية (B2B Clinics)", amount: 68000.0, percent: 20, color: "bg-emerald-600" },
        { name: "المتجر الإلكتروني والتوصيل", amount: 29000.0, percent: 9, color: "bg-purple-600" },
      ],
      categories: [
        { name: "المضادات الحيوية (Antibiotics)", percent: 35, revenue: 119700.0, color: "bg-blue-600" },
        { name: "المسكنات وخافضات الحرارة", percent: 28, revenue: 95760.0, color: "bg-emerald-600" },
        { name: "أدوية الأمراض المزمنة (Chronic)", percent: 22, revenue: 75240.0, color: "bg-amber-600" },
        { name: "المكملات ومنتجات العناية", percent: 15, revenue: 51300.0, color: "bg-purple-600" },
      ],
      topMeds: [
        { rank: 1, name: "بنادول اكسترا 500 ملجم", category: "مسكنات", units: 1420, revenue: 6390.0, margin: "32%" },
        { rank: 2, name: "أوجمنتين 1 جم أقراص", category: "مضاد حيوي", units: 850, revenue: 15512.5, margin: "24%" },
        { rank: 3, name: "نيكسيوم 40 ملجم", category: "جهاز هضمي", units: 620, revenue: 17360.0, margin: "28%" },
        { rank: 4, name: "بروفين 400 ملجم", category: "مسكنات", units: 580, revenue: 3915.0, margin: "35%" },
      ],
    },
    quarter: {
      labelAr: "تقرير الربع الثالث (Q3) 2026",
      grossRevenue: 985000.0,
      cogs: 704275.0,
      grossProfit: 280725.0,
      operatingExpenses: 82000.0,
      netProfit: 198725.0,
      marginPercent: 28.5,
      totalInvoices: 11950,
      avgBasket: 82.4,
      channels: [
        { name: "نقاط البيع المباشرة (POS)", amount: 699350.0, percent: 71, color: "bg-primary" },
        { name: "المبيعات المؤسسية (B2B Clinics)", amount: 197000.0, percent: 20, color: "bg-emerald-600" },
        { name: "المتجر الإلكتروني والتوصيل", amount: 88650.0, percent: 9, color: "bg-purple-600" },
      ],
      categories: [
        { name: "المضادات الحيوية (Antibiotics)", percent: 34, revenue: 334900.0, color: "bg-blue-600" },
        { name: "المسكنات وخافضات الحرارة", percent: 29, revenue: 285650.0, color: "bg-emerald-600" },
        { name: "أدوية الأمراض المزمنة (Chronic)", percent: 23, revenue: 226550.0, color: "bg-amber-600" },
        { name: "المكملات ومنتجات العناية", percent: 14, revenue: 137900.0, color: "bg-purple-600" },
      ],
      topMeds: [
        { rank: 1, name: "بنادول اكسترا 500 ملجم", category: "مسكنات", units: 4120, revenue: 18540.0, margin: "32%" },
        { rank: 2, name: "نيكسيوم 40 ملجم", category: "جهاز هضمي", units: 1950, revenue: 54600.0, margin: "28%" },
        { rank: 3, name: "أوجمنتين 1 جم أقراص", category: "مضاد حيوي", units: 2480, revenue: 45260.0, margin: "24%" },
        { rank: 4, name: "بروفين 400 ملجم", category: "مسكنات", units: 1690, revenue: 11407.5, margin: "35%" },
      ],
    },
    year: {
      labelAr: "التقرير المالي السنوي 2026",
      grossRevenue: 3850000.0,
      cogs: 2752750.0,
      grossProfit: 1097250.0,
      operatingExpenses: 320000.0,
      netProfit: 777250.0,
      marginPercent: 28.5,
      totalInvoices: 46800,
      avgBasket: 82.2,
      channels: [
        { name: "نقاط البيع المباشرة (POS)", amount: 2733500.0, percent: 71, color: "bg-primary" },
        { name: "المبيعات المؤسسية (B2B Clinics)", amount: 770000.0, percent: 20, color: "bg-emerald-600" },
        { name: "المتجر الإلكتروني والتوصيل", amount: 346500.0, percent: 9, color: "bg-purple-600" },
      ],
      categories: [
        { name: "المضادات الحيوية (Antibiotics)", percent: 35, revenue: 1347500.0, color: "bg-blue-600" },
        { name: "المسكنات وخافضات الحرارة", percent: 28, revenue: 1078000.0, color: "bg-emerald-600" },
        { name: "أدوية الأمراض المزمنة (Chronic)", percent: 22, revenue: 847000.0, color: "bg-amber-600" },
        { name: "المكملات ومنتجات العناية", percent: 15, revenue: 577500.0, color: "bg-purple-600" },
      ],
      topMeds: [
        { rank: 1, name: "بنادول اكسترا 500 ملجم", category: "مسكنات", units: 16500, revenue: 74250.0, margin: "32%" },
        { rank: 2, name: "نيكسيوم 40 ملجم", category: "جهاز هضمي", units: 7800, revenue: 218400.0, margin: "28%" },
        { rank: 3, name: "أوجمنتين 1 جم أقراص", category: "مضاد حيوي", units: 9800, revenue: 178850.0, margin: "24%" },
        { rank: 4, name: "بروفين 400 ملجم", category: "مسكنات", units: 6900, revenue: 46575.0, margin: "35%" },
      ],
    },
  };

  const current = periodData[period];

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 2500);
  };

  const handleExportCSV = () => {
    const headers = ["البند المالي", "القيمة ($)", "النسبة / التفاصيل"];
    const rows = [
      ["إجمالي الإيرادات (Gross Revenue)", current.grossRevenue.toFixed(2), "100%"],
      ["تكلفة البضاعة المباعة (COGS)", current.cogs.toFixed(2), `${(100 - current.marginPercent).toFixed(1)}%`],
      ["مجمل الربح (Gross Profit)", current.grossProfit.toFixed(2), `${current.marginPercent}%`],
      ["المصاريف التشغيلية (OpEx)", current.operatingExpenses.toFixed(2), ""],
      ["صافي الأرباح التشغيلية (Net Profit)", current.netProfit.toFixed(2), ""],
      ["عدد الفواتير الصادرة", current.totalInvoices.toString(), ""],
      ["متوسط سلة المشتريات", current.avgBasket.toFixed(2), ""],
    ];

    const csvContent = "\uFEFF" + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `Financial_BI_Report_${period}_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast(locale === "ar" ? "تم تصدير التقرير المالي بصيغة CSV بنجاح" : "Report CSV exported successfully");
  };

  return (
    <div className="space-y-4 font-sans antialiased text-foreground">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-4 end-4 z-50 bg-emerald-600 text-white px-4 py-2.5 rounded-xl shadow-2xl text-xs font-bold flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
          <CheckCircle2 className="h-4 w-4" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header & Filter Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-primary/10 text-primary shrink-0">
            <TrendingUp className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-foreground">{t("reports.title")}</h1>
            <p className="text-[11px] text-muted-foreground">{locale === "ar" ? "لوحات معلومات الأداء المالي، سرعة دوران الأدوية، وهيكل المبيعات" : "Financial KPI dashboards, drug turnover & sales channel analytics"}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Period Selector Tabs */}
          <div className="flex items-center bg-muted/40 p-0.5 rounded-lg border text-xs">
            <Button
              variant={period === "month" ? "default" : "ghost"}
              size="sm"
              onClick={() => { setPeriod("month"); showToast("تم تحديث البيانات إلى النطاق الشهري"); }}
              className="h-7 text-xs font-bold px-3"
            >
              {locale === "ar" ? "شهري" : "Monthly"}
            </Button>
            <Button
              variant={period === "quarter" ? "default" : "ghost"}
              size="sm"
              onClick={() => { setPeriod("quarter"); showToast("تم تحديث البيانات إلى النطاق الربع سنوي"); }}
              className="h-7 text-xs font-bold px-3"
            >
              {locale === "ar" ? "ربع سنوي" : "Quarterly"}
            </Button>
            <Button
              variant={period === "year" ? "default" : "ghost"}
              size="sm"
              onClick={() => { setPeriod("year"); showToast("تم تحديث البيانات إلى النطاق السنوي"); }}
              className="h-7 text-xs font-bold px-3"
            >
              {locale === "ar" ? "سنوي" : "Annual"}
            </Button>
          </div>

          <Button variant="outline" size="sm" onClick={handleExportCSV} className="gap-1.5 text-xs font-semibold h-8 border-border">
            <Download className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "تصدير CSV" : "Export CSV"}</span>
          </Button>

          <Button size="sm" onClick={() => setIsPdfModalOpen(true)} className="gap-1.5 text-xs bg-primary hover:bg-primary/90 font-bold h-8 shadow-sm text-white">
            <FileText className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "تحميل التقرير الشامل (PDF)" : "Download PDF"}</span>
          </Button>
        </div>
      </div>

      {/* Top Financial Performance Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "إجمالي الإيرادات" : "Gross Revenue"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-primary">{formatCurrency(current.grossRevenue)}</p>
          <p className="text-[10px] text-emerald-600 mt-1 font-semibold">+18.5% مقارنة بالفترة السابقة</p>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "مجمل الربح الصيدلاني" : "Gross Profit"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-emerald-600">{formatCurrency(current.grossProfit)}</p>
          <p className="text-[10px] text-muted-foreground mt-1">هامش ربح: {current.marginPercent}%</p>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "صافي الأرباح التشغيلية" : "Net Operating Profit"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-emerald-600">{formatCurrency(current.netProfit)}</p>
          <p className="text-[10px] text-muted-foreground mt-1">بعد خصم المصاريف: {formatCurrency(current.operatingExpenses)}</p>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "عدد العمليات ومتوسط السلة" : "Invoices & Basket"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-foreground">{current.totalInvoices.toLocaleString()}</p>
          <p className="text-[10px] text-muted-foreground mt-1">متوسط الفاتورة: {formatCurrency(current.avgBasket)}</p>
        </Card>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Channel Revenue Distribution */}
        <Card className="p-4 space-y-3 rounded-xl border bg-card shadow-sm">
          <div className="flex items-center justify-between border-b pb-2">
            <div>
              <h3 className="font-bold text-xs text-foreground">{t("reports.sales_chart_title")}</h3>
              <p className="text-[10px] text-muted-foreground mt-0.5">
                {locale === "ar" ? `إجمالي إيرادات المبيعات: ${formatCurrency(current.grossRevenue)}` : `Gross Revenue: ${formatCurrency(current.grossRevenue)}`}
              </p>
            </div>
            <BarChart3 className="h-4 w-4 text-primary" />
          </div>

          <div className="space-y-2.5 pt-1">
            {current.channels.map((ch, idx) => (
              <div key={idx} className="space-y-1 text-xs">
                <div className="flex justify-between font-medium">
                  <span>{ch.name}</span>
                  <span className="font-mono font-bold">{formatCurrency(ch.amount)} ({ch.percent}%)</span>
                </div>
                <div className="w-full h-2 rounded-full bg-muted/60 overflow-hidden">
                  <div className={`h-full rounded-full ${ch.color}`} style={{ width: `${ch.percent}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Pharmaceutical Category Breakdown */}
        <Card className="p-4 space-y-3 rounded-xl border bg-card shadow-sm">
          <div className="flex items-center justify-between border-b pb-2">
            <div>
              <h3 className="font-bold text-xs text-foreground">{t("reports.category_chart_title")}</h3>
              <p className="text-[10px] text-muted-foreground mt-0.5">{locale === "ar" ? "توزيع الإيراد حسب التصنيف العلاجي" : "Therapeutic class breakdown"}</p>
            </div>
            <PieChart className="h-4 w-4 text-primary" />
          </div>

          <div className="space-y-2.5 pt-1">
            {current.categories.map((cat, idx) => (
              <div key={idx} className="space-y-1 text-xs">
                <div className="flex justify-between font-medium">
                  <span>{cat.name}</span>
                  <span className="font-mono font-bold">{cat.percent}% ({formatCurrency(cat.revenue)})</span>
                </div>
                <div className="w-full h-2 rounded-full bg-muted/60 overflow-hidden">
                  <div className={`h-full rounded-full ${cat.color}`} style={{ width: `${cat.percent}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Top Fast-Moving Medications Table */}
      <Card className="rounded-xl border bg-card overflow-hidden shadow-sm">
        <CardHeader className="flex flex-row items-center justify-between p-3 border-b bg-muted/20">
          <div>
            <CardTitle className="text-xs font-bold text-foreground">{locale === "ar" ? "الأدوية الأكثر مبيعاً والأعلى دوراناً (Fast-Moving SKUs)" : "Fast-Moving Medications"}</CardTitle>
            <p className="text-[10px] text-muted-foreground">{locale === "ar" ? "تحليل الكميات المباعة، الإيراد المحقق، وهامش الربحية" : "Units sold, revenue contribution, and gross margins"}</p>
          </div>
          <Badge variant="outline" className="text-[10px] font-mono">{current.labelAr}</Badge>
        </CardHeader>

        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-right">
              <thead className="bg-muted/30 font-semibold text-muted-foreground border-b text-[11px]">
                <tr>
                  <th className="p-2.5 text-center">الترتيب</th>
                  <th className="p-2.5">اسم الدواء</th>
                  <th className="p-2.5">التصنيف</th>
                  <th className="p-2.5 text-center">الوحدات المباعة</th>
                  <th className="p-2.5 text-left">إجمالي الإيراد</th>
                  <th className="p-2.5 text-center">هامش الربح</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {current.topMeds.map((med) => (
                  <tr key={med.rank} className="hover:bg-muted/40 transition-colors">
                    <td className="p-2.5 text-center font-mono font-bold text-primary">#{med.rank}</td>
                    <td className="p-2.5 font-bold text-foreground">{med.name}</td>
                    <td className="p-2.5 text-muted-foreground text-[11px]">{med.category}</td>
                    <td className="p-2.5 text-center font-mono font-bold">{med.units.toLocaleString()}</td>
                    <td className="p-2.5 text-left font-mono font-bold text-emerald-600">{formatCurrency(med.revenue)}</td>
                    <td className="p-2.5 text-center">
                      <Badge variant="outline" className="text-[10px] px-2 py-0.5 text-emerald-700 font-mono font-semibold">
                        {med.margin}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Printable Comprehensive PDF Report Modal */}
      {isPdfModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
          <div className="max-w-3xl w-full bg-card rounded-2xl border border-border shadow-2xl p-6 space-y-5 animate-in fade-in zoom-in duration-200 printable-invoice max-h-[92vh] flex flex-col">
            {/* Modal Controls Bar */}
            <div className="flex items-center justify-between border-b pb-3 no-print">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                <div>
                  <h3 className="text-sm font-bold text-foreground">
                    {locale === "ar" ? "التقرير المالي والتشغيلي الشامل (جاهز للطباعة والتصدير)" : "Comprehensive Financial BI Report"}
                  </h3>
                  <span className="text-[11px] text-muted-foreground font-mono">{current.labelAr}</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button size="sm" onClick={() => window.print()} className="gap-1 text-xs font-bold bg-primary hover:bg-primary/90 h-8 text-white shadow-sm">
                  <Printer className="h-3.5 w-3.5" />
                  <span>{locale === "ar" ? "طباعة التقرير" : "Print Report"}</span>
                </Button>
                <Button variant="ghost" size="icon" onClick={() => setIsPdfModalOpen(false)} className="h-8 w-8">
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Document Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/20 rounded-xl border">
              {/* Report Official Header */}
              <div className="flex justify-between items-start pb-4 border-b-2 border-primary">
                <div>
                  <h2 className="text-base font-extrabold text-foreground">سلسلة صيدليات الأمل الحديثة المحدودة</h2>
                  <p className="text-xs text-muted-foreground">الإدارة المالية المركزية — تقرير ذكاء الأعمال المعتمد</p>
                  <p className="text-[10px] text-muted-foreground font-mono mt-1">الرقم الضريبي: 300998877600003 • السجل التجاري: 1010889922</p>
                </div>
                <div className="text-end">
                  <Badge variant="default" className="text-xs px-2.5 py-0.5">{current.labelAr}</Badge>
                  <p className="text-[10px] text-muted-foreground font-mono mt-1">تاريخ الإصدار: {new Date().toISOString().split("T")[0]}</p>
                </div>
              </div>

              {/* Financial Statement Summary */}
              <div className="space-y-2">
                <h4 className="font-bold text-xs text-foreground">1. ملخص قائمة الدخل والأرباح (Income Statement)</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2.5 rounded-lg bg-card border flex justify-between">
                    <span>إجمالي الإيرادات:</span>
                    <span className="font-bold font-mono text-primary">{formatCurrency(current.grossRevenue)}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-card border flex justify-between">
                    <span>تكلفة المبيعات (COGS):</span>
                    <span className="font-mono text-muted-foreground">{formatCurrency(current.cogs)}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-card border flex justify-between">
                    <span>مجمل الأرباح ({current.marginPercent}%):</span>
                    <span className="font-bold font-mono text-emerald-600">{formatCurrency(current.grossProfit)}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-card border flex justify-between">
                    <span>صافي الأرباح بعد المصاريف:</span>
                    <span className="font-extrabold font-mono text-emerald-600 text-sm">{formatCurrency(current.netProfit)}</span>
                  </div>
                </div>
              </div>

              {/* Channel Distribution */}
              <div className="space-y-2">
                <h4 className="font-bold text-xs text-foreground">2. توزيع المبيعات حسب القنوات</h4>
                <div className="p-3 rounded-lg bg-card border space-y-1.5 text-xs">
                  {current.channels.map((ch, i) => (
                    <div key={i} className="flex justify-between">
                      <span>{ch.name}:</span>
                      <span className="font-mono font-bold">{formatCurrency(ch.amount)} ({ch.percent}%)</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sign-off */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t text-center text-xs text-muted-foreground">
                <div>
                  <p className="font-semibold text-foreground">إعداد: المحاسب المالي</p>
                  <p className="font-mono mt-1 text-[11px]">طارق سالم — الإدارة المالية</p>
                </div>
                <div>
                  <p className="font-semibold text-foreground">اعتماد: المدير التنفيذي</p>
                  <p className="font-mono mt-1 text-[11px]">د. عبد الله — سلسلة صيدليات الأمل</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
