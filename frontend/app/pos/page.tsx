"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Search,
  Barcode,
  ShoppingCart,
  Trash2,
  Plus,
  Minus,
  CreditCard,
  Banknote,
  CheckCircle2,
  Clock,
  UserCheck,
  Printer,
  Sparkles,
  Percent,
  Receipt,
  FileText,
  FileCheck,
  X,
  ArrowRight,
  Download,
  ShieldCheck,
  UserPlus,
  Lock,
  Boxes,
  RotateCcw,
  Check,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { ConfirmationDialog } from "@/components/ui/confirmation-dialog";
import { TaxInvoicePrintable, TaxInvoiceData, InvoiceItem } from "@/components/invoice/TaxInvoicePrintable";
import { formatCurrency } from "@/lib/utils";
import { useI18n } from "@/lib/i18n";

interface ProductCatalogItem {
  id: string;
  name: string;
  nameAr: string;
  generic: string;
  barcode: string;
  price: number;
  stock: number;
  isRx: boolean;
}

const mockCatalog: ProductCatalogItem[] = [
  { id: "1", name: "Panadol Extra 500mg (24 Tab)", nameAr: "بنادول اكسترا 500 ملجم (24 قرص)", generic: "Paracetamol", barcode: "628100112233", price: 4.5, stock: 85, isRx: false },
  { id: "2", name: "Augmentin 1g (14 Tab)", nameAr: "أوجمنتين 1 جم (14 قرص)", generic: "Amoxicillin / Clavulanate", barcode: "628100998877", price: 18.25, stock: 40, isRx: true },
  { id: "3", name: "Brufen 400mg (30 Tab)", nameAr: "بروفين 400 ملجم (30 قرص)", generic: "Ibuprofen", barcode: "628100445566", price: 6.75, stock: 120, isRx: false },
  { id: "4", name: "Nexium 40mg (28 Cap)", nameAr: "نيكسيوم 40 ملجم (28 كبسولة)", generic: "Esomeprazole", barcode: "628100778899", price: 28.0, stock: 25, isRx: false },
  { id: "5", name: "Ventolin Inhaler 100mcg", nameAr: "بخاخ فنتولين 100 ميكروجرام", generic: "Salbutamol", barcode: "628100332211", price: 9.5, stock: 60, isRx: true },
  { id: "6", name: "Cataflam 50mg (20 Tab)", nameAr: "كتافلام 50 ملجم (20 قرص)", generic: "Diclofenac Potassium", barcode: "628100883322", price: 5.5, stock: 95, isRx: false },
];

interface CartLine {
  item: ProductCatalogItem;
  quantity: number;
  discount: number;
}

interface CashierProfile {
  id: string;
  name: string;
  empId: string;
  branch: string;
  register: string;
  pin: string;
}

const initialCashiers: CashierProfile[] = [
  { id: "1", name: "فهد المنصور", empId: "EMP-101", branch: "الفرع الرئيسي", register: "صندوق #01", pin: "1234" },
  { id: "2", name: "سارة القحطاني", empId: "EMP-102", branch: "الفرع الرئيسي", register: "صندوق #02", pin: "5678" },
  { id: "3", name: "خالد العتيبي", empId: "EMP-103", branch: "فرع الملز", register: "صندوق #01 (الملز)", pin: "9999" },
];

interface ShiftSession {
  shiftId: string;
  cashierName: string;
  register: string;
  branch: string;
  openingFloat: number;
  openedAt: string;
  isOpen: boolean;
}

