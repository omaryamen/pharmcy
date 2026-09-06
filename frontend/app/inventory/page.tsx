"use client";

import React, { useState } from "react";
import {
  Search,
  Plus,
  Layers,
  Package,
  Clock,
  ShieldAlert,
  ArrowRightLeft,
  Truck,
  FileCheck,
  CheckCircle2,
  X,
  Download,
  Edit,
  Save,
  Check,
  AlertTriangle,
  RotateCcw,
  Calendar,
  Building2,
  DollarSign,
  Boxes,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";
import { useI18n } from "@/lib/i18n";

type InventoryTab = "stock" | "transfers" | "receiving" | "counts";

interface InventoryRow {
  id: string;
  code: string;
  name: string;
  nameAr: string;
  generic: string;
  batchNumber: string;
  expiryDate: string;
  warehouse: string;
  warehouseAr: string;
  quantityOnHand: number;
  unitCost: number;
  status: "available" | "near_expiry" | "low_stock";
}

const initialInventoryData: InventoryRow[] = [
  {
    id: "1",
    code: "MED-PAN-001",
    name: "Panadol Extra 500mg",
    nameAr: "بنادول اكسترا 500 ملجم",
    generic: "Paracetamol",
    batchNumber: "BATCH-2026-A1",
    expiryDate: "2027-08-30",
    warehouse: "Main Warehouse (Shelf A1)",
    warehouseAr: "المستودع الرئيسي (الرف A1)",
    quantityOnHand: 450,
    unitCost: 2.8,
    status: "available",
  },
  {
    id: "2",
    code: "MED-AUG-002",
    name: "Augmentin 1g Tablets",
    nameAr: "أوجمنتين 1 جم أقراص",
    generic: "Amoxicillin / Clavulanate",
    batchNumber: "BATCH-2025-C9",
    expiryDate: "2026-09-10",
    warehouse: "Main Warehouse (Cold Zone)",
    warehouseAr: "المستودع الرئيسي (منطقة التبريد)",
    quantityOnHand: 8,
    unitCost: 12.5,
    status: "low_stock",
  },
  {
    id: "3",
    code: "MED-BRU-003",
    name: "Brufen 400mg",
    nameAr: "بروفين 400 ملجم",
    generic: "Ibuprofen",
    batchNumber: "BATCH-2026-D4",
    expiryDate: "2026-09-01",
    warehouse: "West Branch Storage",
    warehouseAr: "مستودع فرع الغرب",
    quantityOnHand: 220,
    unitCost: 3.9,
    status: "near_expiry",
  },
  {
    id: "4",
    code: "MED-NEX-004",
    name: "Nexium 40mg (28 Cap)",
    nameAr: "نيكسيوم 40 ملجم (28 كبسولة)",
    generic: "Esomeprazole",
    batchNumber: "BATCH-2026-E5",
    expiryDate: "2027-12-15",
    warehouse: "Main Warehouse (Shelf B3)",
    warehouseAr: "المستودع الرئيسي (الرف B3)",
    quantityOnHand: 180,
    unitCost: 19.5,
    status: "available",
  },
];

interface TransferRecord {
  id: string;
  transferNo: string;
  from: string;
  to: string;
  itemsCount: string;
  status: "completed" | "in_transit";
  date: string;
}

const initialTransfers: TransferRecord[] = [
  { id: "1", transferNo: "TRF-2026-081", from: "المستودع المركزي", to: "الفرع الرئيسي", itemsCount: "14 صنف", status: "completed", date: "2026-08-20" },
  { id: "2", transferNo: "TRF-2026-082", from: "المستودع المركزي", to: "فرع 2 (الملز)", itemsCount: "8 أصناف", status: "in_transit", date: "2026-08-21" },
];

interface GrnRecord {
  id: string;
  grnNo: string;
  supplier: string;
  poNo: string;
  amount: number;
  status: "verified" | "pending";
  date: string;
}

const initialGrns: GrnRecord[] = [
  { id: "1", grnNo: "GRN-2026-114", supplier: "شركة الدواء المحدودة", poNo: "PO-2026-009", amount: 14500.0, status: "verified", date: "2026-08-19" },
  { id: "2", grnNo: "GRN-2026-115", supplier: "سقالة للأدوية والتوزيع", poNo: "PO-2026-010", amount: 8900.0, status: "verified", date: "2026-08-21" },
];

export default function InventoryPage() {
  const { t, locale } = useI18n();
  const [activeTab, setActiveTab] = useState<InventoryTab>("stock");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "available" | "near_expiry" | "low_stock">("all");
  const [inventory, setInventory] = useState<InventoryRow[]>(initialInventoryData);
  const [transfers, setTransfers] = useState<TransferRecord[]>(initialTransfers);
  const [grns, setGrns] = useState<GrnRecord[]>(initialGrns);
  
  // Modals
  const [isGrnModalOpen, setIsGrnModalOpen] = useState(false);
  const [isTransferModalOpen, setIsTransferModalOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // New GRN Form State
  const [newGrnSupplier, setNewGrnSupplier] = useState("شركة الدواء المحدودة");
  const [newGrnMedicine, setNewGrnMedicine] = useState("");
  const [newGrnBatch, setNewGrnBatch] = useState("BATCH-2026-N1");
  const [newGrnExpiry, setNewGrnExpiry] = useState("2028-06-30");
  const [newGrnQty, setNewGrnQty] = useState<number>(100);
  const [newGrnCost, setNewGrnCost] = useState<number>(5.0);

  // New Transfer Form State
  const [transferFrom, setTransferFrom] = useState("المستودع المركزي");
  const [transferTo, setTransferTo] = useState("الفرع الرئيسي");
  const [transferItemsCount, setTransferItemsCount] = useState("5 أصناف");

  // Stock Count Session State
  const [stockCounts, setStockCounts] = useState<{ [id: string]: number }>({ "1": 450, "2": 8, "3": 220, "4": 180 });
  const [isCountCompleted, setIsCountCompleted] = useState(false);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 2500);
  };

  const handleCreateGrn = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGrnMedicine.trim()) return;
    const newGrnNumber = `GRN-2026-${115 + grns.length}`;
    const totalAmount = newGrnQty * newGrnCost;

    const newGrnEntry: GrnRecord = {
      id: String(Date.now()),
      grnNo: newGrnNumber,
      supplier: newGrnSupplier,
      poNo: `PO-2026-0${10 + grns.length}`,
      amount: totalAmount,
      status: "verified",
      date: new Date().toISOString().split("T")[0],
    };
    setGrns([newGrnEntry, ...grns]);

    const newStockRow: InventoryRow = {
      id: String(Date.now()),
      code: `MED-${newGrnMedicine.substring(0, 3).toUpperCase()}-00${inventory.length + 1}`,
      name: newGrnMedicine,
      nameAr: newGrnMedicine,
      generic: "Formula verified",
      batchNumber: newGrnBatch,
      expiryDate: newGrnExpiry,
      warehouse: "Main Warehouse (Shelf A1)",
      warehouseAr: "المستودع الرئيسي (الرف A1)",
      quantityOnHand: Number(newGrnQty),
      unitCost: Number(newGrnCost),
      status: "available",
    };
    setInventory([newStockRow, ...inventory]);

    setIsGrnModalOpen(false);
    setNewGrnMedicine("");
    showToast(locale === "ar" ? `تم استلام الشحنة وتوليد سند ${newGrnNumber} وتحديث الأرصدة` : `GRN ${newGrnNumber} created successfully`);
  };

  const handleCreateTransfer = (e: React.FormEvent) => {
    e.preventDefault();
    const newTrf: TransferRecord = {
      id: String(Date.now()),
      transferNo: `TRF-2026-08${transfers.length + 3}`,
      from: transferFrom,
      to: transferTo,
      itemsCount: transferItemsCount,
      status: "in_transit",
      date: new Date().toISOString().split("T")[0],
    };
    setTransfers([newTrf, ...transfers]);
    setIsTransferModalOpen(false);
    showToast(locale === "ar" ? `تم إنشاء أمر التحويل ${newTrf.transferNo} وإرساله للشحن` : `Transfer ${newTrf.transferNo} created`);
  };

  const handleConfirmStockCount = () => {
    setIsCountCompleted(true);
    showToast(locale === "ar" ? "تم اعتماد نتائج الجرد الفعلي ومطابقة السجلات" : "Stock count verified & reconciled");
  };

  const handleExportCSV = () => {
    const headers = ["رمز الدواء", "اسم الصنف", "التركيبة", "رقم التشغيلة", "تاريخ الصلاحية", "المستودع", "الرصيد الفعلي", "تكلفة الوحدة", "الحالة"];
    const rows = filtered.map((i) => [
      i.code,
      `"${i.nameAr}"`,
      `"${i.generic}"`,
      i.batchNumber,
      i.expiryDate,
      `"${i.warehouseAr}"`,
      i.quantityOnHand,
      i.unitCost.toFixed(2),
      i.status === "available" ? "متوفر" : i.status === "near_expiry" ? "يقترب من الانتهاء" : "مخزون منخفض",
    ]);

    const csvContent = "\uFEFF" + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `Inventory_Stock_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast(locale === "ar" ? "تم تصدير كشف المخزون بصيغة CSV بنجاح" : "Inventory CSV exported successfully");
  };

  const filtered = inventory.filter((item) => {
    const matchesSearch =
      item.name.toLowerCase().includes(search.toLowerCase()) ||
      item.nameAr.includes(search) ||
      item.code.toLowerCase().includes(search.toLowerCase()) ||
      item.batchNumber.toLowerCase().includes(search.toLowerCase());

    if (!matchesSearch) return false;
    if (statusFilter === "all") return true;
    return item.status === statusFilter;
  });

  const totalStockUnits = inventory.reduce((acc, i) => acc + i.quantityOnHand, 0);
  const totalValuation = inventory.reduce((acc, i) => acc + i.quantityOnHand * i.unitCost, 0);
  const nearExpiryCount = inventory.filter((i) => i.status === "near_expiry").length;
  const lowStockCount = inventory.filter((i) => i.status === "low_stock").length;

  return (
    <div className="space-y-4 font-sans antialiased text-foreground">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-4 end-4 z-50 bg-emerald-600 text-white px-4 py-2.5 rounded-xl shadow-2xl text-xs font-bold flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
          <CheckCircle2 className="h-4 w-4" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Inventory Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-blue-500/10 text-blue-600 shrink-0">
            <Package className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-foreground">{t("inv.title")}</h1>
            <p className="text-[11px] text-muted-foreground">{locale === "ar" ? "أرصدة الأدوية، التشغيلات وتواريخ الصلاحية وسندات الاستلام (FEFO)" : "Stock batches, warehouse locations & expiry tracking"}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleExportCSV} className="gap-1.5 text-xs font-semibold h-8 border-border">
            <Download className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "تصدير كشف المخزون (CSV)" : "Export CSV"}</span>
          </Button>

          <Button size="sm" onClick={() => setIsGrnModalOpen(true)} className="gap-1.5 text-xs bg-blue-600 hover:bg-blue-700 font-bold h-8 shadow-sm text-white">
            <Plus className="h-3.5 w-3.5" />
            <span>{t("inv.receive_grn")}</span>
          </Button>
        </div>
      </div>

      {/* Operational KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "تقييم المخزون" : "Valuation"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-foreground">{formatCurrency(totalValuation)}</p>
          <p className="text-[10px] text-muted-foreground mt-1">{totalStockUnits.toLocaleString()} {locale === "ar" ? "وحدة دواء متوفرة" : "units on-hand"}</p>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "يقترب من الانتهاء (30 يوم)" : "Near Expiry"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-amber-600">{nearExpiryCount}</p>
          <div className="flex items-center gap-1 mt-1 text-[10px] text-amber-600 font-semibold">
            <Clock className="h-3 w-3" />
            <span>{locale === "ar" ? "أولوية الصرف مفعلة" : "FEFO Active"}</span>
          </div>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "أصناف دون حد الطلب" : "Low Stock"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-destructive">{lowStockCount}</p>
          <p className="text-[10px] text-destructive mt-1 font-medium">{locale === "ar" ? "بحاجة لطلب شراء" : "Reorder Needed"}</p>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card shadow-sm">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "سندات الاستلام (GRN)" : "GRN Receipts"}</span>
          <p className="text-xl font-extrabold mt-1 font-mono text-blue-600">{grns.length}</p>
          <p className="text-[10px] text-muted-foreground mt-1">{locale === "ar" ? "سلسلة التبريد مفحوصة" : "Cold-Chain Check"}</p>
        </Card>
      </div>

      {/* Navigation Sub-Tabs & Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 p-1 bg-muted/40 rounded-xl border text-xs w-fit">
          <Button variant={activeTab === "stock" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("stock")} className="h-7 text-xs font-semibold">
            {locale === "ar" ? "أرصدة الأدوية والتشغيلات" : "Stock Batches"}
          </Button>
          <Button variant={activeTab === "transfers" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("transfers")} className="h-7 text-xs font-semibold">
            {locale === "ar" ? "التحويلات بين الفروع" : "Transfers"}
          </Button>
          <Button variant={activeTab === "receiving" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("receiving")} className="h-7 text-xs font-semibold">
            {locale === "ar" ? "سندات الاستلام (GRN)" : "GRN Receipts"}
          </Button>
          <Button variant={activeTab === "counts" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("counts")} className="h-7 text-xs font-semibold">
            {locale === "ar" ? "الجرد الدوري" : "Stock Counts"}
          </Button>
        </div>

        {activeTab === "stock" && (
          <div className="flex items-center gap-2">
            <div className="flex items-center bg-muted/40 p-0.5 rounded-lg border text-xs">
              <Button
                variant={statusFilter === "all" ? "default" : "ghost"}
                size="sm"
                onClick={() => setStatusFilter("all")}
                className="h-6.5 text-[11px] px-2 font-medium"
              >
                الكل
              </Button>
              <Button
                variant={statusFilter === "available" ? "default" : "ghost"}
                size="sm"
                onClick={() => setStatusFilter("available")}
                className="h-6.5 text-[11px] px-2 font-medium text-emerald-600"
              >
                متوفر
              </Button>
              <Button
                variant={statusFilter === "near_expiry" ? "default" : "ghost"}
                size="sm"
                onClick={() => setStatusFilter("near_expiry")}
                className="h-6.5 text-[11px] px-2 font-medium text-amber-600"
              >
                يقترب من الانتهاء
              </Button>
              <Button
                variant={statusFilter === "low_stock" ? "default" : "ghost"}
                size="sm"
                onClick={() => setStatusFilter("low_stock")}
                className="h-6.5 text-[11px] px-2 font-medium text-destructive"
              >
                منخفض
              </Button>
            </div>

            <div className="relative w-56 md:w-64">
              <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-muted-foreground rtl:left-auto rtl:right-2.5 pointer-events-none" />
              <Input
                placeholder={t("inv.search_placeholder")}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8 text-xs rtl:pl-2.5 rtl:pr-8 h-7.5"
              />
            </div>
          </div>
        )}
      </div>

      {/* Tab: Stock & Batches */}
      {activeTab === "stock" && (
        <Card className="rounded-xl border bg-card overflow-hidden shadow-sm">
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-right">
                <thead className="bg-muted/30 font-semibold text-muted-foreground border-b text-[11px]">
                  <tr>
                    <th className="p-2.5">الدواء / المادة الفعالة</th>
                    <th className="p-2.5">رقم التشغيلة (Batch)</th>
                    <th className="p-2.5">تاريخ الصلاحية</th>
                    <th className="p-2.5">المستودع / الرف</th>
                    <th className="p-2.5 text-center">الرصيد الفعلي</th>
                    <th className="p-2.5 text-left">تكلفة الوحدة</th>
                    <th className="p-2.5 text-center">حالة المخزون</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {filtered.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="p-8 text-center text-muted-foreground text-xs">
                        {locale === "ar" ? "لا توجد أدوية مطابقة لبحثك." : "No matching items."}
                      </td>
                    </tr>
                  ) : (
                    filtered.map((item) => (
                      <tr key={item.id} className="hover:bg-muted/40 transition-colors">
                        <td className="p-2.5">
                          <div className="font-bold text-foreground">{item.nameAr}</div>
                          <div className="text-[10px] text-muted-foreground font-mono">{item.code} • {item.generic}</div>
                        </td>
                        <td className="p-2.5 font-mono text-[11px] font-semibold text-foreground">{item.batchNumber}</td>
                        <td className="p-2.5 font-mono text-[11px] text-muted-foreground">{item.expiryDate}</td>
                        <td className="p-2.5 text-muted-foreground text-[11px]">{item.warehouseAr}</td>
                        <td className="p-2.5 text-center font-bold text-foreground font-mono text-sm">{item.quantityOnHand}</td>
                        <td className="p-2.5 text-left font-mono text-muted-foreground font-semibold">{formatCurrency(item.unitCost)}</td>
                        <td className="p-2.5 text-center">
                          <Badge
                            variant={
                              item.status === "available"
                                ? "success"
                                : item.status === "near_expiry"
                                ? "warning"
                                : "destructive"
                            }
                            className="text-[10px] px-2 py-0.5 font-semibold"
                          >
                            {t(`status.${item.status}`)}
                          </Badge>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab: Transfers */}
      {activeTab === "transfers" && (
        <Card className="rounded-xl border bg-card overflow-hidden shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between p-3 border-b bg-muted/20">
            <CardTitle className="text-xs font-bold">{locale === "ar" ? "حركات النقل والتحويل بين الفروع" : "Branch Transfers"}</CardTitle>
            <Button size="sm" onClick={() => setIsTransferModalOpen(true)} className="gap-1 text-xs bg-blue-600 hover:bg-blue-700 font-bold h-7.5 text-white">
              <Plus className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "إنشاء طلب تحويل" : "New Transfer"}</span>
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-right">
                <thead className="bg-muted/30 font-semibold text-muted-foreground border-b text-[11px]">
                  <tr>
                    <th className="p-2.5">رقم السند</th>
                    <th className="p-2.5">المستودع المصدر</th>
                    <th className="p-2.5">الفرع المستلم</th>
                    <th className="p-2.5">الأصناف المنقولة</th>
                    <th className="p-2.5">التاريخ</th>
                    <th className="p-2.5 text-center">الحالة</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {transfers.map((trf) => (
                    <tr key={trf.id} className="hover:bg-muted/40 transition-colors">
                      <td className="p-2.5 font-mono font-bold text-primary">{trf.transferNo}</td>
                      <td className="p-2.5 font-medium text-foreground">{trf.from}</td>
                      <td className="p-2.5 text-foreground">{trf.to}</td>
                      <td className="p-2.5 font-mono text-[11px]">{trf.itemsCount}</td>
                      <td className="p-2.5 font-mono text-muted-foreground text-[11px]">{trf.date}</td>
                      <td className="p-2.5 text-center">
                        <Badge variant={trf.status === "completed" ? "success" : "default"} className="text-[10px] px-2 py-0.5">
                          {trf.status === "completed" ? "تم الاستلام" : "قيد النقل والشحن"}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab: Receiving (GRN) */}
      {activeTab === "receiving" && (
        <Card className="rounded-xl border bg-card overflow-hidden shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between p-3 border-b bg-muted/20">
            <CardTitle className="text-xs font-bold">{locale === "ar" ? "سندات استلام الموردين الرسمية (GRN)" : "Goods Receipt Notes"}</CardTitle>
            <Button size="sm" onClick={() => setIsGrnModalOpen(true)} className="gap-1 text-xs bg-blue-600 hover:bg-blue-700 font-bold h-7.5 text-white">
              <Plus className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "استلام شحنة جديدة" : "Receive GRN"}</span>
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-right">
                <thead className="bg-muted/30 font-semibold text-muted-foreground border-b text-[11px]">
                  <tr>
                    <th className="p-2.5">رقم GRN</th>
                    <th className="p-2.5">المورد الدوائي</th>
                    <th className="p-2.5">رقم أمر الشراء (PO)</th>
                    <th className="p-2.5">التاريخ</th>
                    <th className="p-2.5 text-left">القيمة الإجمالية</th>
                    <th className="p-2.5 text-center">الحالة</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {grns.map((grn) => (
                    <tr key={grn.id} className="hover:bg-muted/40 transition-colors">
                      <td className="p-2.5 font-mono font-bold text-primary">{grn.grnNo}</td>
                      <td className="p-2.5 font-medium text-foreground">{grn.supplier}</td>
                      <td className="p-2.5 font-mono text-[11px] text-muted-foreground">{grn.poNo}</td>
                      <td className="p-2.5 font-mono text-muted-foreground text-[11px]">{grn.date}</td>
                      <td className="p-2.5 text-left font-mono font-bold text-emerald-600">{formatCurrency(grn.amount)}</td>
                      <td className="p-2.5 text-center">
                        <Badge variant="success" className="text-[10px] px-2 py-0.5">
                          {locale === "ar" ? "مطابق ومخزن بالرف" : "Verified & Stocked"}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab: Counts (Stock Audit) */}
      {activeTab === "counts" && (
        <Card className="rounded-xl border bg-card overflow-hidden shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between p-3 border-b bg-muted/20">
            <div>
              <CardTitle className="text-xs font-bold text-foreground">{locale === "ar" ? "جلسة الجرد الدوري الفعلي للمخزون" : "Periodic Physical Stock Count"}</CardTitle>
              <p className="text-[10px] text-muted-foreground">{locale === "ar" ? "أدخل الكميات المعدودة على الأرفف لتسوية أي فروقات مخزنية" : "Enter shelf counts to reconcile any variances"}</p>
            </div>
            <Button size="sm" onClick={handleConfirmStockCount} className="gap-1 text-xs bg-emerald-600 hover:bg-emerald-700 font-bold h-7.5 text-white">
              <Check className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "اعتماد وترحيل نتائج الجرد" : "Reconcile Ledger"}</span>
            </Button>
          </CardHeader>

          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-right">
                <thead className="bg-muted/30 font-semibold text-muted-foreground border-b text-[11px]">
                  <tr>
                    <th className="p-2.5">رمز الصنف</th>
                    <th className="p-2.5">اسم الدواء</th>
                    <th className="p-2.5">رقم التشغيلة</th>
                    <th className="p-2.5 text-center">الرصيد الدفتري (النظام)</th>
                    <th className="p-2.5 text-center w-36">العدد الفعلي على الرف</th>
                    <th className="p-2.5 text-center">الفارق المخزني</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {inventory.map((item) => {
                    const counted = stockCounts[item.id] !== undefined ? stockCounts[item.id] : item.quantityOnHand;
                    const variance = counted - item.quantityOnHand;
                    return (
                      <tr key={item.id} className="hover:bg-muted/40 transition-colors">
                        <td className="p-2.5 font-mono text-[11px] text-muted-foreground">{item.code}</td>
                        <td className="p-2.5 font-bold text-foreground">{item.nameAr}</td>
                        <td className="p-2.5 font-mono text-[11px]">{item.batchNumber}</td>
                        <td className="p-2.5 text-center font-mono font-bold text-sm">{item.quantityOnHand}</td>
                        <td className="p-2.5 text-center">
                          <Input
                            type="text"
                            inputMode="numeric"
                            value={counted}
                            onChange={(e) => {
                              const val = parseInt(e.target.value) || 0;
                              setStockCounts({ ...stockCounts, [item.id]: val });
                            }}
                            className="w-24 h-7 text-xs font-mono text-center mx-auto font-bold"
                          />
                        </td>
                        <td className="p-2.5 text-center font-mono font-bold">
                          {variance === 0 ? (
                            <Badge variant="success" className="text-[10px] px-2 py-0.5">مطابق (0)</Badge>
                          ) : (
                            <Badge variant="destructive" className="text-[10px] px-2 py-0.5">
                              {variance > 0 ? `+${variance}` : variance}
                            </Badge>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Clean, Modern & Well-Paced Modal: Goods Receipt Note (GRN) */}
      {isGrnModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="max-w-lg w-full bg-card rounded-2xl border border-border shadow-2xl p-6 space-y-5 animate-in fade-in zoom-in duration-200">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-blue-500/10 text-blue-600">
                  <Boxes className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-foreground">
                    {locale === "ar" ? "سند استلام بضاعة جديدة (GRN)" : "Goods Receipt Note (GRN)"}
                  </h3>
                  <p className="text-[11px] text-muted-foreground">
                    {locale === "ar" ? "استلام شحنة أدوية وتغذية الأرصدة والتشغيلات" : "Receive drug shipments and update warehouse batches"}
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsGrnModalOpen(false)} className="h-8 w-8 text-muted-foreground hover:text-foreground">
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Form */}
            <form onSubmit={handleCreateGrn} className="space-y-4 text-xs">
              {/* Supplier */}
              <div className="space-y-1.5">
                <label className="font-semibold text-foreground block text-right">المورد الدوائي</label>
                <select
                  value={newGrnSupplier}
                  onChange={(e) => setNewGrnSupplier(e.target.value)}
                  className="w-full h-9 rounded-lg border border-input bg-background px-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  <option value="شركة الدواء المحدودة">شركة الدواء المحدودة</option>
                  <option value="سقالة للأدوية والتوزيع">سقالة للأدوية والتوزيع</option>
                  <option value="الشركة الخليجية للرعاية الصيدلانية">الشركة الخليجية للرعاية الصيدلانية</option>
                </select>
              </div>

              {/* Drug Name */}
              <div className="space-y-1.5">
                <label className="font-semibold text-foreground block text-right">اسم الصنف / الدواء</label>
                <Input
                  value={newGrnMedicine}
                  onChange={(e) => setNewGrnMedicine(e.target.value)}
                  placeholder="مثال: ليفوفلوكساسين 500 ملجم"
                  className="h-9 text-xs"
                  required
                  autoFocus
                />
              </div>

              {/* Batch & Expiry (2 Columns) */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground block text-right">رقم التشغيلة (Batch #)</label>
                  <Input
                    value={newGrnBatch}
                    onChange={(e) => setNewGrnBatch(e.target.value)}
                    className="h-9 font-mono text-xs font-bold"
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground block text-right">تاريخ الصلاحية (Expiry)</label>
                  <Input
                    type="date"
                    value={newGrnExpiry}
                    onChange={(e) => setNewGrnExpiry(e.target.value)}
                    className="h-9 font-mono text-xs"
                    required
                  />
                </div>
              </div>

              {/* Quantity & Unit Cost (2 Columns with clean text numbers) */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground block text-right">الكمية المستلمة (وحدات)</label>
                  <Input
                    type="text"
                    inputMode="numeric"
                    value={newGrnQty}
                    onChange={(e) => setNewGrnQty(parseInt(e.target.value) || 0)}
                    className="h-9 font-mono text-xs font-bold text-center"
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground block text-right">تكلفة الوحدة ($)</label>
                  <Input
                    type="text"
                    inputMode="decimal"
                    value={newGrnCost}
                    onChange={(e) => setNewGrnCost(parseFloat(e.target.value) || 0)}
                    className="h-9 font-mono text-xs font-bold text-center"
                    required
                  />
                </div>
              </div>

              {/* Total Calculation Card */}
              <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-900 dark:text-blue-200 text-xs flex items-center justify-between font-bold">
                <span>إجمالي قيمة سند الاستلام:</span>
                <span className="font-mono text-sm text-blue-600 dark:text-blue-400 font-extrabold">
                  {formatCurrency(newGrnQty * newGrnCost)}
                </span>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-2.5 pt-3 border-t">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsGrnModalOpen(false)} className="text-xs h-9 px-4">
                  {locale === "ar" ? "إلغاء" : "Cancel"}
                </Button>
                <Button type="submit" size="sm" className="text-xs font-bold bg-blue-600 hover:bg-blue-700 h-9 px-5 text-white shadow-sm">
                  {locale === "ar" ? "حفظ واستلام المخزون" : "Receive & Stock"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: New Stock Transfer */}
      {isTransferModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-card rounded-2xl border border-border shadow-2xl p-6 space-y-4 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <ArrowRightLeft className="h-5 w-5 text-blue-600" />
                <h3 className="font-bold text-sm text-foreground">
                  {locale === "ar" ? "إنشاء طلب تحويل بين الفروع" : "New Branch Transfer"}
                </h3>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsTransferModalOpen(false)} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <form onSubmit={handleCreateTransfer} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground block text-right">من (المستودع المصدر)</label>
                  <Input value={transferFrom} onChange={(e) => setTransferFrom(e.target.value)} className="h-9 text-xs" />
                </div>
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground block text-right">إلى (الفرع المستلم)</label>
                  <Input value={transferTo} onChange={(e) => setTransferTo(e.target.value)} className="h-9 text-xs" />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="font-semibold text-foreground block text-right">بيان الأصناف والكميات</label>
                <Input
                  value={transferItemsCount}
                  onChange={(e) => setTransferItemsCount(e.target.value)}
                  placeholder="مثال: 5 كراتين بنادول + 2 أوجمنتين"
                  className="h-9 text-xs"
                  required
                />
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-3 border-t">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsTransferModalOpen(false)} className="text-xs h-9 px-4">
                  {locale === "ar" ? "إلغاء" : "Cancel"}
                </Button>
                <Button type="submit" size="sm" className="text-xs font-bold bg-blue-600 hover:bg-blue-700 h-9 px-5 text-white">
                  {locale === "ar" ? "إرسال أمر التحويل" : "Send Transfer"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
