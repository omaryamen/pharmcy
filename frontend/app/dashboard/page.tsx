"use client";

import React from "react";
import Link from "next/link";
import {
  TrendingUp,
  Package,
  AlertTriangle,
  Pill,
  ShoppingCart,
  Users,
  Building2,
  ArrowUpRight,
  ShieldCheck,
  CreditCard,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Top Header & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Executive & Pharmacy Overview</h1>
          <p className="text-sm text-muted-foreground">Real-time enterprise metrics, clinical alerts, and live POS operations.</p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/pos">
            <Button className="gap-2">
              <ShoppingCart className="h-4 w-4" /> Open POS Terminal
            </Button>
          </Link>
          <Link href="/prescriptions">
            <Button variant="outline" className="gap-2">
              <Pill className="h-4 w-4" /> Review Prescriptions (4)
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Today's Sales (POS + Online)</CardTitle>
            <TrendingUp className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$12,450.80</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <span className="text-emerald-500 font-medium">+14.2%</span> vs yesterday (328 transactions)
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Pending Prescriptions</CardTitle>
            <Pill className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">7 Awaiting</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <Badge variant="warning" className="text-[10px] px-1 py-0">2 Controlled Rx</Badge> Requires Pharmacist Approval
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Inventory Stock On Hand</CardTitle>
            <Package className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">18,940 Units</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              Valuation: <span className="font-semibold text-foreground">$142,850.00</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Expiry & Low-Stock Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">12 Items</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <span className="text-destructive font-medium">5 batches</span> expiring within 30 days
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Grid: Live Orders / Clinical Queues */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Live Sales & Orders */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent POS & Online Sales</CardTitle>
              <CardDescription>Live real-time feed of multi-channel transactions.</CardDescription>
            </div>
            <Link href="/sales" className="text-xs text-primary hover:underline flex items-center gap-1">
              View All <ArrowUpRight className="h-3 w-3" />
            </Link>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="border-b bg-muted/40 font-medium text-muted-foreground">
                  <tr>
                    <th className="p-3">Invoice #</th>
                    <th className="p-3">Customer / Patient</th>
                    <th className="p-3">Branch</th>
                    <th className="p-3">Amount</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  <tr className="hover:bg-muted/50">
                    <td className="p-3 font-semibold text-primary">INV-2026-8891</td>
                    <td className="p-3">Sarah Al-Mansoor (Walk-in)</td>
                    <td className="p-3">Main Branch</td>
                    <td className="p-3 font-medium">$45.00</td>
                    <td className="p-3"><Badge variant="success">Completed</Badge></td>
                    <td className="p-3 text-muted-foreground">2 mins ago</td>
                  </tr>
                  <tr className="hover:bg-muted/50">
                    <td className="p-3 font-semibold text-primary">ORD-2026-4412</td>
                    <td className="p-3">Dr. Tarek Clinic (B2B)</td>
                    <td className="p-3">Central Warehouse</td>
                    <td className="p-3 font-medium">$1,250.00</td>
                    <td className="p-3"><Badge variant="default">Dispatched</Badge></td>
                    <td className="p-3 text-muted-foreground">15 mins ago</td>
                  </tr>
                  <tr className="hover:bg-muted/50">
                    <td className="p-3 font-semibold text-primary">INV-2026-8890</td>
                    <td className="p-3">Omar Khaled</td>
                    <td className="p-3">Main Branch</td>
                    <td className="p-3 font-medium">$18.50</td>
                    <td className="p-3"><Badge variant="success">Completed</Badge></td>
                    <td className="p-3 text-muted-foreground">30 mins ago</td>
                  </tr>
                  <tr className="hover:bg-muted/50">
                    <td className="p-3 font-semibold text-primary">INV-2026-8889</td>
                    <td className="p-3">Fahad Al-Harbi (Insured)</td>
                    <td className="p-3">West Branch</td>
                    <td className="p-3 font-medium">$84.00</td>
                    <td className="p-3"><Badge variant="success">Completed</Badge></td>
                    <td className="p-3 text-muted-foreground">42 mins ago</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Right Col: Quick Clinical & Operational Actions */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Clinical Verification Queue</CardTitle>
              <CardDescription>Prescriptions requiring pharmacist sign-off.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-3 rounded-lg border bg-muted/30 flex items-center justify-between">
                <div className="flex flex-col">
                  <span className="text-xs font-semibold">Rx #RX-2026-091 - Amoxicillin 500mg</span>
                  <span className="text-[10px] text-muted-foreground">Patient: Yasmin Noor | Dr. K. Nader</span>
                </div>
                <Badge variant="warning">Review</Badge>
              </div>

              <div className="p-3 rounded-lg border bg-muted/30 flex items-center justify-between">
                <div className="flex flex-col">
                  <span className="text-xs font-semibold">Rx #RX-2026-088 - Pregabalin 75mg</span>
                  <span className="text-[10px] text-destructive font-medium">⚠️ Controlled Drug (Schedule IV)</span>
                </div>
                <Badge variant="destructive">Critical</Badge>
              </div>

              <Link href="/prescriptions" className="block w-full">
                <Button variant="outline" className="w-full text-xs">Open Pharmacist Queue</Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>System & Multi-Tenant Status</CardTitle>
              <CardDescription>SaaS platform health and database synchronization.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-xs">
              <div className="flex items-center justify-between py-1 border-b">
                <span className="text-muted-foreground">Platform Engine</span>
                <span className="font-semibold text-emerald-600">v1.33.0 Enterprise</span>
              </div>
              <div className="flex items-center justify-between py-1 border-b">
                <span className="text-muted-foreground">Stock Engine</span>
                <span className="font-semibold text-emerald-600">Double-Entry FEFO Active</span>
              </div>
              <div className="flex items-center justify-between py-1">
                <span className="text-muted-foreground">GL Integration</span>
                <span className="font-semibold text-emerald-600">Auto-Journaling Synced</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
