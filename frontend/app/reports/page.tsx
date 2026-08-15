"use client";

import React from "react";
import { TrendingUp, Download, Calendar, Filter, BarChart3, PieChart } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Reporting & Business Intelligence</h1>
          <p className="text-sm text-muted-foreground">Executive dashboards, product movement velocity, and financial health statements.</p>
        </div>
        <Button variant="outline" className="gap-2">
          <Download className="h-4 w-4" /> Download PDF Report
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-sm">Monthly Sales Trend (by Channel)</h3>
            <BarChart3 className="h-4 w-4 text-primary" />
          </div>
          <div className="h-48 rounded-lg bg-muted/30 border flex items-center justify-center text-xs text-muted-foreground">
            [Interactive Sales BI Bar Chart — POS vs Online Store vs B2B Wholesale]
          </div>
        </Card>

        <Card className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-sm">Top Selling Pharmaceutical Categories</h3>
            <PieChart className="h-4 w-4 text-primary" />
          </div>
          <div className="h-48 rounded-lg bg-muted/30 border flex items-center justify-center text-xs text-muted-foreground">
            [Category Revenue Breakdown — Antibiotics (35%), Analgesics (28%), Chronic (22%), OTC (15%)]
          </div>
        </Card>
      </div>
    </div>
  );
}
