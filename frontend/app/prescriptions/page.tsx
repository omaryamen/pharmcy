"use client";

import React, { useState } from "react";
import {
  Pill,
  CheckCircle2,
  XCircle,
  FileText,
  AlertTriangle,
  ShieldAlert,
  Stethoscope,
  Clock,
  User,
  ExternalLink,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { EmptyState } from "@/components/ui/empty-state";
import { ConfirmationDialog } from "@/components/ui/confirmation-dialog";
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
  rejectionReason?: string;
}

const mockPrescriptions: RxItem[] = [
  {
    id: "rx-1",
    orderNumber: "ORD-2026-9901",
    patientName: "Yasmin Al-Noor (34 yrs)",
    patientNameAr: "ياسمين النور (34 سنة)",
    prescriberName: "Dr. Khaled Nader (MD-8841)",
    prescriberNameAr: "د. خالد نادر (ترخيص #MD-8841)",
    medication: "Amoxicillin 500mg (20 Caps)",
    medicationAr: "أموكسيسيلين 500 ملجم (20 كبسولة)",
    dosage: "1 capsule 3 times daily for 7 days",
    dosageAr: "كبسولة واحدة 3 مرات يومياً لمدة 7 أيام",
    status: "uploaded",
    isControlled: false,
    fileUrl: "https://storage.pharmacloud/rx/sample1.pdf",
    date: "04:10 PM",
  },
  {
    id: "rx-2",
    orderNumber: "ORD-2026-9884",
    patientName: "Sultan Al-Otaibi (48 yrs)",
    patientNameAr: "سلطان العتيبي (48 سنة)",
    prescriberName: "Dr. Fatima Zahra (Neurology)",
    prescriberNameAr: "د. فاطمة الزهراء (استشارية الأعصاب)",
    medication: "Pregabalin 75mg (30 Caps)",
    medicationAr: "بريجابالين 75 ملجم (30 كبسولة)",
    dosage: "1 capsule twice daily",
    dosageAr: "كبسولة واحدة مرتين يومياً",
    status: "uploaded",
    isControlled: true,
    fileUrl: "https://storage.pharmacloud/rx/sample2.pdf",
    date: "03:45 PM",
  },
  {
    id: "rx-3",
    orderNumber: "ORD-2026-9762",
    patientName: "Mona Salem (62 yrs)",
    patientNameAr: "منى سالم (62 سنة)",
    prescriberName: "Dr. Tariq Hamad (Cardiology)",
    prescriberNameAr: "د. طارق حمد (استشاري القلب)",
    medication: "Atorvastatin 20mg (28 Tab)",
    medicationAr: "أتورفاستاتين 20 ملجم (28 قرص)",
    dosage: "1 tablet once daily at bedtime",
    dosageAr: "قرص واحد يومياً قبل النوم",
    status: "approved",
    isControlled: false,
    fileUrl: "https://storage.pharmacloud/rx/sample3.pdf",
    date: "02:20 PM",
  },
];

