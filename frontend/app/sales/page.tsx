"use client";

import React, { useState } from "react";
import { FileText, Search, Plus, Filter, Download } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";

export default function SalesPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Sales & Customer Invoices</h1>
          <p className="text-sm text-muted-foreground">Multi-channel sales records, customer credit invoices, and returns.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="gap-2">
            <Download className="h-4 w-4" /> Export CSV
          </Button>
          <Button className="gap-2">
            <Plus className="h-4 w-4" /> New Credit Invoice
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between border-b">
          <div className="relative w-72">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search invoice #, customer..." className="pl-9 text-xs" />
          </div>
          <Button variant="outline" size="sm" className="gap-2 text-xs">
            <Filter className="h-3 w-3" /> Filter Status
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-xs text-left">
            <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
              <tr>
                <th className="p-3">Invoice Number</th>
                <th className="p-3">Customer</th>
                <th className="p-3">Date</th>
                <th className="p-3">Payment Method</th>
                <th className="p-3 text-right">Net Amount</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary">INV-2026-0091</td>
                <td className="p-3">Sarah Al-Mansoor (Walk-in)</td>
                <td className="p-3">2026-08-15 04:12</td>
                <td className="p-3">Cash</td>
                <td className="p-3 text-right font-bold">$45.00</td>
                <td className="p-3"><Badge variant="success">Completed</Badge></td>
              </tr>
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary">INV-2026-0090</td>
                <td className="p-3">Al-Amal Clinic (B2B Credit)</td>
                <td className="p-3">2026-08-15 03:30</td>
                <td className="p-3">Account Credit</td>
                <td className="p-3 text-right font-bold">$1,200.00</td>
                <td className="p-3"><Badge variant="default">Posted</Badge></td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
