"use client";

import React from "react";
import Link from "next/link";
import {
  GitBranch,
  ShoppingCart,
  Pill,
  Package,
  FileText,
  DollarSign,
  TrendingUp,
  Users,
  Clock,
  CheckCircle2,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";

export default function BranchManagerPage() {
  const { t, locale } = useI18n();

  return (
    <div className="space-y-6 font-sans">
      {/* Header & Branch Manager Identity */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="default" className="bg-primary hover:bg-primary/90 text-[11px] gap-1 px-2.5 py-0.5">
              <GitBranch className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "لوحة مدير الفرع (Branch Manager)" : "Branch Manager Dashboard"}</span>
            </Badge>
            <Badge variant="outline" className="text-[10px] text-muted-foreground">
              {locale === "ar" ? "الفرع الرئيسي - الرياض (العليا)" : "Main Branch - Riyadh (Al-Olaya)"}
            </Badge>
          </div>
          <h1 className="text-2xl font-bold tracking-tight">
            {locale === "ar" ? "إشراف ومتابعة عمليات الفرع" : "Branch Operations & Supervision"}
          </h1>
          <p className="text-sm text-muted-foreground">
            {locale === "ar"
              ? "متابعة المبيعات المباشرة، ورديات الصناديق، حضور طاقم الصيادلة، ومخزون الرفوف بالفرع."
              : "Live branch sales, cash register sessions, pharmacy staff supervision, and on-shelf stock."}
          </p>
        </div>
      </div>

      {/* Branch KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">{locale === "ar" ? "مبيعات الفرع اليوم" : "Branch Sales Today"}</span>
          <p className="text-2xl font-bold mt-1 text-foreground font-mono">$4,850.50</p>
          <p className="text-[11px] text-emerald-600 mt-2 font-medium">+12.4% vs yesterday (142 sales)</p>
        </Card>

        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">{locale === "ar" ? "صناديق الكاشير النشطة" : "Active Cash Registers"}</span>
          <p className="text-2xl font-bold mt-1 text-emerald-600 font-mono">3 / 3</p>
          <div className="flex items-center gap-1.5 mt-2 text-[11px] text-muted-foreground">
            <Clock className="h-3.5 w-3.5 text-primary" />
            <span>{locale === "ar" ? "الورديات متزنة بالكامل" : "All register floats balanced"}</span>
          </div>
        </Card>

        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">{locale === "ar" ? "طاقم العمل المناوب" : "On-Duty Staff"}</span>
          <p className="text-2xl font-bold mt-1 text-purple-600 font-mono">4 {locale === "ar" ? "صيادلة وكاشير" : "Staff"}</p>
          <p className="text-[11px] text-muted-foreground mt-2">{locale === "ar" ? "الوردية الصباحية نشطة" : "Morning shift active"}</p>
        </Card>

        <Card className="p-4">
          <span className="text-xs text-muted-foreground font-medium">{locale === "ar" ? "طلبات تغذية المخزون" : "Restock Requests"}</span>
          <p className="text-2xl font-bold mt-1 text-amber-600 font-mono">2</p>
          <p className="text-[11px] text-muted-foreground mt-2">{locale === "ar" ? "من المستودع المركزي" : "From central warehouse"}</p>
        </Card>
      </div>

      {/* Quick Access Branch Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 space-y-2">
          <div className="flex items-center gap-2 font-bold text-xs">
            <ShoppingCart className="h-4 w-4 text-primary" />
            <span>{locale === "ar" ? "نقطة البيع والصرف" : "POS Station"}</span>
          </div>
          <p className="text-xs text-muted-foreground">{locale === "ar" ? "مباشرة أو الإشراف على عمليات الصرف السريع." : "Operate or supervise direct counter dispensing."}</p>
          <Link href="/pos" className="block pt-2">
            <Button size="sm" variant="outline" className="w-full text-xs">{locale === "ar" ? "فتح نقطة البيع" : "Open POS"}</Button>
          </Link>
        </Card>

        <Card className="p-4 space-y-2">
          <div className="flex items-center gap-2 font-bold text-xs">
            <Pill className="h-4 w-4 text-primary" />
            <span>{locale === "ar" ? "طابور الوصفات السريرية" : "Prescriptions Queue"}</span>
          </div>
          <p className="text-xs text-muted-foreground">{locale === "ar" ? "تدقيق واعتماد الوصفات الطبية الواردة." : "Review and approve incoming doctor prescriptions."}</p>
          <Link href="/prescriptions" className="block pt-2">
            <Button size="sm" variant="outline" className="w-full text-xs">{locale === "ar" ? "فتح الوصفات" : "Open Prescriptions"}</Button>
          </Link>
        </Card>

        <Card className="p-4 space-y-2">
          <div className="flex items-center gap-2 font-bold text-xs">
            <Package className="h-4 w-4 text-primary" />
            <span>{locale === "ar" ? "جرد ومخزون الفرع" : "Branch Stock"}</span>
          </div>
          <p className="text-xs text-muted-foreground">{locale === "ar" ? "متابعة أرصدة الأدوية بالرفوف وتواريخ الصلاحية." : "Inspect on-hand shelf balance and batch expiry."}</p>
          <Link href="/inventory" className="block pt-2">
            <Button size="sm" variant="outline" className="w-full text-xs">{locale === "ar" ? "فحص المخزون" : "Inspect Inventory"}</Button>
          </Link>
        </Card>
      </div>
    </div>
  );
}