export default function PrescriptionsPage() {
  const { t, locale } = useI18n();
  const [prescriptions, setPrescriptions] = useState<RxItem[]>(mockPrescriptions);
  const [selectedRx, setSelectedRx] = useState<RxItem>(mockPrescriptions[0]);
  const [isRejectModalOpen, setIsRejectModalOpen] = useState(false);
  const [isApproveConfirmOpen, setIsApproveConfirmOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState(locale === "ar" ? "الجرعة المقررة تتجاوز الحد العلاجي الموصى به" : "Dosage exceeds clinical safety ceiling");

  const handleApprove = (id: string) => {
    setPrescriptions((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: "approved" as const } : r))
    );
    setSelectedRx((prev) => (prev.id === id ? { ...prev, status: "approved" as const } : prev));
    setIsApproveConfirmOpen(false);
  };

  const handleConfirmReject = () => {
    setPrescriptions((prev) =>
      prev.map((r) => (r.id === selectedRx.id ? { ...r, status: "rejected" as const, rejectionReason: rejectReason } : r))
    );
    setSelectedRx((prev) => (prev.id === selectedRx.id ? { ...prev, status: "rejected" as const, rejectionReason: rejectReason } : prev));
    setIsRejectModalOpen(false);
  };

  return (
    <div className="space-y-4 font-sans">
      {/* Clean Top Header */}
      <div className="flex items-center justify-between pb-2 border-b">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-600">
            <Stethoscope className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground">{locale === "ar" ? "طابور الوصفات والاعتماد السريري" : "Clinical Prescriptions Queue"}</h1>
            <p className="text-[11px] text-muted-foreground">{locale === "ar" ? "تدقيق الجرعات واعتماد صرف الأدوية" : "Verify dosages and sign-off drug dispensing"}</p>
          </div>
        </div>

        <Badge variant="outline" className="text-xs gap-1 py-1">
          <span className="font-mono font-bold text-primary">{prescriptions.filter(r => r.status === "uploaded").length}</span>
          <span>{locale === "ar" ? "وصفات معلقة" : "Pending"}</span>
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Prescription Queue List */}
        <div className="lg:col-span-4 space-y-2">
          <div className="text-xs font-bold text-muted-foreground px-1">{locale === "ar" ? "الوصفات الواردة" : "Incoming Queue"}</div>
          <div className="space-y-2">
            {prescriptions.map((rx) => (
              <Card
                key={rx.id}
                onClick={() => setSelectedRx(rx)}
                className={`p-3 cursor-pointer transition-all border rounded-xl ${
                  selectedRx.id === rx.id ? "border-primary bg-primary/5 shadow-sm" : "hover:border-border/80 hover:bg-muted/30"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-foreground">{rx.orderNumber}</span>
                  <Badge
                    variant={
                      rx.status === "approved" ? "success" : rx.status === "rejected" ? "destructive" : "warning"
                    }
                    className="text-[10px] px-1.5 py-0"
                  >
                    {t(`status.${rx.status}`)}
                  </Badge>
                </div>

                <p className="text-xs font-bold text-foreground mt-1.5">{locale === "ar" ? rx.patientNameAr : rx.patientName}</p>
                <p className="text-[11px] text-muted-foreground truncate">{locale === "ar" ? rx.medicationAr : rx.medication}</p>

                <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-border/40 text-[10px] text-muted-foreground">
                  <span className="flex items-center gap-1 font-mono"><Clock className="h-3 w-3" /> {rx.date}</span>
                  {rx.isControlled && (
                    <span className="text-destructive font-bold flex items-center gap-1">
                      <ShieldAlert className="h-3 w-3" /> {locale === "ar" ? "مراقب" : "Controlled"}
                    </span>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Selected Prescription Verification & Actions */}
        <Card className="lg:col-span-8 p-4 md:p-5 flex flex-col justify-between rounded-xl border bg-card">
          <div className="space-y-4">
            {/* Header with status */}
            <div className="flex items-center justify-between pb-3 border-b">
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold text-sm text-primary">{selectedRx.orderNumber}</span>
                <span className="text-muted-foreground text-xs">• {selectedRx.date}</span>
              </div>
              <Badge
                variant={
                  selectedRx.status === "approved" ? "success" : selectedRx.status === "rejected" ? "destructive" : "warning"
                }
                className="text-xs font-semibold px-2 py-0.5"
              >
                {t(`status.${selectedRx.status}`)}
              </Badge>
            </div>

            {/* Controlled Drug Alert Banner */}
            {selectedRx.isControlled && (
              <div className="p-2.5 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive flex items-center gap-2.5 text-xs">
                <AlertTriangle className="h-4 w-4 shrink-0" />
                <span className="font-semibold">
                  {locale === "ar" ? "تنبيه سريري: دواء مراقب يتطلب مطابقة هوية المريض وتوثيق رقم الترخيص." : "Clinical Alert: Controlled narcotic requires patient ID verification."}
                </span>
              </div>
            )}

            {/* Structured Details Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-muted/30 border space-y-1">
                <span className="text-[11px] text-muted-foreground">{locale === "ar" ? "المريض" : "Patient"}</span>
                <p className="font-bold text-foreground text-xs">{locale === "ar" ? selectedRx.patientNameAr : selectedRx.patientName}</p>
              </div>

              <div className="p-3 rounded-lg bg-muted/30 border space-y-1">
                <span className="text-[11px] text-muted-foreground">{locale === "ar" ? "الطبيب المعالج" : "Prescribing Doctor"}</span>
                <p className="font-bold text-foreground text-xs">{locale === "ar" ? selectedRx.prescriberNameAr : selectedRx.prescriberName}</p>
              </div>

              <div className="p-3 rounded-lg bg-muted/30 border space-y-1 md:col-span-2">
                <span className="text-[11px] text-muted-foreground">{locale === "ar" ? "الدواء والجرعة المقررة" : "Medication & Dosage"}</span>
                <p className="font-bold text-foreground text-xs text-primary">{locale === "ar" ? selectedRx.medicationAr : selectedRx.medication}</p>
                <p className="text-[11px] text-foreground/80 mt-0.5">{locale === "ar" ? selectedRx.dosageAr : selectedRx.dosage}</p>
              </div>
            </div>

            {selectedRx.rejectionReason && (
              <div className="p-2.5 rounded-lg bg-destructive/10 border border-destructive/20 text-xs">
                <span className="font-bold text-destructive">{locale === "ar" ? "سبب الرفض: " : "Rejection Reason: "}</span>
                <span className="text-foreground">{selectedRx.rejectionReason}</span>
              </div>
            )}

            {/* Prescription Attachment Link */}
            <div className="flex items-center justify-between p-2.5 rounded-lg border bg-muted/10 text-xs">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-primary" />
                <span className="font-medium text-foreground">{locale === "ar" ? "الملف الطبي المرفق (PDF)" : "Attached Medical Rx (PDF)"}</span>
              </div>
              <a
                href={selectedRx.fileUrl}
                target="_blank"
                rel="noreferrer"
                className="text-primary hover:underline flex items-center gap-1 font-semibold text-[11px]"
              >
                <span>{locale === "ar" ? "معاينة الوصفة" : "View Rx"}</span>
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>

          {/* Action Bar */}
          <div className="flex items-center justify-end gap-2 pt-4 mt-4 border-t">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsRejectModalOpen(true)}
              disabled={selectedRx.status === "rejected"}
              className="gap-1.5 text-xs text-destructive border-destructive/30 hover:bg-destructive/10 h-9 px-3 font-semibold"
            >
              <XCircle className="h-4 w-4" />
              <span>{locale === "ar" ? "رفض الوصفة" : "Reject"}</span>
            </Button>
            <Button
              size="sm"
              onClick={() => setIsApproveConfirmOpen(true)}
              disabled={selectedRx.status === "approved"}
              className="gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-xs text-white h-9 px-4 font-bold shadow-sm"
            >
              <CheckCircle2 className="h-4 w-4" />
              <span>{selectedRx.status === "approved" ? (locale === "ar" ? "معتمدة ومصروفة" : "Dispensed") : (locale === "ar" ? "اعتماد وصرف الدواء" : "Approve & Dispense")}</span>
            </Button>
          </div>
        </Card>
      </div>

      {/* Confirmation Dialog for Approving Rx */}
      <ConfirmationDialog
        isOpen={isApproveConfirmOpen}
        title={locale === "ar" ? "اعتماد وصرف الوصفة" : "Approve Prescription"}
        description={locale === "ar" ? `تأكيد التحقق السريري وصرف دواء ${selectedRx.medicationAr} للمريض؟` : `Confirm clinical verification and dispense ${selectedRx.medication}?`}
        confirmLabel={locale === "ar" ? "اعتماد وصرف" : "Approve"}
        cancelLabel={locale === "ar" ? "إلغاء" : "Cancel"}
        onConfirm={() => handleApprove(selectedRx.id)}
        onCancel={() => setIsApproveConfirmOpen(false)}
      />

      {/* Clinical Rejection Reason Modal */}
      {isRejectModalOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="max-w-sm w-full p-5 space-y-3 bg-card shadow-2xl border">
            <div className="flex items-center gap-2 text-destructive">
              <XCircle className="h-5 w-5" />
              <h3 className="text-sm font-bold text-foreground">
                {locale === "ar" ? "سبب رفض الوصفة" : "Prescription Rejection"}
              </h3>
            </div>

            <div className="space-y-1.5 py-1">
              <label className="text-xs font-semibold text-foreground">
                {locale === "ar" ? "المبرر السريري" : "Clinical Reason"}
              </label>
              <Input
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                className="text-xs"
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t">
              <Button variant="outline" size="sm" onClick={() => setIsRejectModalOpen(false)} className="text-xs h-8">
                {locale === "ar" ? "إلغاء" : "Cancel"}
              </Button>
              <Button variant="destructive" size="sm" onClick={handleConfirmReject} className="text-xs h-8 font-bold">
                {locale === "ar" ? "تأكيد الرفض" : "Confirm"}
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
