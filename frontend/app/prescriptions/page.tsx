"use client";

import React, { useState } from "react";
import { Pill, CheckCircle, XCircle, FileText, AlertTriangle, ShieldAlert } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";

interface RxItem {
  id: string;
  orderNumber: string;
  patientName: string;
  patientNameAr: string;
  prescriberName: string;
  prescriberNameAr: string;
  medication: string;
  medicationAr: string;
  dosage: string;
  dosageAr: string;
  status: "uploaded" | "approved" | "rejected";
  isControlled: boolean;
  fileUrl: string;
  date: string;
}

const mockPrescriptions: RxItem[] = [
  {
    id: "rx-1",
    orderNumber: "ORD-2026-9901",
    patientName: "Yasmin Al-Noor",
    patientNameAr: "ياسمين النور",
    prescriberName: "Dr. Khaled Nader (License #MD-8841)",
    prescriberNameAr: "د. خالد نادر (ترخيص #MD-8841)",
    medication: "Amoxicillin 500mg (20 Caps)",
    medicationAr: "أموكسيسيلين 500 ملجم (20 كبسولة)",
    dosage: "1 capsule 3 times daily for 7 days",
    dosageAr: "كبسولة واحدة 3 مرات يومياً لمدة 7 أيام",
    status: "uploaded",
    isControlled: false,
    fileUrl: "https://storage.pharmacloud/rx/sample1.pdf",
    date: "2026-08-15 04:10",
  },
  {
    id: "rx-2",
    orderNumber: "ORD-2026-9884",
    patientName: "Sultan Al-Otaibi",
    patientNameAr: "سلطان العتيبي",
    prescriberName: "Dr. Fatima Zahra (Consultant Neurologist)",
    prescriberNameAr: "د. فاطمة الزهراء (استشارية المخ والأعصاب)",
    medication: "Pregabalin 75mg (30 Caps)",
    medicationAr: "بريجابالين 75 ملجم (30 كبسولة)",
    dosage: "1 capsule twice daily",
    dosageAr: "كبسولة واحدة مرتين يومياً",
    status: "uploaded",
    isControlled: true,
    fileUrl: "https://storage.pharmacloud/rx/sample2.pdf",
    date: "2026-08-15 03:45",
  },
  {
    id: "rx-3",
    orderNumber: "ORD-2026-9762",
    patientName: "Mona Salem",
    patientNameAr: "منى سالم",
    prescriberName: "Dr. Tariq Hamad (Cardiology)",
    prescriberNameAr: "د. طارق حمد (استشاري القلب)",
    medication: "Atorvastatin 20mg (28 Tab)",
    medicationAr: "أتورفاستاتين 20 ملجم (28 قرص)",
    dosage: "1 tablet once daily at bedtime",
    dosageAr: "قرص واحد يومياً قبل النوم",
    status: "approved",
    isControlled: false,
    fileUrl: "https://storage.pharmacloud/rx/sample3.pdf",
    date: "2026-08-14 18:20",
  },
];

