"use client";

import React, { useState } from "react";
import { Search, Plus, Layers, RefreshCw } from "lucide-react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";
import { useI18n } from "@/lib/i18n";

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

const mockInventory: InventoryRow[] = [
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
];

export default function InventoryPage() {
  const { t, locale } = useI18n();
  const [search, setSearch] = useState("");

  const filtered = mockInventory.filter(
    (item) =>
      item.name.toLowerCase().includes(search.toLowerCase()) ||
      item.nameAr.includes(search) ||
      item.code.toLowerCase().includes(search.toLowerCase()) ||
      item.batchNumber.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t("inv.title")}</h1>
          <p className="text-sm text-muted-foreground">{t("inv.subtitle")}</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="gap-2">
            <Layers className="h-4 w-4" /> {t("inv.start_count")}
          </Button>
          <Button className="gap-2">
            <Plus className="h-4 w-4" /> {t("inv.receive_grn")}
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b">
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-3" />
            <Input
              placeholder={t("inv.search_placeholder")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 text-xs rtl:pl-3 rtl:pr-9"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="text-xs gap-1">
              <RefreshCw className="h-3 w-3" /> {locale === "ar" ? "تحديث" : "Refresh"}
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left rtl:text-right">
              <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
                <tr>
                  <th className="p-3">{t("inv.col_medicine")}</th>
                  <th className="p-3">{t("inv.col_batch")}</th>
                  <th className="p-3">{t("inv.col_expiry")}</th>
                  <th className="p-3">{t("inv.col_warehouse")}</th>
                  <th className="p-3 text-right rtl:text-left">{t("inv.col_on_hand")}</th>
                  <th className="p-3 text-right rtl:text-left">{t("inv.col_cost")}</th>
                  <th className="p-3">{t("inv.col_status")}</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filtered.map((item) => (
                  <tr key={item.id} className="hover:bg-muted/50">
                    <td className="p-3">
                      <div className="font-semibold text-foreground">{locale === "ar" ? item.nameAr : item.name}</div>
                      <div className="text-[10px] text-muted-foreground font-mono">{item.code} • {item.generic}</div>
                    </td>
                    <td className="p-3 font-mono">{item.batchNumber}</td>
                    <td className="p-3 font-mono">{item.expiryDate}</td>
                    <td className="p-3 text-muted-foreground">{locale === "ar" ? item.warehouseAr : item.warehouse}</td>
                    <td className="p-3 text-right rtl:text-left font-bold text-foreground font-mono">{item.quantityOnHand}</td>
                    <td className="p-3 text-right rtl:text-left font-mono">{formatCurrency(item.unitCost)}</td>
                    <td className="p-3">
                      <Badge
                        variant={
                          item.status === "available"
                            ? "success"
                            : item.status === "near_expiry"
                            ? "warning"
                            : "destructive"
                        }
                      >
                        {t(`status.${item.status}`)}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
