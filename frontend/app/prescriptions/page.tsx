"use client";

import React, { useState } from "react";
import { Pill, CheckCircle, XCircle, FileText, AlertTriangle, User, Calendar, ShieldAlert } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface RxItem {
  id: string;
  orderNumber: string;
  patientName: string;
  prescriberName: string;
  medication: string;
  dosage: string;
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
    prescriberName: "Dr. Khaled Nader (License #MD-8841)",
    medication: "Amoxicillin 500mg (20 Caps)",
    dosage: "1 capsule 3 times daily for 7 days",
    status: "uploaded",
    isControlled: false,
    fileUrl: "https://storage.pharmacloud/rx/sample1.pdf",
    date: "2026-08-15 04:10",
  },
  {
    id: "rx-2",
    orderNumber: "ORD-2026-9884",
    patientName: "Sultan Al-Otaibi",
    prescriberName: "Dr. Fatima Zahra (Consultant Neurologist)",
    medication: "Pregabalin 75mg (30 Caps)",
    dosage: "1 capsule twice daily",
    status: "uploaded",
    isControlled: true,
    fileUrl: "https://storage.pharmacloud/rx/sample2.pdf",
    date: "2026-08-15 03:45",
  },
  {
    id: "rx-3",
    orderNumber: "ORD-2026-9762",
    patientName: "Mona Salem",
    prescriberName: "Dr. Tariq Hamad (Cardiology)",
    medication: "Atorvastatin 20mg (28 Tab)",
    dosage: "1 tablet once daily at bedtime",
    status: "approved",
    isControlled: false,
    fileUrl: "https://storage.pharmacloud/rx/sample3.pdf",
    date: "2026-08-14 18:20",
  },
];

export default function PrescriptionsPage() {
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
        <h1 className="text-2xl font-bold tracking-tight">Clinical Prescriptions & Dispensing</h1>
        <p className="text-sm text-muted-foreground">Pharmacist verification queue, regulatory checks, and clinical sign-off.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Prescription List */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-sm font-semibold">Prescription Queue ({prescriptions.length})</CardTitle>
            <CardDescription>Select a prescription to inspect clinical details.</CardDescription>
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
                  <span className="text-xs font-bold text-foreground">{rx.orderNumber}</span>
                  <Badge
                    variant={
                      rx.status === "approved" ? "success" : rx.status === "rejected" ? "destructive" : "warning"
                    }
                  >
                    {rx.status}
                  </Badge>
                </div>
                <p className="text-xs font-medium text-foreground mt-1">{rx.patientName}</p>
                <p className="text-[11px] text-muted-foreground truncate">{rx.medication}</p>
                {rx.isControlled && (
                  <Badge variant="destructive" className="mt-2 text-[10px] px-1 py-0 gap-1">
                    <ShieldAlert className="h-3 w-3" /> Controlled Substance
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
                {selectedRx.orderNumber} — Clinical Verification
              </CardTitle>
              <CardDescription>Patient: {selectedRx.patientName} | Date: {selectedRx.date}</CardDescription>
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
              {selectedRx.status.toUpperCase()}
            </Badge>
          </CardHeader>

          <CardContent className="p-6 space-y-6">
            {/* Warning banner for controlled substances */}
            {selectedRx.isControlled && (
              <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 shrink-0" />
                <div className="text-xs">
                  <span className="font-bold">Controlled Substance Alert:</span> This medication is subject to narcotics/controlled drug tracking. Verify doctor license and patient national ID before approval.
                </div>
              </div>
            )}

            {/* Clinical Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="space-y-1 p-3 rounded-lg bg-muted/40 border">
                <span className="text-muted-foreground font-medium">Prescriber</span>
                <p className="font-semibold text-foreground">{selectedRx.prescriberName}</p>
              </div>
              <div className="space-y-1 p-3 rounded-lg bg-muted/40 border">
                <span className="text-muted-foreground font-medium">Medication Prescribed</span>
                <p className="font-semibold text-foreground">{selectedRx.medication}</p>
              </div>
              <div className="space-y-1 p-3 rounded-lg bg-muted/40 border md:col-span-2">
                <span className="text-muted-foreground font-medium">Dosage & Administration Instructions</span>
                <p className="font-semibold text-foreground">{selectedRx.dosage}</p>
              </div>
            </div>

            {/* Prescription Document Preview Mock */}
            <div className="border rounded-lg p-6 bg-muted/20 text-center space-y-2">
              <FileText className="h-10 w-10 text-primary mx-auto" />
              <p className="text-xs font-medium">Uploaded Medical Prescription Document</p>
              <a href={selectedRx.fileUrl} target="_blank" rel="noreferrer" className="text-xs text-primary hover:underline block">
                View Original Signed File (PDF)
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
                <XCircle className="h-4 w-4" /> Reject Prescription
              </Button>
              <Button
                variant="default"
                onClick={() => handleApprove(selectedRx.id)}
                disabled={selectedRx.status === "approved"}
                className="gap-2 bg-emerald-600 hover:bg-emerald-700 text-xs"
              >
                <CheckCircle className="h-4 w-4" /> Approve & Release for Dispensing
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
