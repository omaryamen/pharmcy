"use client";

import React from "react";
import { CreditCard, Check, ShieldCheck, Download } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function BillingPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">SaaS Subscription & Licensing</h1>
        <p className="text-sm text-muted-foreground">Manage your plan entitlements, active licenses, and billing invoices.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 md:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Current Plan</span>
              <h3 className="text-xl font-bold text-foreground mt-0.5">Enterprise Pharmacy Suite</h3>
            </div>
            <Badge variant="success">Active</Badge>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-4 border-y text-xs">
            <div>
              <span className="text-muted-foreground">Monthly Fee</span>
              <p className="font-bold text-foreground mt-0.5">$299.00 / mo</p>
            </div>
            <div>
              <span className="text-muted-foreground">Branches Allowed</span>
              <p className="font-bold text-foreground mt-0.5">5 / 10 Branches</p>
            </div>
            <div>
              <span className="text-muted-foreground">Users Allowed</span>
              <p className="font-bold text-foreground mt-0.5">18 / 25 Users</p>
            </div>
            <div>
              <span className="text-muted-foreground">Renewal Date</span>
              <p className="font-bold text-foreground mt-0.5">Sep 15, 2026</p>
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <Button variant="outline">Change Plan</Button>
            <Button>Manage Add-Ons</Button>
          </div>
        </Card>

        <Card className="p-6 space-y-4">
          <h3 className="font-semibold text-sm">Included Entitlements</h3>
          <ul className="space-y-2 text-xs text-muted-foreground">
            <li className="flex items-center gap-2 text-foreground font-medium">
              <Check className="h-4 w-4 text-emerald-500" /> Multi-Branch POS & Cash Registers
            </li>
            <li className="flex items-center gap-2 text-foreground font-medium">
              <Check className="h-4 w-4 text-emerald-500" /> Double-Entry General Ledger
            </li>
            <li className="flex items-center gap-2 text-foreground font-medium">
              <Check className="h-4 w-4 text-emerald-500" /> E-Commerce Digital Storefront
            </li>
            <li className="flex items-center gap-2 text-foreground font-medium">
              <Check className="h-4 w-4 text-emerald-500" /> Mobile Applications & Push Sync
            </li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
