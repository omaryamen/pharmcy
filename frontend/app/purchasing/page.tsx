"use client";

import React, { useState } from "react";
import {
  Plus,
  Search,
  ShoppingBag,
  Truck,
  FileCheck,
  CheckCircle2,
  Clock,
  DollarSign,
  Building,
  Download,
  Eye,
  Check,
  X,
  Printer,
  FileText,
  Boxes,
  ShieldCheck,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ConfirmationDialog } from "@/components/ui/confirmation-dialog";
import { useI18n } from "@/lib/i18n";
import { formatCurrency } from "@/lib/utils";

interface PurchaseOrderRecord {
  id: string;
  poNumber: string;
  supplier: string;
  date: string;
  expectedDate: string;
  itemsCount: number;
  itemsDesc: string;
  amount: number;
  paymentTerms: string;
  status: "received" | "pending_grn" | "draft";
  matching: "matched" | "pending";
}

const initialPurchaseOrders: PurchaseOrderRecord[] = [
  {
    id: "1",
    poNumber: "PO-2026-0041",
    supplier: "شركة نوفارتس للأدوية",
    date: "2026-08-14",
    expectedDate: "2026-08-18",
    itemsCount: 14,
    itemsDesc: "14 صنف أدوية قلب وضغط",
    amount: 14500.0,
    paymentTerms: "آجل 30 يوم",
    status: "received",
    matching: "matched",
  },
  {
    id: "2",
    poNumber: "PO-2026-0042",
    supplier: "فايزر العالمية للتوزيع",
    date: "2026-08-15",
    expectedDate: "2026-08-22",
    itemsCount: 8,
    itemsDesc: "8 أصناف مضادات حيوية ولقاحات",
    amount: 8200.0,
    paymentTerms: "آجل 45 يوم",
    status: "pending_grn",
    matching: "pending",
  },
  {
    id: "3",
    poNumber: "PO-2026-0043",
    supplier: "الشركة السعودية للصناعات الدوائية (سبيماكو)",
    date: "2026-08-16",
    expectedDate: "2026-08-24",
    itemsCount: 22,
    itemsDesc: "22 صنف مسكنات وأدوية جهاز هضمي",
    amount: 19800.0,
    paymentTerms: "آجل 60 يوم",
    status: "draft",
    matching: "pending",
  },
];