export default function PosPage() {
  const { t, locale } = useI18n();
  const searchInputRef = useRef<HTMLInputElement>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [cart, setCart] = useState<CartLine[]>([
    { item: mockCatalog[0], quantity: 2, discount: 0 },
    { item: mockCatalog[2], quantity: 1, discount: 0 },
  ]);

  // Cashier & Shift Session Management State
  const [cashiersList, setCashiersList] = useState<CashierProfile[]>(initialCashiers);
  const [currentShift, setCurrentShift] = useState<ShiftSession>({
    shiftId: "SHF-2026-0821-01",
    cashierName: "فهد المنصور",
    register: "صندوق #01 (نقطة البيع الرئيسية)",
    branch: "الفرع الرئيسي — صيدلية الأمل",
    openingFloat: 150.0,
    openedAt: "08:00 صباحاً",
    isOpen: true,
  });

  // Shift & Cashier Modals
  const [isNewShiftModalOpen, setIsNewShiftModalOpen] = useState(false);
  const [isNewCashierModalOpen, setIsNewCashierModalOpen] = useState(false);
  const [isZReportModalOpen, setIsZReportModalOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // New Shift Form State
  const [selectedShiftCashier, setSelectedShiftCashier] = useState("فهد المنصور");
  const [selectedShiftRegister, setSelectedShiftRegister] = useState("صندوق #01 (نقطة البيع الرئيسية)");
  const [selectedShiftBranch, setSelectedShiftBranch] = useState("الفرع الرئيسي — صيدلية الأمل");
  const [shiftOpeningFloat, setShiftOpeningFloat] = useState<number>(150.0);

  // New Cashier Account Form State
  const [newCashierName, setNewCashierName] = useState("");
  const [newCashierEmpId, setNewCashierEmpId] = useState(`EMP-10${cashiersList.length + 1}`);
  const [newCashierBranch, setNewCashierBranch] = useState("الفرع الرئيسي");
  const [newCashierRegister, setNewCashierRegister] = useState("صندوق #01");
  const [newCashierPin, setNewCashierPin] = useState("1234");

  // Z-Report Actual Drawer Count
  const [actualDrawerCash, setActualDrawerCash] = useState<number>(345.0);

  // Discount State
  const [isDiscountModalOpen, setIsDiscountModalOpen] = useState(false);
  const [discountType, setDiscountType] = useState<"percent" | "fixed">("percent");
  const [discountValue, setDiscountValue] = useState<number>(0);
  const [appliedDiscount, setAppliedDiscount] = useState<{ type: "percent" | "fixed"; value: number }>({ type: "percent", value: 0 });

  // Invoicing & Print Modal State
  const [isInvoiceModalOpen, setIsInvoiceModalOpen] = useState(false);
  const [invoiceFormat, setInvoiceFormat] = useState<"thermal" | "a4">("thermal");
  const [lastInvoiceData, setLastInvoiceData] = useState<TaxInvoiceData | null>(null);

  const [isClearConfirmOpen, setIsClearConfirmOpen] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState(locale === "ar" ? "عميل نقدي (مباشر)" : "Walk-in Cash Customer");

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 2500);
  };

  // Keyboard Shortcuts (F2: Search, F4: Cash, F8: Card, F9: Credit)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "F2") {
        e.preventDefault();
        searchInputRef.current?.focus();
      } else if (e.key === "F4" && cart.length > 0) {
        e.preventDefault();
        handleCheckout("cash");
      } else if (e.key === "F8" && cart.length > 0) {
        e.preventDefault();
        handleCheckout("card");
      } else if (e.key === "F9" && cart.length > 0) {
        e.preventDefault();
        handleCheckout("credit");
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [cart, appliedDiscount, selectedCustomer, currentShift]);

  const filteredCatalog = mockCatalog.filter(
    (p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.nameAr.includes(searchQuery) ||
      p.generic.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.barcode.includes(searchQuery)
  );

  const addToCart = (product: ProductCatalogItem) => {
    setCart((prev) => {
      const existing = prev.find((line) => line.item.id === product.id);
      if (existing) {
        return prev.map((line) =>
          line.item.id === product.id ? { ...line, quantity: line.quantity + 1 } : line
        );
      }
      return [...prev, { item: product, quantity: 1, discount: 0 }];
    });
  };

  const updateQuantity = (id: string, delta: number) => {
    setCart((prev) =>
      prev
        .map((line) => (line.item.id === id ? { ...line, quantity: line.quantity + delta } : line))
        .filter((line) => line.quantity > 0)
    );
  };

  const removeFromCart = (id: string) => {
    setCart((prev) => prev.filter((line) => line.item.id !== id));
  };

  // Calculations
  const subtotal = cart.reduce((acc, line) => acc + line.item.price * line.quantity, 0);
  const discountAmount =
    appliedDiscount.type === "percent"
      ? (subtotal * appliedDiscount.value) / 100
      : Math.min(subtotal, appliedDiscount.value);
  const taxableAmount = Math.max(0, subtotal - discountAmount);
  const vatRate = 5;
  const tax = taxableAmount * (vatRate / 100);
  const grandTotal = taxableAmount + tax;

  const handleApplyDiscount = () => {
    setAppliedDiscount({ type: discountType, value: Number(discountValue) || 0 });
    setIsDiscountModalOpen(false);
  };

  const handleRemoveDiscount = () => {
    setAppliedDiscount({ type: "percent", value: 0 });
    setDiscountValue(0);
  };

  // Handle Opening a New Register / Shift Session
  const handleOpenNewShift = (e: React.FormEvent) => {
    e.preventDefault();
    const newShiftId = `SHF-2026-${Date.now().toString().slice(-6)}`;
    const timeNow = new Date().toLocaleTimeString(locale === "ar" ? "ar-SA" : "en-US", { hour: "2-digit", minute: "2-digit" });
    
    setCurrentShift({
      shiftId: newShiftId,
      cashierName: selectedShiftCashier,
      register: selectedShiftRegister,
      branch: selectedShiftBranch,
      openingFloat: Number(shiftOpeningFloat) || 0,
      openedAt: timeNow,
      isOpen: true,
    });

    setIsNewShiftModalOpen(false);
    showToast(locale === "ar" ? `تم بدء وردية الكاشير بنجاح: ${selectedShiftCashier} (${selectedShiftRegister})` : `Shift ${newShiftId} opened`);
  };

  // Handle Creating a New Cashier Account
  const handleCreateCashierAccount = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCashierName.trim()) return;

    const newCashier: CashierProfile = {
      id: String(Date.now()),
      name: newCashierName,
      empId: newCashierEmpId,
      branch: newCashierBranch,
      register: newCashierRegister,
      pin: newCashierPin,
    };

    setCashiersList([...cashiersList, newCashier]);
    setSelectedShiftCashier(newCashier.name);
    setIsNewCashierModalOpen(false);
    setNewCashierName("");
    showToast(locale === "ar" ? `تم تسجيل حساب الكاشير الجديد [${newCashier.name}] بنجاح` : `Cashier ${newCashier.name} registered`);
  };

  const handleCheckout = (method: "cash" | "card" | "credit") => {
    const invoiceItems: InvoiceItem[] = cart.map((line) => ({
      id: line.item.id,
      name: line.item.name,
      nameAr: line.item.nameAr,
      generic: line.item.generic,
      batchNumber: "BATCH-2026-A1",
      quantity: line.quantity,
      unitPrice: line.item.price,
      discount: line.discount,
      totalPrice: line.item.price * line.quantity,
    }));

    const invoiceData: TaxInvoiceData = {
      invoiceNumber: `INV-2026-${Math.floor(1000 + Math.random() * 9000)}`,
      issueDate: new Date().toISOString().split("T")[0],
      issueTime: new Date().toLocaleTimeString(locale === "ar" ? "ar-SA" : "en-US", { hour: "2-digit", minute: "2-digit" }),
      customerName: selectedCustomer,
      customerType: method === "credit" ? "حساب آجل معتمد (Credit B2B)" : "عميل نقدي",
      paymentMethod: method,
      branchName: currentShift.branch,
      cashierName: `${currentShift.cashierName} (${currentShift.register})`,
      items: invoiceItems,
      subtotal: subtotal,
      discountAmount: discountAmount,
      taxableAmount: taxableAmount,
      vatAmount: tax,
      vatRatePercentage: vatRate,
      grandTotal: grandTotal,
      amountInWordsAr: `المبلغ الإجمالي المعتمد: ${grandTotal.toFixed(2)} دولاراً أمريكياً لا غير`,
    };

    try {
      const existingInvoices = JSON.parse(localStorage.getItem("pharma_sales_invoices") || "[]");
      const newInvoiceEntry = {
        id: String(Date.now()),
        invoiceNo: invoiceData.invoiceNumber,
        customer: invoiceData.customerName,
        customerType: invoiceData.customerType,
        branch: invoiceData.branchName,
        itemsCount: invoiceItems.reduce((acc, i) => acc + i.quantity, 0),
        items: invoiceItems,
        amount: invoiceData.grandTotal,
        subtotal: invoiceData.subtotal,
        discount: invoiceData.discountAmount,
        vat: invoiceData.vatAmount,
        paymentMethod: method,
        status: "completed",
        time: invoiceData.issueTime,
        issueDate: invoiceData.issueDate,
      };
      localStorage.setItem("pharma_sales_invoices", JSON.stringify([newInvoiceEntry, ...existingInvoices]));
    } catch (e) {
      console.error("Failed to sync invoice to localStorage:", e);
    }

    setLastInvoiceData(invoiceData);
    setIsInvoiceModalOpen(true);
  };

  const handleStartNewSale = () => {
    setCart([]);
    handleRemoveDiscount();
    setIsInvoiceModalOpen(false);
  };

  return (
    <div className="flex flex-col lg:flex-row h-[calc(100vh-6.5rem)] gap-4 overflow-hidden font-sans antialiased text-foreground">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-4 end-4 z-50 bg-emerald-600 text-white px-4 py-2.5 rounded-xl shadow-2xl text-xs font-bold flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
          <CheckCircle2 className="h-4 w-4" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Left: Product Grid & Barcode Search */}
      <div className="flex-1 flex flex-col gap-3 overflow-hidden">
        {/* Cashier Session Status Bar & Quick Actions */}
        <div className="flex flex-wrap items-center justify-between gap-2 bg-card p-2.5 rounded-xl border shadow-sm">
          {/* Active Shift Indicator */}
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-600">
              <UserCheck className="h-4 w-4" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-xs font-bold text-foreground">{currentShift.cashierName}</span>
                <span className="text-[10px] text-muted-foreground">({currentShift.register})</span>
              </div>
              <p className="text-[10px] text-muted-foreground">
                العهدة الافتتاحية: <span className="font-mono font-bold text-emerald-600">{formatCurrency(currentShift.openingFloat)}</span> • بدأت: {currentShift.openedAt}
              </p>
            </div>
          </div>

          {/* Action Buttons: New Shift, New Cashier, End Shift */}
          <div className="flex items-center gap-1.5">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsNewShiftModalOpen(true)}
              className="h-7.5 text-xs font-bold gap-1 text-emerald-700 hover:bg-emerald-500/10 border-emerald-300 dark:border-emerald-800"
              title="فتح وردية أو جلسة كاشير جديدة"
            >
              <Plus className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "فتح وردية جديدة" : "Open Shift"}</span>
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsNewCashierModalOpen(true)}
              className="h-7.5 text-xs font-semibold gap-1 text-primary hover:bg-primary/5"
              title="إنشاء وتسجيل حساب كاشير جديد"
            >
              <UserPlus className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "حساب كاشير جديد" : "New Cashier"}</span>
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsZReportModalOpen(true)}
              className="h-7.5 text-xs font-semibold gap-1 text-destructive hover:bg-destructive/10"
              title="إغلاق الوردية وطباعة تقرير Z-Report"
            >
              <Lock className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "إغلاق الوردية (Z-Report)" : "Close Shift"}</span>
            </Button>
          </div>
        </div>

        {/* Clean Barcode & Search Bar */}
        <div className="flex items-center gap-3 bg-card p-2 rounded-xl border shadow-sm">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-3 pointer-events-none" />
            <Input
              ref={searchInputRef}
              type="text"
              placeholder={locale === "ar" ? "امسح الباركود أو ابحث باسم الدواء... (F2)" : "Scan barcode or search medicine... (F2)"}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-14 text-xs rtl:pl-14 rtl:pr-9 font-medium h-8.5"
              autoFocus
            />
            <span className="absolute right-2.5 top-2 text-[10px] font-mono bg-muted px-1.5 py-0.5 rounded text-muted-foreground rtl:right-auto rtl:left-2.5">
              F2
            </span>
          </div>
        </div>

        {/* Product Catalog Grid */}
        <div className="flex-1 overflow-y-auto grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-3 gap-2.5 pr-1">
          {filteredCatalog.length === 0 ? (
            <div className="col-span-full py-12">
              <EmptyState
                icon={Search}
                title={locale === "ar" ? "لا توجد نتائج مطابقة" : "No Matches"}
                description={locale === "ar" ? "تأكد من كتابة الاسم أو مطابقة الباركود." : "Check search keyword or barcode scanner input."}
                actionLabel={locale === "ar" ? "مسح البحث" : "Clear"}
                onAction={() => setSearchQuery("")}
              />
            </div>
          ) : (
            filteredCatalog.map((product) => (
              <Card
                key={product.id}
                onClick={() => addToCart(product)}
                className="group cursor-pointer hover:border-primary/60 hover:shadow-md transition-all flex flex-col justify-between p-3 border bg-card rounded-xl select-none"
              >
                <div>
                  <div className="flex items-start justify-between gap-1.5">
                    <h4 className="font-bold text-xs text-foreground group-hover:text-primary transition-colors leading-tight line-clamp-2">
                      {locale === "ar" ? product.nameAr : product.name}
                    </h4>
                    {product.isRx && (
                      <Badge variant="warning" className="text-[9px] px-1 py-0 shrink-0 font-mono">
                        Rx
                      </Badge>
                    )}
                  </div>
                  <p className="text-[10px] text-muted-foreground mt-0.5 font-mono truncate">{product.generic}</p>
                </div>

                <div className="flex items-center justify-between mt-3 pt-2 border-t border-border/50">
                  <span className="text-sm font-extrabold text-emerald-600 font-mono">
                    {formatCurrency(product.price)}
                  </span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                    product.stock <= 10 ? "bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-400" : "bg-muted text-muted-foreground"
                  }`}>
                    {product.stock} {locale === "ar" ? "متوفر" : "in stock"}
                  </span>
                </div>
              </Card>
            ))
          )}
        </div>
      </div>

      {/* Right: Cart & Billing Terminal */}
      <div className="w-full lg:w-96 flex flex-col bg-card border rounded-2xl p-4 shadow-sm h-full overflow-hidden">
        {/* Cart Header */}
        <div className="flex items-center justify-between pb-3 border-b">
          <div className="flex items-center gap-2">
            <ShoppingCart className="h-4 w-4 text-primary" />
            <h3 className="font-bold text-xs text-foreground">{locale === "ar" ? "سلة البيع الحالية" : "Active Register Cart"}</h3>
            <Badge variant="outline" className="text-[10px] font-mono px-1.5 py-0">
              {cart.reduce((acc, l) => acc + l.quantity, 0)} {locale === "ar" ? "أصناف" : "items"}
            </Badge>
          </div>
          {cart.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsClearConfirmOpen(true)}
              className="text-[11px] h-6 px-2 text-destructive hover:bg-destructive/10"
            >
              <Trash2 className="h-3 w-3" />
              <span>{locale === "ar" ? "تفريغ" : "Clear"}</span>
            </Button>
          )}
        </div>

        {/* Customer Selector */}
        <div className="py-2.5 border-b space-y-1">
          <label className="text-[10px] text-muted-foreground font-semibold block">{locale === "ar" ? "حساب العميل / المريض" : "Customer Account"}</label>
          <select
            value={selectedCustomer}
            onChange={(e) => setSelectedCustomer(e.target.value)}
            className="w-full h-7.5 rounded-lg border border-input bg-background px-2.5 text-xs font-medium text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="عميل نقدي (مباشر)">عميل نقدي (مباشر)</option>
            <option value="محمد الدوسري (تأمين بوبا)">محمد الدوسري (تأمين بوبا)</option>
            <option value="مجمع عيادات الأمل (B2B آجل)">مجمع عيادات الأمل (B2B آجل)</option>
            <option value="شركة الرعاية الشاملة (آجل)">شركة الرعاية الشاملة (آجل)</option>
          </select>
        </div>

        {/* Cart Items List */}
        <div className="flex-1 overflow-y-auto divide-y py-1 pr-1">
          {cart.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-muted-foreground p-6 text-center">
              <ShoppingCart className="h-8 w-8 mb-2 opacity-30" />
              <p className="text-xs font-medium">{locale === "ar" ? "السلة فارغة حالياً" : "Cart is empty"}</p>
              <p className="text-[10px] mt-1">{locale === "ar" ? "امسح الباركود أو انقر على صنف لإضافته" : "Scan item or click to add"}</p>
            </div>
          ) : (
            cart.map((line) => (
              <div key={line.item.id} className="py-2 flex items-center justify-between gap-2 text-xs">
                <div className="flex-1 min-w-0">
                  <h5 className="font-bold text-foreground truncate">{locale === "ar" ? line.item.nameAr : line.item.name}</h5>
                  <div className="text-[10px] text-muted-foreground font-mono">
                    {formatCurrency(line.item.price)} × {line.quantity}
                  </div>
                </div>

                <div className="flex items-center gap-1.5 shrink-0">
                  <div className="flex items-center border rounded-lg overflow-hidden bg-background">
                    <button
                      onClick={() => updateQuantity(line.item.id, -1)}
                      className="p-1 hover:bg-muted text-muted-foreground"
                    >
                      <Minus className="h-3 w-3" />
                    </button>
                    <span className="px-2 font-mono font-bold text-xs">{line.quantity}</span>
                    <button
                      onClick={() => updateQuantity(line.item.id, 1)}
                      className="p-1 hover:bg-muted text-muted-foreground"
                    >
                      <Plus className="h-3 w-3" />
                    </button>
                  </div>
                  <span className="font-mono font-bold text-xs w-14 text-end text-foreground">
                    {formatCurrency(line.item.price * line.quantity)}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Summary & Checkout Section */}
        <div className="pt-3 border-t space-y-2 text-xs">
          <div className="flex justify-between text-muted-foreground text-[11px]">
            <span>{locale === "ar" ? "المجموع الفرعي:" : "Subtotal:"}</span>
            <span className="font-mono">{formatCurrency(subtotal)}</span>
          </div>

          {/* Discount Trigger / Display */}
          <div className="flex justify-between items-center text-[11px]">
            <div className="flex items-center gap-1">
              <span className="text-muted-foreground">{locale === "ar" ? "الخصم التجاري:" : "Discount:"}</span>
              {appliedDiscount.value > 0 ? (
                <button onClick={handleRemoveDiscount} className="text-[10px] text-destructive hover:underline font-semibold">
                  ({locale === "ar" ? "إلغاء" : "Remove"})
                </button>
              ) : (
                <button
                  onClick={() => setIsDiscountModalOpen(true)}
                  className="text-[10px] text-primary hover:underline font-semibold"
                >
                  +{locale === "ar" ? "تطبيق خصم" : "Add Discount"}
                </button>
              )}
            </div>
            <span className="font-mono text-emerald-600 font-bold">
              {discountAmount > 0 ? `-${formatCurrency(discountAmount)}` : formatCurrency(0)}
            </span>
          </div>

          <div className="flex justify-between text-muted-foreground text-[11px]">
            <span>{locale === "ar" ? "ضريبة القيمة المضافة (5%):" : "VAT (5%):"}</span>
            <span className="font-mono">{formatCurrency(tax)}</span>
          </div>

          <div className="flex justify-between text-base font-extrabold text-foreground pt-1 border-t">
            <span>{locale === "ar" ? "الإجمالي الصافي:" : "Net Total:"}</span>
            <span className="font-mono text-emerald-600">{formatCurrency(grandTotal)}</span>
          </div>

          {/* 3-Way Payment Action Buttons */}
          <div className="grid grid-cols-3 gap-1.5 pt-2">
            <Button
              onClick={() => handleCheckout("cash")}
              disabled={cart.length === 0}
              className="gap-1 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 h-9 text-white shadow-sm"
              title="سداد نقدي كاش (F4)"
            >
              <Banknote className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "كاش (F4)" : "Cash (F4)"}</span>
            </Button>

            <Button
              onClick={() => handleCheckout("card")}
              disabled={cart.length === 0}
              className="gap-1 text-xs font-bold bg-blue-600 hover:bg-blue-700 h-9 text-white shadow-sm"
              title="سداد شبكة وبطاقات (F8)"
            >
              <CreditCard className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "شبكة (F8)" : "Card (F8)"}</span>
            </Button>

            <Button
              onClick={() => handleCheckout("credit")}
              disabled={cart.length === 0}
              variant="outline"
              className="gap-1 text-xs font-bold border-amber-500/40 text-amber-700 dark:text-amber-400 hover:bg-amber-500/10 h-9"
              title="بيع آجل على الحساب (F9)"
            >
              <FileCheck className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "آجل (F9)" : "Credit (F9)"}</span>
            </Button>
          </div>
        </div>
      </div>

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
                  {cashiersList.map((c) => (
                    <option key={c.id} value={c.name}>{c.name} ({c.empId})</option>
                  ))}
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
                  بدء الوردية وفتح الصندوق
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

      {/* Modal: Close Shift & Z-Report Reconcile */}
      {isZReportModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="max-w-lg w-full bg-card rounded-2xl border border-border shadow-2xl p-6 space-y-4 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <Receipt className="h-5 w-5 text-amber-600" />
                <div>
                  <h3 className="text-sm font-bold text-foreground">
                    {locale === "ar" ? "إغلاق الوردية وجرد الصندوق (Z-Report)" : "Shift Closing & Z-Report Reconciliation"}
                  </h3>
                  <p className="text-[10px] text-muted-foreground font-mono">{currentShift.shiftId} • {currentShift.cashierName}</p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsZReportModalOpen(false)} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 rounded-xl bg-muted/30 border flex justify-between">
                  <span>العهدة الافتتاحية:</span>
                  <span className="font-mono font-bold text-foreground">{formatCurrency(currentShift.openingFloat)}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-muted/30 border flex justify-between">
                  <span>المبيعات النقدية (كاش):</span>
                  <span className="font-mono font-bold text-emerald-600">{formatCurrency(195.0)}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-muted/30 border flex justify-between">
                  <span>مبيعات الشبكة (بطاقات):</span>
                  <span className="font-mono font-bold text-blue-600">{formatCurrency(480.5)}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-muted/30 border flex justify-between">
                  <span>المبيعات الآجلة:</span>
                  <span className="font-mono font-bold text-amber-600">{formatCurrency(1250.0)}</span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex justify-between items-center font-bold">
                <span>إجمالي النقد المتوقع في الدرج (Expected Drawer):</span>
                <span className="font-mono text-emerald-700 dark:text-emerald-300 text-sm font-extrabold">{formatCurrency(currentShift.openingFloat + 195.0)}</span>
              </div>

              <div className="space-y-1 pt-1">
                <label className="font-semibold text-foreground block text-right">النقد الفعلي المعدود في الدرج ($)</label>
                <Input
                  type="text"
                  inputMode="decimal"
                  value={actualDrawerCash}
                  onChange={(e) => setActualDrawerCash(parseFloat(e.target.value) || 0)}
                  className="h-9 font-mono text-xs font-bold text-center"
                />
              </div>

              <div className="flex justify-between items-center text-xs font-semibold py-1">
                <span>الفارق في الدرج (Variance):</span>
                <span className="font-mono font-bold text-emerald-600">
                  {actualDrawerCash - (currentShift.openingFloat + 195.0) === 0 ? "مطابق (0.00)" : formatCurrency(actualDrawerCash - (currentShift.openingFloat + 195.0))}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t">
              <Button variant="outline" size="sm" onClick={() => window.print()} className="gap-1 text-xs h-8 font-semibold">
                <Printer className="h-3.5 w-3.5" />
                <span>طباعة Z-Report</span>
              </Button>
              <Button
                size="sm"
                onClick={() => {
                  setIsZReportModalOpen(false);
                  showToast("تم إغلاق الوردية وترحيل قيود الإقفال المالي لدفتر الأستاذ");
                }}
                className="text-xs font-bold bg-destructive hover:bg-destructive/90 h-8 px-4 text-white"
              >
                تأكيد إغلاق الوردية
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Discount Application */}
      {isDiscountModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="max-w-sm w-full bg-card rounded-2xl border border-border shadow-2xl p-5 space-y-4 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-2">
              <div className="flex items-center gap-2">
                <Percent className="h-4 w-4 text-primary" />
                <h3 className="font-bold text-xs text-foreground">تطبيق خصم تجاري على الفاتورة</h3>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsDiscountModalOpen(false)} className="h-7 w-7">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center gap-2 bg-muted/40 p-1 rounded-lg border">
                <button
                  type="button"
                  onClick={() => setDiscountType("percent")}
                  className={`flex-1 py-1 text-xs rounded-md font-bold transition-all ${
                    discountType === "percent" ? "bg-background text-primary shadow-sm" : "text-muted-foreground"
                  }`}
                >
                  نسبة مئوية (%)
                </button>
                <button
                  type="button"
                  onClick={() => setDiscountType("fixed")}
                  className={`flex-1 py-1 text-xs rounded-md font-bold transition-all ${
                    discountType === "fixed" ? "bg-background text-primary shadow-sm" : "text-muted-foreground"
                  }`}
                >
                  مبلغ نقدي مقطوع ($)
                </button>
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-foreground block text-right">
                  {discountType === "percent" ? "نسبة الخصم (%)" : "قيمة الخصم بالدولار ($)"}
                </label>
                <Input
                  type="text"
                  inputMode="decimal"
                  value={discountValue}
                  onChange={(e) => setDiscountValue(parseFloat(e.target.value) || 0)}
                  placeholder={discountType === "percent" ? "مثال: 10" : "مثال: 5.00"}
                  className="h-9 font-mono text-xs font-bold text-center"
                  autoFocus
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t">
              <Button variant="outline" size="sm" onClick={() => setIsDiscountModalOpen(false)} className="text-xs h-8">
                إلغاء
              </Button>
              <Button size="sm" onClick={handleApplyDiscount} className="text-xs font-bold bg-primary h-8 px-4">
                تطبيق الخصم
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Official Tax Invoice Printable Presentation */}
      {isInvoiceModalOpen && lastInvoiceData && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
          <div className="max-w-2xl w-full bg-card rounded-2xl border border-border shadow-2xl p-6 space-y-4 animate-in fade-in zoom-in duration-200">
            {/* Modal Controls Bar */}
            <div className="flex items-center justify-between border-b pb-3 no-print">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                <div>
                  <h3 className="text-sm font-bold text-foreground">
                    {locale === "ar" ? "تم اعتماد الفاتورة وسدادها بنجاح" : "Transaction Completed & Paid"}
                  </h3>
                  <span className="text-[11px] text-muted-foreground font-mono">{lastInvoiceData.invoiceNumber}</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <div className="flex items-center bg-muted/60 p-0.5 rounded-lg border text-xs">
                  <button
                    onClick={() => setInvoiceFormat("thermal")}
                    className={`px-2.5 py-1 text-xs rounded-md font-bold transition-all ${
                      invoiceFormat === "thermal" ? "bg-background text-primary shadow-sm" : "text-muted-foreground"
                    }`}
                  >
                    إيصال حراري (80mm)
                  </button>
                  <button
                    onClick={() => setInvoiceFormat("a4")}
                    className={`px-2.5 py-1 text-xs rounded-md font-bold transition-all ${
                      invoiceFormat === "a4" ? "bg-background text-primary shadow-sm" : "text-muted-foreground"
                    }`}
                  >
                    فاتورة ضريبية رسمية (A4)
                  </button>
                </div>

                <Button size="sm" onClick={() => window.print()} className="gap-1 text-xs font-bold bg-primary hover:bg-primary/90 h-8 text-white">
                  <Printer className="h-3.5 w-3.5" />
                  <span>{locale === "ar" ? "طباعة" : "Print"}</span>
                </Button>

                <Button size="sm" onClick={handleStartNewSale} className="gap-1 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 h-8 text-white">
                  <span>{locale === "ar" ? "عملية بيع جديدة" : "New Sale"}</span>
                </Button>
              </div>
            </div>

            {/* Printable Tax Invoice Content */}
            <div className="max-h-[70vh] overflow-y-auto border rounded-xl p-4 bg-muted/10">
              <TaxInvoicePrintable data={lastInvoiceData} format={invoiceFormat} />
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Dialog: Clear Cart */}
      <ConfirmationDialog
        isOpen={isClearConfirmOpen}
        title={locale === "ar" ? "تفريغ سلة المبيعات" : "Clear Active Cart"}
        description={
          locale === "ar"
            ? "هل أنت متأكد من تفريغ جميع الأصناف الحالية من السلة؟ لن يتم حفظ هذه العملية."
            : "Are you sure you want to clear all products from the register cart?"
        }
        confirmLabel={locale === "ar" ? "نعم، تفريغ السلة" : "Clear Cart"}
        cancelLabel={locale === "ar" ? "إلغاء" : "Cancel"}
        onConfirm={() => {
          setCart([]);
          handleRemoveDiscount();
          setIsClearConfirmOpen(false);
        }}
        onCancel={() => setIsClearConfirmOpen(false)}
      />
    </div>
  );
}
