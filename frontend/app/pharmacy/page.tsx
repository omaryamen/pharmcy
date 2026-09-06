"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Pill,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  Search,
  Clock,
  User,
  Stethoscope,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useI18n } from "@/lib/i18n";

export default function PharmacistWorkspacePage() {
  const { t, locale } = useI18n();
  const [searchQuery, setSearchQuery] = useState("");

  const pendingPrescriptions = [
    {
      id: "rx-101",
      orderNo: "ORD-2026-9901",
      patient: locale === "ar" ? "ياسمين النور (34 سنة)" : "Yasmin Al-Noor (34 yrs)",
      doctor: locale === "ar" ? "د. خالد نادر (MD-8841)" : "Dr. Khaled Nader (MD-8841)",
      medication: "Amoxicillin 500mg",
      dosage: "1 Cap 3x Daily for 7 Days",
      isControlled: false,
      time: "10 mins ago",
    },
    {
      id: "rx-102",
      orderNo: "ORD-2026-9884",
      patient: locale === "ar" ? "سلطان العتيبي (48 سنة)" : "Sultan Al-Otaibi (48 yrs)",
      doctor: locale === "ar" ? "د. فاطمة الزهراء (استشارية الأعصاب)" : "Dr. Fatima Zahra (Neurology)",
      medication: "Pregabalin 75mg",
      dosage: "1 Cap Twice Daily",
      isControlled: true,
      time: "25 mins ago",
    },
    {
      id: "rx-103",
      orderNo: "ORD-2026-9762",
      patient: locale === "ar" ? "منى سالم (62 سنة)" : "Mona Salem (62 yrs)",
      doctor: locale === "ar" ? "د. طارق حمد (استشاري القلب)" : "Dr. Tariq Hamad (Cardiology)",
      medication: "Atorvastatin 20mg",
      dosage: "1 Tab Daily at Bedtime",
      isControlled: false,
      time: "1 hour ago",
    },
  ];

  return (
    <div className="space-y-4 font-sans">
      {/* Workspace Header */}
      <div className="flex items-center justify-between pb-2 border-b">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-600">
            <Stethoscope className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground">
              {locale === "ar" ? "محطة الصيدلي الإكلينيكي" : "Clinical Pharmacist Station"}
            </h1>
            <p className="text-[11px] text-muted-foreground">
              {locale === "ar" ? "التدقيق السريري، اعتماد الوصفات، وصرف الأدوية المراقبة" : "Clinical verification, Rx approval, and controlled drug safety"}
            </p>
          </div>
        </div>

        <Link href="/prescriptions">
          <Button size="sm" className="gap-1 text-xs bg-emerald-600 hover:bg-emerald-700 font-bold h-8">
            <Pill className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "طابور الوصفات" : "Rx Queue"}</span>
          </Button>
        </Link>
      </div>

      {/* Clinical KPI Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Card className="p-3.5 rounded-xl border bg-card">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "الوصفات قيد التدقيق" : "Pending Reviews"}</span>
          <p className="text-xl font-extrabold mt-1 text-amber-600 font-mono">3</p>
          <div className="flex items-center gap-1 mt-1 text-[10px] text-destructive font-semibold">
            <ShieldAlert className="h-3 w-3" />
            <span>1 {locale === "ar" ? "دواء مراقب" : "Controlled"}</span>
          </div>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "تم صرفها اليوم" : "Dispensed Today"}</span>
          <p className="text-xl font-extrabold mt-1 text-emerald-600 font-mono">42</p>
          <p className="text-[10px] text-muted-foreground mt-1">{locale === "ar" ? "100% مطابقة لمعايير FEFO" : "100% FEFO Compliant"}</p>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "تعارضات دوائية حرجة" : "Drug Conflicts"}</span>
          <p className="text-xl font-extrabold mt-1 text-purple-600 font-mono">0</p>
          <p className="text-[10px] text-emerald-600 mt-1 font-medium">{locale === "ar" ? "سليم وآمن" : "Safe"}</p>
        </Card>

        <Card className="p-3.5 rounded-xl border bg-card">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "تشغيلات تقترب من الانتهاء" : "Near Expiry Batches"}</span>
          <p className="text-xl font-extrabold mt-1 text-amber-600 font-mono">5</p>
          <p className="text-[10px] text-muted-foreground mt-1">{locale === "ar" ? "أولوية الصرف مفعلة" : "FEFO Active"}</p>
        </Card>
      </div>

      {/* Main Verification Queue Feed */}
      <Card className="rounded-xl border bg-card overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between p-3.5 border-b bg-muted/20">
          <CardTitle className="text-xs font-bold text-foreground">
            {locale === "ar" ? "الوصفات بانتظار الاعتماد السريري" : "Prescriptions Awaiting Review"}
          </CardTitle>
          <div className="relative w-48 sm:w-64">
            <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-muted-foreground rtl:left-auto rtl:right-2.5 pointer-events-none" />
            <Input
              placeholder={locale === "ar" ? "بحث برقم الوصفة..." : "Search Rx #..."}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 text-xs rtl:pl-2.5 rtl:pr-8 h-7.5"
            />
          </div>
        </CardHeader>

        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left rtl:text-right">
              <thead className="bg-muted/30 font-medium text-muted-foreground border-b text-[11px]">
                <tr>
                  <th className="p-2.5">رقم الوصفة</th>
                  <th className="p-2.5">المريض</th>
                  <th className="p-2.5">الدواء والجرعة</th>
                  <th className="p-2.5">النوع</th>
                  <th className="p-2.5 text-right rtl:text-left">الإجراء</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {pendingPrescriptions.map((rx) => (
                  <tr key={rx.id} className="hover:bg-muted/40 transition-colors">
                    <td className="p-2.5 font-mono font-bold text-primary">{rx.orderNo}</td>
                    <td className="p-2.5 font-medium">{rx.patient}</td>
                    <td className="p-2.5">
                      <span className="font-semibold text-foreground">{rx.medication}</span>
                      <div className="text-[10px] text-muted-foreground">{rx.dosage}</div>
                    </td>
                    <td className="p-2.5">
                      {rx.isControlled ? (
                        <Badge variant="destructive" className="text-[9px] gap-1 px-1.5 py-0 font-medium">
                          <ShieldAlert className="h-3 w-3" /> {locale === "ar" ? "مراقب" : "Controlled"}
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-[9px] px-1.5 py-0">
                          {locale === "ar" ? "عادي" : "Standard"}
                        </Badge>
                      )}
                    </td>
                    <td className="p-2.5 text-right rtl:text-left">
                      <Link href="/prescriptions">
                        <Button size="sm" variant="outline" className="h-7 text-[11px] gap-1 font-semibold hover:bg-primary/5">
                          <span>{locale === "ar" ? "فحص واعتماد" : "Verify"}</span>
                          <ChevronRight className="h-3 w-3 rtl:rotate-180" />
                        </Button>
                      </Link>
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
