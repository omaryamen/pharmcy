"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Search,
  FileText,
  TrendingUp,
  DollarSign,
  Printer,
  X,
  CheckCircle2,
  ArrowRight,
  Eye,
  Download,
  RotateCcw,
  ShoppingCart,
  Receipt,
  Filter,
  CreditCard,
  Banknote,
  FileCheck,
  AlertOctagon,
  UserPlus,
  Boxes,
  Plus,
  UserCheck,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ConfirmationDialog } from "@/components/ui/confirmation-dialog";
import { TaxInvoicePrintable, TaxInvoiceData, InvoiceItem } from "@/components/invoice/TaxInvoicePrintable";
import { useI18n } from "@/lib/i18n";
import { formatCurrency } from "@/lib/utils";

interface SalesInvoiceRecord {
  id: string;
  invoiceNo: string;
  customer: string;
  customerType: string;
  branch: string;
  itemsCount: number;
  items?: InvoiceItem[];
  amount: number;
  subtotal: number;
  discount: number;
  vat: number;
  paymentMethod: "cash" | "card" | "credit";
  status: "completed" | "refunded";
  time: string;
  issueDate?: string;
}

const defaultInitialInvoices: SalesInvoiceRecord[] = [
  {
    id: "1",
    invoiceNo: "INV-2026-8891",
    customer: "عميل نقدي (مباشر)",
    customerType: "عميل نقدي",
    branch: "الفرع الرئيسي",
    itemsCount: 3,
    items: [
      { id: "1", name: "Panadol Extra 500mg", nameAr: "بنادول اكسترا 500 ملجم", generic: "Paracetamol", batchNumber: "BATCH-2026-A1", quantity: 2, unitPrice: 4.5, totalPrice: 9.0 },
      { id: "2", name: "Brufen 400mg", nameAr: "بروفين 400 ملجم", generic: "Ibuprofen", batchNumber: "BATCH-2026-B2", quantity: 1, unitPrice: 6.75, totalPrice: 6.75 },
    ],
    amount: 16.54,
    subtotal: 15.75,
    discount: 0,
    vat: 0.79,
    paymentMethod: "cash",
    status: "completed",
    time: "منذ دقيقتين",
    issueDate: "2026-08-21",
  },
  {
    id: "2",
    invoiceNo: "INV-2026-8892",
    customer: "محمد الدوسري (تأمين بوبا)",
    customerType: "تأمين طبي معتمد",
    branch: "الفرع الرئيسي",
    itemsCount: 5,
    items: [
      { id: "1", name: "Augmentin 1g", nameAr: "أوجمنتين 1 جم", generic: "Amoxicillin", batchNumber: "BATCH-2026-C3", quantity: 2, unitPrice: 18.25, totalPrice: 36.5 },
      { id: "2", name: "Nexium 40mg", nameAr: "نيكسيوم 40 ملجم", generic: "Esomeprazole", batchNumber: "BATCH-2026-D4", quantity: 5, unitPrice: 28.0, totalPrice: 140.0 },
    ],
    amount: 180.5,
    subtotal: 176.5,
    discount: 5.0,
    vat: 8.58,
    paymentMethod: "card",
    status: "completed",
    time: "منذ 14 دقيقة",
    issueDate: "2026-08-21",
  },
  {
    id: "3",
    invoiceNo: "INV-2026-8893",
    customer: "مجمع عيادات الأمل (B2B آجل)",
    customerType: "حساب منشأة معتمد (Credit B2B)",
    branch: "المستودع المركزي",
    itemsCount: 24,
    items: [
      { id: "1", name: "Augmentin 1g", nameAr: "أوجمنتين 1 جم", generic: "Amoxicillin", batchNumber: "BATCH-2026-C3", quantity: 20, unitPrice: 18.25, totalPrice: 365.0 },
      { id: "2", name: "Ventolin Inhaler", nameAr: "بخاخ فنتولين", generic: "Salbutamol", batchNumber: "BATCH-2026-E5", quantity: 40, unitPrice: 9.5, totalPrice: 380.0 },
    ],
    amount: 1250.0,
    subtotal: 1200.0,
    discount: 50.0,
    vat: 57.5,
    paymentMethod: "credit",
    status: "completed",
    time: "منذ 45 دقيقة",
    issueDate: "2026-08-21",
  },
];