export default function PurchasingPage() {
  const { t, locale } = useI18n();
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState<"all" | "pending" | "received" | "draft">("all");
  const [orders, setOrders] = useState<PurchaseOrderRecord[]>(initialPurchaseOrders);
  
  // Modals & States
  const [isNewPoModalOpen, setIsNewPoModalOpen] = useState(false);
  const [selectedPoForView, setSelectedPoForView] = useState<PurchaseOrderRecord | null>(null);
  const [matchingPo, setMatchingPo] = useState<PurchaseOrderRecord | null>(null);
  const [isMatchConfirmOpen, setIsMatchConfirmOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // New PO Form State
  const [newPoSupplier, setNewPoSupplier] = useState("شركة نوفارتس للأدوية");
  const [newPoItemsDesc, setNewPoItemsDesc] = useState("");
  const [newPoItemsCount, setNewPoItemsCount] = useState<number>(5);
  const [newPoAmount, setNewPoAmount] = useState<number>(5000);
  const [newPoExpectedDate, setNewPoExpectedDate] = useState("2026-08-28");
  const [newPoPaymentTerms, setNewPoPaymentTerms] = useState("آجل 30 يوم");

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 2500);
  };

  const handleCreatePo = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPoItemsDesc.trim()) return;
    const newPoNum = `PO-2026-00${44 + orders.length}`;
    const newPo: PurchaseOrderRecord = {
      id: String(Date.now()),
      poNumber: newPoNum,
      supplier: newPoSupplier,
      date: new Date().toISOString().split("T")[0],
      expectedDate: newPoExpectedDate,
      itemsCount: Number(newPoItemsCount) || 1,
      itemsDesc: newPoItemsDesc,
      amount: Number(newPoAmount) || 0,
      paymentTerms: newPoPaymentTerms,
      status: "pending_grn",
      matching: "pending",
    };
    setOrders([newPo, ...orders]);
    setIsNewPoModalOpen(false);
    setNewPoItemsDesc("");
    showToast(locale === "ar" ? `تم إصدار أمر الشراء ${newPoNum} وإرساله للمورد بنجاح` : `Purchase Order ${newPoNum} issued`);
  };

  const handleExecuteThreeWayMatch = () => {
    if (!matchingPo) return;
    const updated = orders.map((o) =>
      o.id === matchingPo.id ? { ...o, status: "received" as const, matching: "matched" as const } : o
    );
    setOrders(updated);
    setIsMatchConfirmOpen(false);
    showToast(
      locale === "ar"
        ? `تمت المطابقة الثلاثية 3-Way Match لأمر الشراء ${matchingPo.poNumber} بنجاح وترحيلها لدفتر الأستاذ`
        : `Three-way match completed for ${matchingPo.poNumber}`
    );
    setMatchingPo(null);
  };

  const handleExportCSV = () => {
    const headers = ["رقم أمر الشراء", "المورد الدوائي", "تاريخ الطلب", "تاريخ الاستحقاق", "الأصناف", "المبلغ الإجمالي", "شروط السداد", "حالة التوريد", "المطابقة الثلاثية"];
    const rows = filteredOrders.map((o) => [
      o.poNumber,
      `"${o.supplier}"`,
      o.date,
      o.expectedDate,
      `"${o.itemsDesc}"`,
      o.amount.toFixed(2),
      `"${o.paymentTerms}"`,
      o.status === "received" ? "تم الاستلام" : o.status === "pending_grn" ? "بانتظار الاستلام" : "مسودة",
      o.matching === "matched" ? "مطابق ومعتمد" : "معلق",
    ]);

    const csvContent = "\uFEFF" + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `Purchase_Orders_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast(locale === "ar" ? "تم تصدير كشف أوامر الشراء بصيغة CSV بنجاح" : "Procurement CSV exported");
  };

  const filteredOrders = orders.filter((po) => {
    const matchesSearch =
      po.poNumber.toLowerCase().includes(search.toLowerCase()) ||
      po.supplier.toLowerCase().includes(search.toLowerCase()) ||
      po.itemsDesc.toLowerCase().includes(search.toLowerCase());

    if (!matchesSearch) return false;
    if (activeFilter === "all") return true;
    if (activeFilter === "pending") return po.status === "pending_grn";
    if (activeFilter === "received") return po.status === "received";
    if (activeFilter === "draft") return po.status === "draft";
    return true;
  });

  const openOrdersGross = orders.filter((o) => o.status === "pending_grn" || o.status === "draft").reduce((acc, o) => acc + o.amount, 0);
  const pendingMatchCount = orders.filter((o) => o.matching === "pending").length;
  const monthlyPurchasesTotal = orders.filter((o) => o.status === "received").reduce((acc, o) => acc + o.amount, 0) + 110000;

  return (
    <div className="space-y-4 font-sans antialiased text-foreground">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-4 end-4 z-50 bg-emerald-600 text-white px-4 py-2.5 rounded-xl shadow-2xl text-xs font-bold flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
          <CheckCircle2 className="h-4 w-4" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header & Purchasing Role Context */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-amber-500/10 text-amber-600 shrink-0">
            <ShoppingBag className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-foreground">{locale === "ar" ? "المشتريات وفواتير الموردين" : "Procurement & Supplier Invoices"}</h1>
            <p className="text-[11px] text-muted-foreground">{locale === "ar" ? "أوامر الشراء (PO)، المطابقة الثلاثية 3-Way Match، وإدارة الذمم الدائنة" : "Purchase orders, three-way match, and vendor accounts payable"}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleExportCSV} className="gap-1.5 text-xs font-semibold h-8 border-border">
            <Download className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "تصدير كشف المشتريات (CSV)" : "Export CSV"}</span>
          </Button>

          <Button size="sm" onClick={() => setIsNewPoModalOpen(true)} className="gap-1.5 text-xs bg-amber-600 hover:bg-amber-700 font-bold h-8 shadow-sm text-white">
            <Plus className="h-3.5 w-3.5" />
            <span>{t("purchasing.new_po")}</span>
          </Button>
        </div>
      </div>

      {/* Purchasing KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "أوامر الشراء المفتوحة" : "Open Purchase Orders"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-foreground">{formatCurrency(openOrdersGross)}</p>
          <p className="text-[10px] text-muted-foreground mt-1">{orders.filter(o => o.status !== "received").length} {locale === "ar" ? "أمر شراء قيد التوريد" : "POs in progress"}</p>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "فواتير بانتظار المطابقة الثلاثية" : "3-Way Match Pending"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-amber-600">{pendingMatchCount}</p>
          <div className="flex items-center gap-1 mt-1 text-[10px] text-amber-600 font-semibold">
            <Clock className="h-3 w-3" />
            <span>{locale === "ar" ? "بانتظار سند الاستلام الفني GRN" : "Awaiting GRN match"}</span>
          </div>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "الموردون المعتمدون" : "Approved Suppliers"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-primary">18</p>
          <p className="text-[10px] text-emerald-600 mt-1 font-semibold">{locale === "ar" ? "مرخصون من هيئة الغذاء والدواء" : "SFDA Accredited"}</p>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "مشتريات الشهر المعتمدة" : "Monthly Purchases"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-emerald-600">{formatCurrency(monthlyPurchasesTotal)}</p>
          <p className="text-[10px] text-muted-foreground mt-1">{locale === "ar" ? "مرحلة تلقائياً إلى دفتر الأستاذ" : "Posted to General Ledger"}</p>
        </Card>
      </div>

      {/* Sub-Tabs Filters */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 p-1 bg-muted/40 rounded-xl border text-xs w-fit">
          <Button
            variant={activeFilter === "all" ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveFilter("all")}
            className="h-7 text-xs font-semibold"
          >
            {locale === "ar" ? "الكل" : "All"} ({orders.length})
          </Button>
          <Button
            variant={activeFilter === "pending" ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveFilter("pending")}
            className="h-7 text-xs font-semibold gap-1"
          >
            <Clock className="h-3 w-3" />
            <span>{locale === "ar" ? "قيد التوريد" : "In Transit"}</span>
          </Button>
          <Button
            variant={activeFilter === "received" ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveFilter("received")}
            className="h-7 text-xs font-semibold gap-1"
          >
            <CheckCircle2 className="h-3 w-3 text-emerald-600" />
            <span>{locale === "ar" ? "تم الاستلام والمطابقة" : "Received & Matched"}</span>
          </Button>
          <Button
            variant={activeFilter === "draft" ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveFilter("draft")}
            className="h-7 text-xs font-semibold"
          >
            {locale === "ar" ? "مسودات" : "Drafts"}
          </Button>
        </div>

        <div className="relative w-64 md:w-80">
          <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-muted-foreground rtl:left-auto rtl:right-2.5 pointer-events-none" />
          <Input
            placeholder={locale === "ar" ? "بحث برقم PO، اسم المورد، الصنف..." : "Search PO #, supplier..."}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-8 text-xs rtl:pl-2.5 rtl:pr-8 h-7.5"
          />
        </div>
      </div>

      {/* Orders Table */}
      <Card className="rounded-xl border bg-card overflow-hidden shadow-sm">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-right">
              <thead className="bg-muted/30 font-semibold text-muted-foreground border-b text-[11px]">
                <tr>
                  <th className="p-2.5">رقم أمر الشراء</th>
                  <th className="p-2.5">شركة التوريد / الوكيل</th>
                  <th className="p-2.5">بيان الأصناف</th>
                  <th className="p-2.5">تاريخ الطلب</th>
                  <th className="p-2.5 text-left">الإجمالي</th>
                  <th className="p-2.5 text-center">حالة التوريد</th>
                  <th className="p-2.5 text-center">المطابقة الثلاثية</th>
                  <th className="p-2.5 text-center">الإجراءات</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredOrders.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="p-8 text-center text-muted-foreground text-xs">
                      {locale === "ar" ? "لا توجد أوامر شراء مطابقة." : "No matching purchase orders."}
                    </td>
                  </tr>
                ) : (
                  filteredOrders.map((po) => (
                    <tr key={po.id} className="hover:bg-muted/40 transition-colors">
                      <td className="p-2.5 font-semibold text-primary font-mono">{po.poNumber}</td>
                      <td className="p-2.5 font-medium text-foreground">{po.supplier}</td>
                      <td className="p-2.5 text-muted-foreground text-[11px]">{po.itemsDesc}</td>
                      <td className="p-2.5 font-mono text-[11px] text-muted-foreground">{po.date}</td>
                      <td className="p-2.5 text-left font-bold font-mono text-emerald-600">{formatCurrency(po.amount)}</td>
                      <td className="p-2.5 text-center">
                        <Badge
                          variant={po.status === "received" ? "success" : po.status === "pending_grn" ? "warning" : "outline"}
                          className="text-[10px] px-2 py-0.5"
                        >
                          {po.status === "received" ? "تم الاستلام" : po.status === "pending_grn" ? "بانتظار الاستلام" : "مسودة"}
                        </Badge>
                      </td>
                      <td className="p-2.5 text-center">
                        <Badge
                          variant={po.matching === "matched" ? "success" : "outline"}
                          className="text-[10px] px-2 py-0.5"
                        >
                          {po.matching === "matched" ? "مطابق (3-Way)" : "معلق"}
                        </Badge>
                      </td>
                      <td className="p-2.5 text-center space-x-1 rtl:space-x-reverse">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedPoForView(po)}
                          className="h-6.5 text-[11px] gap-1 font-semibold text-primary hover:bg-primary/5"
                        >
                          <Eye className="h-3 w-3" />
                          <span>{locale === "ar" ? "معاينة" : "View"}</span>
                        </Button>

                        {po.status !== "received" && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setMatchingPo(po);
                              setIsMatchConfirmOpen(true);
                            }}
                            className="h-6.5 text-[11px] gap-1 text-emerald-600 hover:bg-emerald-500/10 font-bold"
                            title="إتمام الاستلام والمطابقة الثلاثية 3-Way Match"
                          >
                            <ShieldCheck className="h-3.5 w-3.5" />
                            <span>{locale === "ar" ? "مطابقة واستلام" : "Match & Receive"}</span>
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Modal: New Purchase Order (PO Entry) */}
      {isNewPoModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="max-w-lg w-full bg-card rounded-2xl border border-border shadow-2xl p-6 space-y-5 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-amber-500/10 text-amber-600">
                  <ShoppingBag className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-foreground">
                    {locale === "ar" ? "إنشاء أمر شراء وتوريد دوائي (Purchase Order)" : "New Purchase Order (PO)"}
                  </h3>
                  <p className="text-[11px] text-muted-foreground">
                    {locale === "ar" ? "إصدار أمر شراء رسمي للمورد مع شروط السداد والاستلام" : "Issue official supplier procurement order"}
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsNewPoModalOpen(false)} className="h-8 w-8 text-muted-foreground hover:text-foreground">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <form onSubmit={handleCreatePo} className="space-y-4 text-xs">
              <div className="space-y-1.5">
                <label className="font-semibold text-foreground block text-right">شركة التوريد / الوكيل المعتمد</label>
                <select
                  value={newPoSupplier}
                  onChange={(e) => setNewPoSupplier(e.target.value)}
                  className="w-full h-9 rounded-lg border border-input bg-background px-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  <option value="شركة نوفارتس للأدوية">شركة نوفارتس للأدوية</option>
                  <option value="فايزر العالمية للتوزيع">فايزر العالمية للتوزيع</option>
                  <option value="الشركة السعودية للصناعات الدوائية (سبيماكو)">الشركة السعودية للصناعات الدوائية (سبيماكو)</option>
                  <option value="شركة الدواء المحدودة">شركة الدواء المحدودة</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="font-semibold text-foreground block text-right">بيان الأصناف والكميات المطلوبة</label>
                <Input
                  value={newPoItemsDesc}
                  onChange={(e) => setNewPoItemsDesc(e.target.value)}
                  placeholder="مثال: 50 كرتون بنادول + 20 أوجمنتين + 10 نيكسيوم"
                  className="h-9 text-xs"
                  required
                  autoFocus
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground block text-right">عدد الأصناف</label>
                  <Input
                    type="text"
                    inputMode="numeric"
                    value={newPoItemsCount}
                    onChange={(e) => setNewPoItemsCount(parseInt(e.target.value) || 0)}
                    className="h-9 font-mono text-xs font-bold text-center"
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground block text-right">القيمة التقديرية ($)</label>
                  <Input
                    type="text"
                    inputMode="decimal"
                    value={newPoAmount}
                    onChange={(e) => setNewPoAmount(parseFloat(e.target.value) || 0)}
                    className="h-9 font-mono text-xs font-bold text-center text-emerald-600"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground block text-right">التاريخ المتوقع للتسليم</label>
                  <Input
                    type="date"
                    value={newPoExpectedDate}
                    onChange={(e) => setNewPoExpectedDate(e.target.value)}
                    className="h-9 font-mono text-xs"
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground block text-right">شروط السداد (Payment Terms)</label>
                  <select
                    value={newPoPaymentTerms}
                    onChange={(e) => setNewPoPaymentTerms(e.target.value)}
                    className="w-full h-9 rounded-lg border border-input bg-background px-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    <option value="آجل 30 يوم">آجل 30 يوم (Net 30)</option>
                    <option value="آجل 60 يوم">آجل 60 يوم (Net 60)</option>
                    <option value="نقدي عند الاستلام">نقدي عند الاستلام (COD)</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-3 border-t">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsNewPoModalOpen(false)} className="text-xs h-9 px-4">
                  {locale === "ar" ? "إلغاء" : "Cancel"}
                </Button>
                <Button type="submit" size="sm" className="text-xs font-bold bg-amber-600 hover:bg-amber-700 h-9 px-5 text-white shadow-sm">
                  {locale === "ar" ? "إصدار أمر الشراء" : "Issue PO"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: View Purchase Order Document */}
      {selectedPoForView && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="max-w-lg w-full bg-card rounded-2xl border border-border shadow-2xl p-6 space-y-4 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-amber-600" />
                <div>
                  <h3 className="text-sm font-bold text-foreground font-mono">{selectedPoForView.poNumber}</h3>
                  <p className="text-[10px] text-muted-foreground">وثيقة أمر الشراء المعتمدة</p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setSelectedPoForView(null)} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-border/40">
                <span className="text-muted-foreground">المورد:</span>
                <span className="font-bold text-foreground">{selectedPoForView.supplier}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/40">
                <span className="text-muted-foreground">تاريخ الإصدار:</span>
                <span className="font-mono">{selectedPoForView.date}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/40">
                <span className="text-muted-foreground">التاريخ المتوقع للتوريد:</span>
                <span className="font-mono">{selectedPoForView.expectedDate}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/40">
                <span className="text-muted-foreground">الأصناف المطلوبة:</span>
                <span className="font-semibold text-foreground">{selectedPoForView.itemsDesc}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/40">
                <span className="text-muted-foreground">شروط السداد:</span>
                <span className="text-foreground">{selectedPoForView.paymentTerms}</span>
              </div>
              <div className="flex justify-between py-2 text-sm font-bold border-t">
                <span>القيمة الإجمالية:</span>
                <span className="font-mono text-emerald-600">{formatCurrency(selectedPoForView.amount)}</span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-3 border-t">
              <Button variant="outline" size="sm" onClick={() => setSelectedPoForView(null)} className="text-xs h-8">
                {locale === "ar" ? "إغلاق" : "Close"}
              </Button>
              <Button size="sm" onClick={() => window.print()} className="gap-1 text-xs font-bold bg-amber-600 hover:bg-amber-700 h-8 text-white">
                <Printer className="h-3.5 w-3.5" />
                <span>{locale === "ar" ? "طباعة الوثيقة" : "Print PO"}</span>
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Dialog for Three-Way Matching */}
      <ConfirmationDialog
        isOpen={isMatchConfirmOpen}
        title={locale === "ar" ? "تأكيد المطابقة الثلاثية 3-Way Match والاستلام" : "Confirm 3-Way Match & Goods Receipt"}
        description={
          locale === "ar"
            ? `هل تم التحقق من مطابقة أمر الشراء ${matchingPo?.poNumber} مع سند الاستلام الفني GRN وفاتورة المورد بقيمة ${formatCurrency(matchingPo?.amount || 0)}؟ سيتم ترحيل الذمة الدائنة إلى دفتر الأستاذ العام وتحديث المخزون.`
            : `Verify and post 3-way match for PO ${matchingPo?.poNumber} of ${formatCurrency(matchingPo?.amount || 0)}? Accounts payable and inventory balances will be updated.`
        }
        confirmLabel={locale === "ar" ? "اعتماد المطابقة والاستلام" : "Confirm & Match"}
        cancelLabel={locale === "ar" ? "إلغاء" : "Cancel"}
        onConfirm={handleExecuteThreeWayMatch}
        onCancel={() => setIsMatchConfirmOpen(false)}
      />
    </div>
  );
}
