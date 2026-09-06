"use client";

import React, { useState } from "react";
import { Plus, BookOpen, Layers, CheckCircle2, ChevronDown, ChevronRight, TrendingUp, DollarSign, Receipt, AlertCircle, X } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ConfirmationDialog } from "@/components/ui/confirmation-dialog";
import { useI18n } from "@/lib/i18n";
import { formatCurrency } from "@/lib/utils";

interface JournalEntry {
  id: string;
  journalNo: string;
  desc: string;
  debit: string;
  credit: string;
  amount: number;
  status: string;
}

const initialJournals: JournalEntry[] = [
  { id: "1", journalNo: "JRN-2026-0089", desc: "إقفال مبيعات نقطة البيع اليومية (INV-8891)", debit: "1010 - نقدية الصندوق", credit: "4000 - إيراد مبيعات الأدوية", amount: 12450.8, status: "posted" },
  { id: "2", journalNo: "JRN-2026-0088", desc: "استلام بضاعة مشتريات مخزنية (GRN-041)", debit: "1300 - أصول المخزون السلعي", credit: "2000 - الذمم الدائنة (الموردين)", amount: 14500.0, status: "posted" },
];

const mockChartOfAccounts = [
  {
    code: "1000",
    nameAr: "الأصول (Assets)",
    balance: 210650.0,
    children: [
      { code: "1010", nameAr: "نقدية الصناديق ونقاط البيع", balance: 45200.0 },
      { code: "1020", nameAr: "الحساب البنكي الرئيسي", balance: 83250.0 },
      { code: "1200", nameAr: "الذمم المدينة (العيادات والتأمين)", balance: 34200.0 },
      { code: "1300", nameAr: "مخزون الأدوية والمستلزمات", balance: 48000.0 },
    ],
  },
  {
    code: "2000",
    nameAr: "الالتزامات والخصوم (Liabilities)",
    balance: 18900.0,
    children: [
      { code: "2010", nameAr: "الذمم الدائنة (شركات الأدوية والموردين)", balance: 18900.0 },
    ],
  },
  {
    code: "4000",
    nameAr: "الإيرادات (Revenue)",
    balance: 142500.0,
    children: [
      { code: "4010", nameAr: "مبيعات الأدوية والوصفات الطبية", balance: 98000.0 },
      { code: "4020", nameAr: "مبيعات المستلزمات والمكملات الغذائية", balance: 44500.0 },
    ],
  },
];