export default function SalesLedgerPage() {
  const { t, locale } = useI18n();
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState<"all" | "cash" | "card" | "credit" | "refunded">("all");
  const [invoices, setInvoices] = useState<SalesInvoiceRecord[]>(defaultInitialInvoices);

  // Modals & States
  const [selectedInvoice, setSelectedInvoice] = useState<SalesInvoiceRecord | null>(null);
  const [refundingInvoice, setRefundingInvoice] = useState<SalesInvoiceRecord | null>(null);
  const [invoiceFormat, setInvoiceFormat] = useState<"thermal" | "a4">("thermal");
  const [isRefundConfirmOpen, setIsRefundConfirmOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Shift & Cashier Modals
  const [isNewShiftModalOpen, setIsNewShiftModalOpen] = useState(false);
  const [isNewCashierModalOpen, setIsNewCashierModalOpen] = useState(false);

  // New Shift Form State
  const [selectedShiftCashier, setSelectedShiftCashier] = useState("فهد المنصور");
  const [selectedShiftRegister, setSelectedShiftRegister] = useState("صندوق #01 (نقطة البيع الرئيسية)");
  const [selectedShiftBranch, setSelectedShiftBranch] = useState("الفرع الرئيسي — صيدلية الأمل");
  const [shiftOpeningFloat, setShiftOpeningFloat] = useState<number>(150.0);

  // New Cashier Form State
  const [newCashierName, setNewCashierName] = useState("");
  const [newCashierEmpId, setNewCashierEmpId] = useState("EMP-104");
  const [newCashierBranch, setNewCashierBranch] = useState("الفرع الرئيسي");
  const [newCashierRegister, setNewCashierRegister] = useState("صندوق #01");
  const [newCashierPin, setNewCashierPin] = useState("1234");

  // Sync with localStorage on mount to pull live POS transactions
  useEffect(() => {
    try {
      const stored = localStorage.getItem("pharma_sales_invoices");
      if (stored) {
        const parsed: SalesInvoiceRecord[] = JSON.parse(stored);
        const merged = [...parsed];
        defaultInitialInvoices.forEach((def) => {
          if (!merged.some((m) => m.invoiceNo === def.invoiceNo)) {
            merged.push(def);
          }
        });
        setInvoices(merged);
      }
    } catch (e) {
      console.error("Error reading stored sales invoices", e);
    }
  }, []);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 2500);
  };

  const handleProcessRefund = () => {
    if (!refundingInvoice) return;
    const updated = invoices.map((inv) =>
      inv.id === refundingInvoice.id ? { ...inv, status: "refunded" as const } : inv
    );
    setInvoices(updated);
    try {
      localStorage.setItem("pharma_sales_invoices", JSON.stringify(updated));
    } catch (e) {}
    setIsRefundConfirmOpen(false);
    showToast(
      locale === "ar"
        ? `تم استرجاع الفاتورة ${refundingInvoice.invoiceNo} وإصدار إشعار دائن ضريبي معتمد`
        : `Invoice ${refundingInvoice.invoiceNo} refunded. Credit note issued.`
    );
    setRefundingInvoice(null);
  };

  const handleOpenNewShift = (e: React.FormEvent) => {
    e.preventDefault();
    const newShiftId = `SHF-2026-${Date.now().toString().slice(-6)}`;
    setIsNewShiftModalOpen(false);
    showToast(locale === "ar" ? `تم بدء وردية الكاشير [${selectedShiftCashier}] بنجاح (${selectedShiftRegister})` : `Shift ${newShiftId} opened`);
    // Automatically switch role and route to pos
    localStorage.setItem("pharma_user_role", "cashier");
    window.location.href = "/pos";
  };

  const handleCreateCashierAccount = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCashierName.trim()) return;
    setIsNewCashierModalOpen(false);
    setNewCashierName("");
    showToast(locale === "ar" ? `تم إنشاء وتفعيل حساب الكاشير [${newCashierName}] بنجاح` : `Cashier profile created`);
  };

  const handleExportCSV = () => {
    const headers = [
      "رقم الفاتورة",
      "العميل / المنشأة",
      "نوع العميل",
      "الفرع",
      "عدد الأصناف",
      "طريقة الدفع",
      "المجموع قبل الضريبة",
      "الخصم",
      "ضريبة القيمة المضافة (5%)",
      "الإجمالي الصافي",
      "حالة الفاتورة",
      "تاريخ ووقت الإصدار",
    ];

    const rows = filteredInvoices.map((inv) => [
      inv.invoiceNo,
      `"${inv.customer}"`,
      `"${inv.customerType}"`,
      `"${inv.branch}"`,
      inv.itemsCount,
      inv.paymentMethod,
      inv.subtotal.toFixed(2),
      inv.discount.toFixed(2),
      inv.vat.toFixed(2),
      inv.amount.toFixed(2),
      inv.status === "completed" ? "مكتملة" : "مستردة (مرتجع)",
      `"${inv.issueDate || '2026-08-21'} ${inv.time}"`,
    ]);

    const csvContent = "\uFEFF" + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `Sales_Report_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast(locale === "ar" ? "تم تصدير كشف المبيعات بصيغة CSV بنجاح" : "Sales CSV exported successfully");
  };

  const filteredInvoices = invoices.filter((inv) => {
    const matchesSearch =
      inv.invoiceNo.toLowerCase().includes(search.toLowerCase()) ||
      inv.customer.toLowerCase().includes(search.toLowerCase()) ||
      inv.paymentMethod.toLowerCase().includes(search.toLowerCase());

    if (!matchesSearch) return false;
    if (activeFilter === "all") return true;
    if (activeFilter === "refunded") return inv.status === "refunded";
    return inv.paymentMethod === activeFilter && inv.status !== "refunded";
  });

  const getTaxInvoiceData = (inv: SalesInvoiceRecord): TaxInvoiceData => ({
    invoiceNumber: inv.invoiceNo,
    issueDate: inv.issueDate || "2026-08-21",
    issueTime: inv.time,
    customerName: inv.customer,
    customerType: inv.customerType,
    paymentMethod: inv.paymentMethod,
    branchName: inv.branch,
    cashierName: "فهد (صندوق #1)",
    items: inv.items || [],
    subtotal: inv.subtotal,
    discountAmount: inv.discount,
    taxableAmount: inv.subtotal - inv.discount,
    vatAmount: inv.vat,
    vatRatePercentage: 5,
    grandTotal: inv.amount,
    amountInWordsAr: `المبلغ الإجمالي المعتمد: ${inv.amount.toFixed(2)} دولاراً أمريكياً لا غير`,
  });

  const totalSalesGross = invoices.filter((i) => i.status === "completed").reduce((acc, i) => acc + i.amount, 0);
  const totalDiscounts = invoices.reduce((acc, i) => acc + (i.discount || 0), 0);
  const totalCreditSales = invoices.filter((i) => i.paymentMethod === "credit" && i.status === "completed").reduce((acc, i) => acc + i.amount, 0);

  const handleOpenPosTerminal = () => {
    const currentRole = localStorage.getItem("pharma_user_role") || "cashier";
    if (currentRole === "accountant" || currentRole === "inventory_manager" || currentRole === "superadmin") {
      localStorage.setItem("pharma_user_role", "cashier");
    }
    window.location.href = "/pos";
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

      {/* Header with Direct POS Link, Cashier Shift Actions & CSV Export */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-600 shrink-0">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-foreground">{locale === "ar" ? "سجل فواتير المبيعات الضريبية" : "Tax Invoices & Sales Receipts"}</h1>
            <p className="text-[11px] text-muted-foreground">{locale === "ar" ? "إدارة فواتير الكاشير، ورديات نقاط البيع، المبيعات الآجلة، والمرتجعات" : "POS cashier transactions, shift sessions, credit invoices, and refunds"}</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsNewShiftModalOpen(true)}
            className="gap-1.5 text-xs font-bold h-8 text-emerald-700 border-emerald-300 dark:border-emerald-800 hover:bg-emerald-500/10"
          >
            <Boxes className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "فتح وردية كاشير جديدة" : "Open Shift"}</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsNewCashierModalOpen(true)}
            className="gap-1.5 text-xs font-semibold h-8 border-border text-primary hover:bg-primary/5"
          >
            <UserPlus className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "حساب كاشير جديد" : "New Cashier"}</span>
          </Button>

          <Button variant="outline" size="sm" onClick={handleExportCSV} className="gap-1.5 text-xs font-semibold h-8 border-border">
            <Download className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "تصدير كشف المبيعات (CSV)" : "Export CSV"}</span>
          </Button>

          <Button size="sm" onClick={handleOpenPosTerminal} className="gap-1.5 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 h-8 shadow-sm text-white">
            <ShoppingCart className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "فتح نقطة البيع (POS)" : "Open POS Terminal"}</span>
          </Button>
        </div>
      </div>

      {/* Sales KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "إجمالي مبيعات اليوم" : "Today's Gross Sales"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-emerald-600">{formatCurrency(totalSalesGross)}</p>
          <p className="text-[10px] text-muted-foreground mt-1">+14.2% مقارنة بالأمس</p>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "عدد الفواتير الصادرة" : "Invoices Count"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-foreground">{invoices.length}</p>
          <p className="text-[10px] text-muted-foreground mt-1">{invoices.filter((i) => i.status === "refunded").length} مرتجعات مستردة</p>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "المبيعات الآجلة (B2B Credit)" : "B2B Credit Sales"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-amber-600">{formatCurrency(totalCreditSales)}</p>
          <p className="text-[10px] text-muted-foreground mt-1">مرحلة إلى دفتر الذمم المدينة</p>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "إجمالي الخصومات الممنوحة" : "Total Discounts"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-destructive">{formatCurrency(totalDiscounts)}</p>
          <p className="text-[10px] text-muted-foreground mt-1">عروض ترويجية وخصومات عملاء</p>
        </Card>
      </div>

      {/* Sub-Tab Filter Navigation & Search */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 p-1 bg-muted/40 rounded-xl border text-xs w-fit">
          <Button
            variant={activeFilter === "all" ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveFilter("all")}
            className="h-7 text-xs font-semibold"
          >
            {locale === "ar" ? "الكل" : "All"} ({invoices.length})
          </Button>
          <Button
            variant={activeFilter === "cash" ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveFilter("cash")}
            className="h-7 text-xs font-semibold gap-1"
          >
            <Banknote className="h-3 w-3 text-emerald-600" />
            <span>{locale === "ar" ? "نقدي (كاش)" : "Cash"}</span>
          </Button>
          <Button
            variant={activeFilter === "card" ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveFilter("card")}
            className="h-7 text-xs font-semibold gap-1"
          >
            <CreditCard className="h-3 w-3 text-blue-600" />
            <span>{locale === "ar" ? "شبكة وبطاقات" : "Card"}</span>
          </Button>
          <Button
            variant={activeFilter === "credit" ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveFilter("credit")}
            className="h-7 text-xs font-semibold gap-1"
          >
            <FileCheck className="h-3 w-3 text-amber-600" />
            <span>{locale === "ar" ? "آجل (B2B)" : "Credit"}</span>
          </Button>
          <Button
            variant={activeFilter === "refunded" ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveFilter("refunded")}
            className="h-7 text-xs font-semibold gap-1 text-destructive"
          >
            <RotateCcw className="h-3 w-3" />
            <span>{locale === "ar" ? "المرتجعات" : "Refunds"}</span>
          </Button>
        </div>

        <div className="relative w-64 md:w-80">
          <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-muted-foreground rtl:left-auto rtl:right-2.5 pointer-events-none" />
          <Input
            placeholder={locale === "ar" ? "بحث برقم الفاتورة، اسم العميل، طريقة الدفع..." : "Search invoice #, customer..."}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-8 text-xs rtl:pl-2.5 rtl:pr-8 h-7.5"
          />
        </div>
      </div>

      {/* Invoices Master Table */}
      <Card className="rounded-xl border bg-card overflow-hidden shadow-sm">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-right">
              <thead className="bg-muted/30 font-semibold text-muted-foreground border-b text-[11px]">
                <tr>
                  <th className="p-2.5">رقم الفاتورة</th>
                  <th className="p-2.5">العميل / المنشأة</th>
                  <th className="p-2.5">الفرع</th>
                  <th className="p-2.5 text-center">عدد الأصناف</th>
                  <th className="p-2.5 text-center">طريقة الدفع</th>
                  <th className="p-2.5 text-left">الإجمالي الصافي</th>
                  <th className="p-2.5 text-center">الحالة</th>
                  <th className="p-2.5">التوقيت</th>
                  <th className="p-2.5 text-center">الإجراءات</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredInvoices.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="p-8 text-center text-muted-foreground text-xs">
                      {locale === "ar" ? "لا توجد فواتير مطابقة للبحث الحالي." : "No matching invoices found."}
                    </td>
                  </tr>
                ) : (
                  filteredInvoices.map((inv) => (
                    <tr key={inv.id} className="hover:bg-muted/40 transition-colors">
                      <td className="p-2.5 font-bold text-primary font-mono">{inv.invoiceNo}</td>
                      <td className="p-2.5">
                        <div className="font-semibold text-foreground">{inv.customer}</div>
                        <div className="text-[10px] text-muted-foreground">{inv.customerType}</div>
                      </td>
                      <td className="p-2.5 text-muted-foreground text-[11px]">{inv.branch}</td>
                      <td className="p-2.5 text-center font-mono font-bold">{inv.itemsCount}</td>
                      <td className="p-2.5 text-center">
                        <Badge
                          variant={inv.paymentMethod === "cash" ? "success" : inv.paymentMethod === "card" ? "default" : "outline"}
                          className="text-[10px] px-2 py-0.5"
                        >
                          {inv.paymentMethod === "cash" ? "كاش 💵" : inv.paymentMethod === "card" ? "شبكة 💳" : "آجل 📝"}
                        </Badge>
                      </td>
                      <td className="p-2.5 text-left font-mono font-bold text-emerald-600 text-sm">
                        {formatCurrency(inv.amount)}
                      </td>
                      <td className="p-2.5 text-center">
                        <Badge
                          variant={inv.status === "completed" ? "success" : "destructive"}
                          className="text-[10px] px-2 py-0.5"
                        >
                          {inv.status === "completed" ? (locale === "ar" ? "مكتملة ومسددة" : "Paid") : (locale === "ar" ? "مستردة (مرتجع)" : "Refunded")}
                        </Badge>
                      </td>
                      <td className="p-2.5 text-muted-foreground text-[11px] font-mono">{inv.time}</td>
                      <td className="p-2.5 text-center space-x-1 rtl:space-x-reverse">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedInvoice(inv)}
                          className="h-6.5 text-[11px] gap-1 font-semibold text-primary hover:bg-primary/5"
                        >
                          <Eye className="h-3 w-3" />
                          <span>{locale === "ar" ? "معاينة" : "View"}</span>
                        </Button>

                        {inv.status === "completed" && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setRefundingInvoice(inv);
                              setIsRefundConfirmOpen(true);
                            }}
                            className="h-6.5 text-[11px] gap-1 text-destructive hover:bg-destructive/10"
                            title="إصدار إشعار دائن واسترجاع الفاتورة"
                          >
                            <RotateCcw className="h-3 w-3" />
                            <span>{locale === "ar" ? "استرجاع" : "Refund"}</span>
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

      {/* Modal: Open New Shift / Session */}
      {isNewShiftModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-card rounded-2xl border border-border shadow-2xl p-6 space-y-4 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <Boxes className="h-5 w-5 text-emerald-600" />
                <div>
                  <h3 className="text-sm font-bold text-foreground">
                    {locale === "ar" ? "فتح جلسة / وردية كاشير جديدة" : "Open New POS Shift Session"}
                  </h3>
                  <p className="text-[10px] text-muted-foreground">تسجيل عهدة الصندوق وتعيين الكاشير المسؤول</p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsNewShiftModalOpen(false)} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <form onSubmit={handleOpenNewShift} className="space-y-3.5 text-xs">
              <div className="space-y-1">
                <label className="font-semibold text-foreground block text-right">أمين الصندوق (الكاشير)</label>
                <select
                  value={selectedShiftCashier}
                  onChange={(e) => setSelectedShiftCashier(e.target.value)}
                  className="w-full h-9 rounded-lg border border-input bg-background px-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  <option value="فهد المنصور">فهد المنصور (EMP-101)</option>
                  <option value="سارة القحطاني">سارة القحطاني (EMP-102)</option>
                  <option value="خالد العتيبي">خالد العتيبي (EMP-103)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                <div className="space-y-1">
                  <label className="font-semibold text-foreground block text-right">صندوق / نقطة البيع</label>
                  <select
                    value={selectedShiftRegister}
                    onChange={(e) => setSelectedShiftRegister(e.target.value)}
                    className="w-full h-9 rounded-lg border border-input bg-background px-2.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    <option value="صندوق #01 (نقطة البيع الرئيسية)">صندوق #01 (الرئيسي)</option>
                    <option value="صندوق #02 (الكاشير السريع)">صندوق #02 (السريع)</option>
                    <option value="صندوق #03 (قسم التجميل)">صندوق #03 (التجميل)</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="font-semibold text-foreground block text-right">الفرع</label>
                  <select
                    value={selectedShiftBranch}
                    onChange={(e) => setSelectedShiftBranch(e.target.value)}
                    className="w-full h-9 rounded-lg border border-input bg-background px-2.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    <option value="الفرع الرئيسي — صيدلية الأمل">الفرع الرئيسي</option>
                    <option value="فرع 2 (الملز)">فرع 2 (الملز)</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-foreground block text-right">الرصيد الافتتاحي للعهدة النقدية في الدرج ($)</label>
                <Input
                  type="text"
                  inputMode="decimal"
                  value={shiftOpeningFloat}
                  onChange={(e) => setShiftOpeningFloat(parseFloat(e.target.value) || 0)}
                  className="h-9 font-mono text-xs font-bold text-center text-emerald-600"
                  required
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsNewShiftModalOpen(false)} className="text-xs h-8">
                  إلغاء
                </Button>
                <Button type="submit" size="sm" className="text-xs font-bold bg-emerald-600 hover:bg-emerald-700 h-8 px-5 text-white">
                  بدء الوردية وفتح نقطة البيع
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Register New Cashier Account */}
      {isNewCashierModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-card rounded-2xl border border-border shadow-2xl p-6 space-y-4 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <UserPlus className="h-5 w-5 text-primary" />
                <div>
                  <h3 className="text-sm font-bold text-foreground">
                    {locale === "ar" ? "إنشاء وتسجيل حساب كاشير جديد" : "Create New Cashier Profile"}
                  </h3>
                  <p className="text-[10px] text-muted-foreground">إضافة موظف صندوق لنقاط البيع مع تعيين الصلاحيات</p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsNewCashierModalOpen(false)} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <form onSubmit={handleCreateCashierAccount} className="space-y-3.5 text-xs">
              <div className="space-y-1">
                <label className="font-semibold text-foreground block text-right">الاسم الكامل للكاشير / الصيدلي</label>
                <Input
                  value={newCashierName}
                  onChange={(e) => setNewCashierName(e.target.value)}
                  placeholder="مثال: عبد الرحمن السالم"
                  className="h-9 text-xs"
                  required
                  autoFocus
                />
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                <div className="space-y-1">
                  <label className="font-semibold text-foreground block text-right">الرقم الوظيفي</label>
                  <Input
                    value={newCashierEmpId}
                    onChange={(e) => setNewCashierEmpId(e.target.value)}
                    className="h-9 font-mono text-xs"
                    required
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-semibold text-foreground block text-right">رمز الدخول (PIN)</label>
                  <Input
                    type="password"
                    maxLength={4}
                    value={newCashierPin}
                    onChange={(e) => setNewCashierPin(e.target.value)}
                    className="h-9 font-mono text-xs text-center"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                <div className="space-y-1">
                  <label className="font-semibold text-foreground block text-right">الفرع المخصص</label>
                  <select
                    value={newCashierBranch}
                    onChange={(e) => setNewCashierBranch(e.target.value)}
                    className="w-full h-9 rounded-lg border border-input bg-background px-2.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    <option value="الفرع الرئيسي">الفرع الرئيسي</option>
                    <option value="فرع الملز">فرع الملز</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="font-semibold text-foreground block text-right">الصندوق الافتراضي</label>
                  <select
                    value={newCashierRegister}
                    onChange={(e) => setNewCashierRegister(e.target.value)}
                    className="w-full h-9 rounded-lg border border-input bg-background px-2.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    <option value="صندوق #01">صندوق #01</option>
                    <option value="صندوق #02">صندوق #02</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsNewCashierModalOpen(false)} className="text-xs h-8">
                  إلغاء
                </Button>
                <Button type="submit" size="sm" className="text-xs font-bold bg-primary hover:bg-primary/90 h-8 px-5 text-white">
                  حفظ وإنشاء الحساب
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Confirmation Dialog: Refund Invoice */}
      <ConfirmationDialog
        isOpen={isRefundConfirmOpen}
        title={locale === "ar" ? "تأكيد استرجاع الفاتورة الضريبية" : "Confirm Tax Invoice Refund"}
        description={
          locale === "ar"
            ? `هل أنت متأكد من استرجاع الفاتورة رقم [${refundingInvoice?.invoiceNo}] بقيمة ${formatCurrency(refundingInvoice?.amount || 0)}؟ سيتم إصدار إشعار دائن ضريبي معتمد وإعادة الكميات إلى المخزون.`
            : `Refund invoice [${refundingInvoice?.invoiceNo}] of amount ${formatCurrency(refundingInvoice?.amount || 0)}? A credit note will be issued and stock reversed.`
        }
        confirmLabel={locale === "ar" ? "تأكيد الاسترجاع وإصدار الإشعار" : "Confirm Refund"}
        cancelLabel={locale === "ar" ? "إلغاء" : "Cancel"}
        onConfirm={handleProcessRefund}
        onCancel={() => setIsRefundConfirmOpen(false)}
      />

      {/* Modal: View Tax Invoice Printable Presentation */}
      {selectedInvoice && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
          <Card className="max-w-2xl w-full p-6 space-y-4 shadow-2xl border bg-card rounded-2xl animate-in fade-in zoom-in duration-200 printable-invoice max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between border-b pb-3 no-print">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                <div>
                  <h3 className="text-sm font-bold text-foreground">
                    {locale === "ar" ? "معاينة الفاتورة الضريبية الرسمية" : "Official Tax Invoice"}
                  </h3>
                  <span className="text-[11px] text-muted-foreground font-mono">{selectedInvoice.invoiceNo}</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <div className="flex items-center bg-muted/40 p-1 rounded-lg border text-xs">
                  <Button
                    variant={invoiceFormat === "thermal" ? "default" : "ghost"}
                    size="sm"
                    onClick={() => setInvoiceFormat("thermal")}
                    className="h-7 text-xs font-bold"
                  >
                    إيصال حراري (80mm)
                  </Button>
                  <Button
                    variant={invoiceFormat === "a4" ? "default" : "ghost"}
                    size="sm"
                    onClick={() => setInvoiceFormat("a4")}
                    className="h-7 text-xs font-bold"
                  >
                    فاتورة رسمية (A4)
                  </Button>
                </div>

                <Button onClick={() => window.print()} size="sm" className="gap-1.5 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 h-8 shadow-sm text-white">
                  <Printer className="h-3.5 w-3.5" />
                  <span>{locale === "ar" ? "طباعة" : "Print"}</span>
                </Button>

                <Button variant="ghost" size="icon" onClick={() => setSelectedInvoice(null)} className="h-7 w-7">
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 bg-muted/30 rounded-xl border flex justify-center">
              <TaxInvoicePrintable data={getTaxInvoiceData(selectedInvoice)} format={invoiceFormat} />
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