export default function PrescriptionsPage() {
  const { t, locale } = useI18n();
  const [prescriptions, setPrescriptions] = useState<RxItem[]>(mockPrescriptions);
  const [selectedRx, setSelectedRx] = useState<RxItem>(mockPrescriptions[0]);

  const handleApprove = (id: string) => {
    setPrescriptions((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: "approved" as const } : r))
    );
    setSelectedRx((prev) => (prev.id === id ? { ...prev, status: "approved" as const } : prev));
  };

  const handleReject = (id: string) => {
    setPrescriptions((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: "rejected" as const } : r))
    );
    setSelectedRx((prev) => (prev.id === id ? { ...prev, status: "rejected" as const } : prev));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{t("rx.title")}</h1>
        <p className="text-sm text-muted-foreground">{t("rx.subtitle")}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Prescription List */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-sm font-semibold">{t("rx.queue_title")} ({prescriptions.length})</CardTitle>
            <CardDescription>{t("rx.queue_desc")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 p-3">
            {prescriptions.map((rx) => (
              <div
                key={rx.id}
                onClick={() => setSelectedRx(rx)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  selectedRx.id === rx.id ? "border-primary bg-primary/5" : "hover:bg-muted/40"
                }`}
              >
                <div className="flex items-start justify-between">
                  <span className="text-xs font-bold text-foreground font-mono">{rx.orderNumber}</span>
                  <Badge
                    variant={
                      rx.status === "approved" ? "success" : rx.status === "rejected" ? "destructive" : "warning"
                    }
                  >
                    {t(`status.${rx.status}`)}
                  </Badge>
                </div>
                <p className="text-xs font-medium text-foreground mt-1">{locale === "ar" ? rx.patientNameAr : rx.patientName}</p>
                <p className="text-[11px] text-muted-foreground truncate">{locale === "ar" ? rx.medicationAr : rx.medication}</p>
                {rx.isControlled && (
                  <Badge variant="destructive" className="mt-2 text-[10px] px-1 py-0 gap-1">
                    <ShieldAlert className="h-3 w-3" /> {locale === "ar" ? "دواء مراقب (مخدرات)" : "Controlled Substance"}
                  </Badge>
                )}
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Prescription Detail & Approval Panel */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between border-b pb-4">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Pill className="h-5 w-5 text-primary" />
                <span className="font-mono">{selectedRx.orderNumber}</span> — {t("dashboard.rx_queue_title")}
              </CardTitle>
              <CardDescription>
                {t("dashboard.col_customer")}: {locale === "ar" ? selectedRx.patientNameAr : selectedRx.patientName} | {t("dashboard.col_time")}: {selectedRx.date}
              </CardDescription>
            </div>
            <Badge
              variant={
                selectedRx.status === "approved"
                  ? "success"
                  : selectedRx.status === "rejected"
                  ? "destructive"
                  : "warning"
              }
            >
              {t(`status.${selectedRx.status}`)}
            </Badge>
          </CardHeader>

          <CardContent className="p-6 space-y-6">
            {/* Warning banner for controlled substances */}
            {selectedRx.isControlled && (
              <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 shrink-0" />
                <div className="text-xs">
                  <span className="font-bold">{t("rx.controlled_alert_title")}:</span> {t("rx.controlled_alert_desc")}
                </div>
              </div>
            )}

            {/* Clinical Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="space-y-1 p-3 rounded-lg bg-muted/40 border">
                <span className="text-muted-foreground font-medium">{t("rx.prescriber")}</span>
                <p className="font-semibold text-foreground">{locale === "ar" ? selectedRx.prescriberNameAr : selectedRx.prescriberName}</p>
              </div>
              <div className="space-y-1 p-3 rounded-lg bg-muted/40 border">
                <span className="text-muted-foreground font-medium">{t("rx.medication")}</span>
                <p className="font-semibold text-foreground">{locale === "ar" ? selectedRx.medicationAr : selectedRx.medication}</p>
              </div>
              <div className="space-y-1 p-3 rounded-lg bg-muted/40 border md:col-span-2">
                <span className="text-muted-foreground font-medium">{t("rx.instructions")}</span>
                <p className="font-semibold text-foreground">{locale === "ar" ? selectedRx.dosageAr : selectedRx.dosage}</p>
              </div>
            </div>

            {/* Prescription Document Preview Mock */}
            <div className="border rounded-lg p-6 bg-muted/20 text-center space-y-2">
              <FileText className="h-10 w-10 text-primary mx-auto" />
              <p className="text-xs font-medium">{t("rx.document_preview")}</p>
              <a href={selectedRx.fileUrl} target="_blank" rel="noreferrer" className="text-xs text-primary hover:underline block">
                {t("rx.view_pdf")}
              </a>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t">
              <Button
                variant="destructive"
                onClick={() => handleReject(selectedRx.id)}
                disabled={selectedRx.status === "rejected"}
                className="gap-2 text-xs"
              >
                <XCircle className="h-4 w-4" /> {t("rx.reject_btn")}
              </Button>
              <Button
                variant="default"
                onClick={() => handleApprove(selectedRx.id)}
                disabled={selectedRx.status === "approved"}
                className="gap-2 bg-emerald-600 hover:bg-emerald-700 text-xs"
              >
                <CheckCircle className="h-4 w-4" /> {t("rx.approve_btn")}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
