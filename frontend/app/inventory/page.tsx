"use client";

import React, { useState } from "react";
import { Package, Search, Plus, ArrowUpDown, AlertCircle, RefreshCw, Layers } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";

interface InventoryRow {
  id: string;
  code: string;
  name: string;
  generic: string;
  batchNumber: string;
  expiryDate: string;
  warehouse: string;
  quantityOnHand: number;
  unitCost: number;
  status: "available" | "near_expiry" | "low_stock";
}

const mockInventory: InventoryRow[] = [
  {
    id: "1",
    code: "MED-PAN-001",
    name: "Panadol Extra 500mg",
    generic: "Paracetamol",
    batchNumber: "BATCH-2026-A1",
    expiryDate: "2027-08-30",
    warehouse: "Main Warehouse (Shelf A1)",
    quantityOnHand: 450,
    unitCost: 2.8,
    status: "available",
  },
  {
    id: "2",
    code: "MED-AUG-002",
    name: "Augmentin 1g Tablets",
    generic: "Amoxicillin / Clavulanate",
    batchNumber: "BATCH-2025-C9",
    expiryDate: "2026-09-10",
    warehouse: "Main Warehouse (Cold Zone)",
    quantityOnHand: 8,
    unitCost: 12.5,
    status: "low_stock",
  },
  {
    id: "3",
    code: "MED-BRU-003",
    name: "Brufen 400mg",
    generic: "Ibuprofen",
    batchNumber: "BATCH-2026-D4",
    expiryDate: "2026-09-01",
    warehouse: "West Branch Storage",
    quantityOnHand: 220,
    unitCost: 3.9,
    status: "near_expiry",
  },
];

export default function InventoryPage() {
  const [search, setSearch] = useState("");

  const filtered = mockInventory.filter(
    (item) =>
      item.name.toLowerCase().includes(search.toLowerCase()) ||
      item.code.toLowerCase().includes(search.toLowerCase()) ||
      item.batchNumber.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Inventory & Stock Movement</h1>
          <p className="text-sm text-muted-foreground">Double-entry stock ledger, FEFO batch tracking, and warehouse positions.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="gap-2">
            <Layers className="h-4 w-4" /> Start Stock Count
          </Button>
          <Button className="gap-2">
            <Plus className="h-4 w-4" /> Receive Goods (GRN)
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b">
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by Medicine, SKU, Barcode, Batch..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 text-xs"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="text-xs gap-1">
              <RefreshCw className="h-3 w-3" /> Refresh
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
                <tr>
                  <th className="p-3">Medicine / SKU</th>
                  <th className="p-3">Batch #</th>
                  <th className="p-3">Expiry (FEFO)</th>
                  <th className="p-3">Warehouse / Shelf</th>
                  <th className="p-3 text-right">On Hand Qty</th>
                  <th className="p-3 text-right">Unit Cost</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filtered.map((item) => (
                  <tr key={item.id} className="hover:bg-muted/50">
                    <td className="p-3">
                      <div className="font-semibold text-foreground">{item.name}</div>
                      <div className="text-[10px] text-muted-foreground">{item.code} • {item.generic}</div>
                    </td>
                    <td className="p-3 font-mono">{item.batchNumber}</td>
                    <td className="p-3 font-medium">{item.expiryDate}</td>
                    <td className="p-3 text-muted-foreground">{item.warehouse}</td>
                    <td className="p-3 text-right font-bold text-foreground">{item.quantityOnHand}</td>
                    <td className="p-3 text-right">{formatCurrency(item.unitCost)}</td>
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
                        {item.status.replace("_", " ")}
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
