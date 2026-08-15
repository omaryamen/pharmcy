"use client";

import React from "react";
import { Plus, Search, DollarSign } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

export default function PurchasingPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Purchasing & Supplier Invoices</h1>
          <p className="text-sm text-muted-foreground">Purchase orders, 3-way matching, goods receipts, and Accounts Payable.</p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" /> Create Purchase Order
        </Button>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between border-b">
          <div className="relative w-72">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search PO #, supplier..." className="pl-9 text-xs" />
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-xs text-left">
            <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
              <tr>
                <th className="p-3">PO Number</th>
                <th className="p-3">Supplier</th>
                <th className="p-3">Order Date</th>
                <th className="p-3 text-right">Total Amount</th>
                <th className="p-3">Status</th>
                <th className="p-3">3-Way Match</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary">PO-2026-0041</td>
                <td className="p-3">Novartis Pharma Distribution</td>
                <td className="p-3">2026-08-14</td>
                <td className="p-3 text-right font-bold">$14,500.00</td>
                <td className="p-3"><Badge variant="success">Received</Badge></td>
                <td className="p-3"><Badge variant="default">Matched</Badge></td>
              </tr>
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary">PO-2026-0042</td>
                <td className="p-3">Pfizer Global Supply</td>
                <td className="p-3">2026-08-15</td>
                <td className="p-3 text-right font-bold">$8,200.00</td>
                <td className="p-3"><Badge variant="warning">Pending GRN</Badge></td>
                <td className="p-3"><Badge variant="outline">Pending</Badge></td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