export default function AccountingPage() {
  const { t, locale } = useI18n();
  const [activeTab, setActiveTab] = useState<"journals" | "chart">("journals");
  const [journals, setJournals] = useState<JournalEntry[]>(initialJournals);
  const [isJournalModalOpen, setIsJournalModalOpen] = useState(false);
  const [isConfirmPostOpen, setIsConfirmPostOpen] = useState(false);
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({ "1000": true, "2000": true, "4000": true });
  const [isToastOpen, setIsToastOpen] = useState(false);

  const [journalDesc, setJournalDesc] = useState("");
  const [journalAmount, setJournalAmount] = useState("500.00");

  const toggleNode = (code: string) => {
    setExpandedNodes((prev) => ({ ...prev, [code]: !prev[code] }));
  };

  const handlePostJournal = () => {
    const newJ: JournalEntry = {
      id: String(journals.length + 1),
      journalNo: `JRN-2026-00${90 + journals.length}`,
      desc: journalDesc || "قيد تسوية محاسبية يدوية",
      debit: "1010 - نقدية الصندوق",
      credit: "4000 - إيراد مبيعات",
      amount: Number(journalAmount) || 500,
      status: "posted",
    };
    setJournals([newJ, ...journals]);
    setIsConfirmPostOpen(false);
    setIsJournalModalOpen(false);
    setJournalDesc("");
    setIsToastOpen(true);
    setTimeout(() => setIsToastOpen(false), 2000);
  };

  return (
    <div className="space-y-4 font-sans">
      {/* Toast Notification */}
      {isToastOpen && (
        <div className="fixed top-4 end-4 z-50 bg-emerald-600 text-white px-4 py-2.5 rounded-xl shadow-2xl text-xs font-bold flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
          <CheckCircle2 className="h-4 w-4" />
          <span>{locale === "ar" ? "تم ترحيل القيد لدفتر الأستاذ العام بنجاح" : "Journal posted successfully"}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-amber-500/10 text-amber-600">
            <TrendingUp className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground">{locale === "ar" ? "الإدارة المالية ودفتر الأستاذ العام" : "General Ledger & Accounting"}</h1>
            <p className="text-[11px] text-muted-foreground">{locale === "ar" ? "القيود المزدوجة الآلية، دليل الحسابات، ومطابقة الأرصدة" : "Double-entry journals, chart of accounts & balance sheets"}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button size="sm" onClick={() => setIsJournalModalOpen(true)} className="gap-1.5 text-xs bg-amber-600 hover:bg-amber-700 font-bold h-8">
            <Plus className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "إنشاء قيد يدوي" : "New Journal"}</span>
          </Button>
        </div>
      </div>

      {/* Accounting KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <Card className="p-3.5 rounded-xl border bg-card">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "نقدية الصناديق والبنوك" : "Cash & Bank"}</span>
          <p className="text-xl font-extrabold mt-1 text-foreground font-mono">{formatCurrency(128450.0)}</p>
          <p className="text-[10px] text-muted-foreground mt-1">مطابق مع كشوفات الحساب</p>
        </Card>
        <Card className="p-3.5 rounded-xl border bg-card">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "الذمم المدينة (AR)" : "Receivables"}</span>
          <p className="text-xl font-extrabold mt-1 text-emerald-600 font-mono">{formatCurrency(34200.0)}</p>
          <p className="text-[10px] text-emerald-600 font-semibold mt-1">مطالبات عيادات وتأمين معتمدة</p>
        </Card>
        <Card className="p-3.5 rounded-xl border bg-card">
          <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "الذمم الدائنة (AP)" : "Payables"}</span>
          <p className="text-xl font-extrabold mt-1 text-destructive font-mono">{formatCurrency(18900.0)}</p>
          <p className="text-[10px] text-muted-foreground mt-1">فواتير شركات التوزيع مستحقة</p>
        </Card>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex items-center gap-1.5 p-1 bg-muted/40 rounded-xl border text-xs w-fit">
        <Button variant={activeTab === "journals" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("journals")} className="h-7 text-xs font-semibold gap-1">
          <BookOpen className="h-3.5 w-3.5" />
          <span>{locale === "ar" ? "سجل القيود المحاسبية" : "Journals"}</span>
        </Button>
        <Button variant={activeTab === "chart" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("chart")} className="h-7 text-xs font-semibold gap-1">
          <Layers className="h-3.5 w-3.5" />
          <span>{locale === "ar" ? "شجرة دليل الحسابات" : "Chart of Accounts"}</span>
        </Button>
      </div>

      {activeTab === "journals" ? (
        <Card className="rounded-xl border bg-card overflow-hidden">
          <CardHeader className="p-3 border-b bg-muted/20">
            <CardTitle className="text-xs font-bold text-foreground">{locale === "ar" ? "دفتر اليومية والقيود المرحلة" : "General Journal Logs"}</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left rtl:text-right">
                <thead className="bg-muted/30 font-medium text-muted-foreground border-b text-[11px]">
                  <tr>
                    <th className="p-2.5">رقم القيد</th>
                    <th className="p-2.5">البيان والوصف</th>
                    <th className="p-2.5">المدين</th>
                    <th className="p-2.5">الدائن</th>
                    <th className="p-2.5 text-right rtl:text-left">المبلغ</th>
                    <th className="p-2.5">الحالة</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {journals.map((j) => (
                    <tr key={j.id} className="hover:bg-muted/40 transition-colors">
                      <td className="p-2.5 font-mono font-bold text-primary">{j.journalNo}</td>
                      <td className="p-2.5 font-medium text-foreground">{j.desc}</td>
                      <td className="p-2.5 font-mono text-[11px] text-muted-foreground">{j.debit}</td>
                      <td className="p-2.5 font-mono text-[11px] text-muted-foreground">{j.credit}</td>
                      <td className="p-2.5 text-right rtl:text-left font-bold font-mono text-foreground">{formatCurrency(j.amount)}</td>
                      <td className="p-2.5">
                        <Badge variant="success" className="text-[9px] px-1.5 py-0">
                          {t("status.posted")}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className="rounded-xl border bg-card p-4 space-y-2.5">
          {mockChartOfAccounts.map((node) => (
            <div key={node.code} className="border rounded-xl overflow-hidden">
              <div
                onClick={() => toggleNode(node.code)}
                className="p-2.5 bg-muted/30 flex items-center justify-between cursor-pointer hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center gap-2">
                  {expandedNodes[node.code] ? <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" /> : <ChevronRight className="h-3.5 w-3.5 text-muted-foreground rtl:rotate-180" />}
                  <span className="font-bold text-xs font-mono">{node.code}</span>
                  <span className="font-semibold text-xs text-foreground">{node.nameAr}</span>
                </div>
                <span className="font-bold font-mono text-xs text-primary">{formatCurrency(node.balance)}</span>
              </div>

              {expandedNodes[node.code] && node.children && (
                <div className="p-2 pl-6 rtl:pl-2 rtl:pr-6 space-y-1.5 bg-card divide-y">
                  {node.children.map((child) => (
                    <div key={child.code} className="pt-1.5 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-muted-foreground text-[11px]">{child.code}</span>
                        <span className="font-medium text-foreground">{child.nameAr}</span>
                      </div>
                      <span className="font-mono text-muted-foreground">{formatCurrency(child.balance)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </Card>
      )}

      {/* Manual Journal Modal */}
      {isJournalModalOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="max-w-md w-full p-5 space-y-4 shadow-2xl border bg-card rounded-2xl animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-2">
              <div className="flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-amber-600" />
                <h3 className="font-bold text-sm text-foreground">
                  {locale === "ar" ? "إنشاء قيد محاسبي يدوي" : "New Manual Journal"}
                </h3>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsJournalModalOpen(false)} className="h-7 w-7">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="space-y-1">
                <label className="font-semibold text-foreground">البيان / الوصف</label>
                <Input
                  value={journalDesc}
                  onChange={(e) => setJournalDesc(e.target.value)}
                  placeholder="مثال: تسوية نقدية صندوق #1"
                  className="text-xs"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <label className="font-semibold text-foreground">المدين</label>
                  <Input defaultValue="1010 - نقدية الصندوق" className="font-mono text-xs" readOnly />
                </div>
                <div className="space-y-1">
                  <label className="font-semibold text-foreground">الدائن</label>
                  <Input defaultValue="4000 - إيرادات المبيعات" className="font-mono text-xs" readOnly />
                </div>
              </div>
              <div className="space-y-1">
                <label className="font-semibold text-foreground">المبلغ ($)</label>
                <Input
                  value={journalAmount}
                  onChange={(e) => setJournalAmount(e.target.value)}
                  className="font-mono text-xs font-bold"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t">
              <Button variant="outline" size="sm" onClick={() => setIsJournalModalOpen(false)} className="text-xs h-8">
                {locale === "ar" ? "إلغاء" : "Cancel"}
              </Button>
              <Button size="sm" onClick={() => setIsConfirmPostOpen(true)} className="text-xs font-bold bg-amber-600 hover:bg-amber-700 h-8">
                <CheckCircle2 className="h-4 w-4 mr-1" />
                {locale === "ar" ? "ترحيل القيد" : "Post"}
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={isConfirmPostOpen}
        title={locale === "ar" ? "تأكيد ترحيل القيد" : "Confirm Journal Post"}
        description={locale === "ar" ? `هل أنت متأكد من ترحيل القيد المالي بقيمة ${formatCurrency(Number(journalAmount) || 0)}؟` : `Post journal of ${formatCurrency(Number(journalAmount) || 0)}?`}
        confirmLabel={locale === "ar" ? "تأكيد وترحيل" : "Confirm"}
        cancelLabel={locale === "ar" ? "إلغاء" : "Cancel"}
        onConfirm={handlePostJournal}
        onCancel={() => setIsConfirmPostOpen(false)}
      />
    </div>
  );
}
