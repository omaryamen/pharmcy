"use client";

import React from "react";
import { Store, Plus, Package, Truck, ExternalLink } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function EcommercePage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">E-Commerce & B2B Digital Marketplace</h1>
          <p className="text-sm text-muted-foreground">Tenant digital storefronts, online catalog publishing, and courier fulfillment.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="gap-2">
            <ExternalLink className="h-4 w-4" /> View Online Store
          </Button>
          <Button className="gap-2">
            <Plus className="h-4 w-4" /> Publish Product to Web
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="border-b">
          <CardTitle>Online Orders & Delivery Tracking</CardTitle>
          <CardDescription>Live B2C retail & B2B wholesale digital orders.</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-xs text-left">
            <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
              <tr>
                <th className="p-3">Order Number</th>
                <th className="p-3">Customer</th>
                <th className="p-3">Tracking #</th>
                <th className="p-3">Prescription Review</th>
                <th className="p-3 text-right">Total</th>
                <th className="p-3">Fulfillment Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary">ORD-2026-4412</td>
                <td className="p-3">Dr. Tarek Clinic (B2B)</td>
                <td className="p-3 font-mono">TRK-8899A</td>
                <td className="p-3"><Badge variant="outline">N/A (OTC)</Badge></td>
                <td className="p-3 text-right font-bold">$1,250.00</td>
                <td className="p-3"><Badge variant="default">Dispatched</Badge></td>
              </tr>
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold text-primary">ORD-2026-4410</td>
                <td className="p-3">Jane Retail</td>
                <td className="p-3 font-mono">TRK-2211B</td>
                <td className="p-3"><Badge variant="success">Approved</Badge></td>
                <td className="p-3 text-right font-bold">$25.00</td>
                <td className="p-3"><Badge variant="success">Delivered</Badge></td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
