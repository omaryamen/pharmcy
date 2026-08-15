"use client";

import React from "react";
import { TrendingUp, Plus, FileText, CheckCircle2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function AccountingPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">General Ledger & Financial Accounting</h1>
          <p className="text-sm text-muted-foreground">Double-entry journal posting, chart of accounts, trial balance, and P&L statements.</p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" /> New Journal Entry
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">Cash & Bank Accounts (1010/1020)</span>
          <p className="text-xl font-bold mt-1 text-foreground">$128,450.00</p>
        </Card>
        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">Accounts Receivable (1200)</span>
          <p className="text-xl font-bold mt-1 text-foreground">$34,200.00</p>
        </Card>
        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">Accounts Payable (2000)</span>
          <p className="text-xl font-bold mt-1 text-destructive">$18,900.00</p>
        </Card>
      </div>

      <Card>
        <CardHeader className="border-b">
          <CardTitle>Recent Posted Journal Entries</CardTitle>
          <CardDescription>Automated double-entry journals posted from POS, Purchasing, and SaaS billing.</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-xs text-left">
            <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
              <tr>
                <th className="p-3">Journal #</th>
                <th className="p-3">Description</th>
                <th className="p-3">Debit Account</th>
                <th className="p-3">Credit Account</th>
                <th className="p-3 text-right">Amount</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary">JRN-2026-0089</td>
                <td className="p-3">POS Cash Sales Daily Close (INV-8891)</td>
                <td className="p-3 font-mono">1010 - Cash on Hand</td>
                <td className="p-3 font-mono">4000 - Sales Revenue</td>
                <td className="p-3 text-right font-bold">$12,450.80</td>
                <td className="p-3"><Badge variant="success">Posted</Badge></td>
              </tr>
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary">JRN-2026-0088</td>
                <td className="p-3">Inventory Purchase Goods Receipt (GRN-041)</td>
                <td className="p-3 font-mono">1300 - Inventory Asset</td>
                <td className="p-3 font-mono">2000 - Accounts Payable</td>
                <td className="p-3 text-right font-bold">$14,500.00</td>
                <td className="p-3"><Badge variant="success">Posted</Badge></td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
