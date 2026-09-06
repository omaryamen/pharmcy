"use client";

import React, { useState } from "react";
import {
  ShieldAlert,
  Server,
  ToggleRight,
  Building2,
  CreditCard,
  Flag,
  UserCheck,
  Activity,
  AlertTriangle,
  History,
  Settings as SettingsIcon,
  Search,
  Plus,
  Play,
  Pause,
  Eye,
  LogOut,
  RefreshCw,
  Cpu,
  HardDrive,
  Database,
  CheckCircle2,
  X,
  Lock,
  Mail,
  Shield,
  Save,
  Trash2,
  Edit,
  ExternalLink,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ConfirmationDialog } from "@/components/ui/confirmation-dialog";
import { useI18n } from "@/lib/i18n";
import { cn } from "@/lib/utils";


type AdminTab = "overview" | "tenants" | "plans" | "flags" | "users" | "health" | "maintenance" | "audit" | "settings";

interface MockTenant {
  id: string;
  code: string;
  name: string;
  nameAr: string;
  plan: string;
  status: "active" | "trial" | "suspended";
  usersCount: number;
  branchesCount: number;
  createdDate: string;
  mrr: string;
}

const initialTenantsList: MockTenant[] = [
  { id: "1", code: "TNT-AMAL", name: "Al-Amal Pharmacy Chain", nameAr: "سلسلة صيدليات الأمل", plan: "Enterprise", status: "active", usersCount: 18, branchesCount: 5, createdDate: "2026-01-10", mrr: "$299.00" },
  { id: "2", code: "TNT-SHIFA", name: "Al-Shifa Medical Complex", nameAr: "مجمع الشفاء الطبي", plan: "Professional", status: "active", usersCount: 8, branchesCount: 2, createdDate: "2026-02-15", mrr: "$149.00" },
  { id: "3", code: "TNT-NOOR", name: "Al-Noor Community Rx", nameAr: "صيدلية النور الأهلية", plan: "Starter (Trial)", status: "trial", usersCount: 3, branchesCount: 1, createdDate: "2026-08-01", mrr: "$0.00" },
  { id: "4", code: "TNT-DELTA", name: "Delta Healthcare Supply", nameAr: "دلتا للرعاية الصيدلانية", plan: "Enterprise", status: "suspended", usersCount: 12, branchesCount: 3, createdDate: "2025-11-20", mrr: "$299.00" },
];

export default function AdminPage() {
  const { t, locale } = useI18n();
  const [activeTab, setActiveTab] = useState<AdminTab>("overview");
  const [impersonatedTenant, setImpersonatedTenant] = useState<string | null>(null);
  const [tenants, setTenants] = useState<MockTenant[]>(initialTenantsList);
  const [tenantSearch, setTenantSearch] = useState("");
  const [isMaintenanceActive, setIsMaintenanceActive] = useState(false);
  const [maintenanceMessage, setMaintenanceMessage] = useState("جاري تنفيذ صيانة وتحديث مجدول لخوادم المنصة السحابية. سنعود خلال 15 دقيقة.");
  
  // Modals
  const [isNewTenantModalOpen, setIsNewTenantModalOpen] = useState(false);
  const [newTenantForm, setNewTenantForm] = useState({ code: "TNT-NEW", nameAr: "", plan: "Professional", adminEmail: "" });
  const [isNewAdminModalOpen, setIsNewAdminModalOpen] = useState(false);
  const [newAdminEmail, setNewAdminEmail] = useState("");
  const [isSavedToastOpen, setIsSavedToastOpen] = useState(false);
  const [isDiagnosticsRefreshing, setIsDiagnosticsRefreshing] = useState(false);

  // Feature Flags State
  const [flags, setFlags] = useState([
    { key: "ENABLE_AI_PRESCRIPTION_OCR", name: "AI Prescription OCR", scope: "Global", isEnabled: true, lastChanged: "2026-08-14" },
    { key: "ENABLE_ZATCA_E_INVOICE_PHASE2", name: "ZATCA E-Invoicing Phase 2", scope: "Tenant (KSA)", isEnabled: true, lastChanged: "2026-08-10" },
    { key: "ENABLE_TELEPHARMACY_B2C", name: "Telepharmacy Video Consult", scope: "Beta (Opt-in)", isEnabled: false, lastChanged: "2026-08-02" },
    { key: "ENABLE_AUTOMATED_DRUG_RECALL_SYNC", name: "SFDA Recall Auto-Sync", scope: "Global", isEnabled: true, lastChanged: "2026-07-28" },
  ]);

  // SaaS Plans State
  const [plans, setPlans] = useState([
    { id: "p1", name: "Starter", nameAr: "الباقة الأساسية", price: "$49/mo", maxBranches: 1, maxUsers: 3, activeCount: 14 },
    { id: "p2", name: "Professional", nameAr: "الباقة المتقدمة", price: "$149/mo", maxBranches: 3, maxUsers: 10, activeCount: 22 },
    { id: "p3", name: "Enterprise", nameAr: "باقة سلاسل الصيدليات", price: "$299/mo", maxBranches: 10, maxUsers: 50, activeCount: 6 },
  ]);

  // SuperAdmins State
  const [adminsList, setAdminsList] = useState([
    { id: "a1", name: "مشرف المنصة الرئيسي", email: "platform_admin@pharmacloud.com", role: "SuperAdmin (Root)", lastActive: "الآن (متصل)", status: "active" },
    { id: "a2", name: "فريق الدعم الفني والتشغيل", email: "ops_support@pharmacloud.com", role: "Cloud Ops Engineer", lastActive: "منذ ساعتين", status: "active" },
    { id: "a3", name: "مدير أمن المنظومة", email: "security_lead@pharmacloud.com", role: "Security Auditor", lastActive: "أمس", status: "active" },
  ]);

  // Platform Settings State
  const [platformSettings, setPlatformSettings] = useState({
    platformName: "فارما كلاود — المنظومة السحابية لإدارة الصيدليات",
    supportEmail: "support@pharmacloud.com",
    trialDays: "14",
    defaultCurrency: "USD ($)",
    enforce2FA: true,
  });

  const toggleFlag = (key: string) => {
    setFlags((prev) => prev.map((f) => (f.key === key ? { ...f, isEnabled: !f.isEnabled } : f)));
    showToast();
  };

  const handleStatusChange = (id: string, newStatus: "active" | "suspended") => {
    setTenants((prev) => prev.map((t) => (t.id === id ? { ...t, status: newStatus } : t)));
    showToast();
  };

  const handleCreateTenant = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTenantForm.nameAr) return;
    const newT: MockTenant = {
      id: String(tenants.length + 1),
      code: newTenantForm.code.toUpperCase(),
      name: newTenantForm.nameAr,
      nameAr: newTenantForm.nameAr,
      plan: newTenantForm.plan,
      status: "active",
      usersCount: 1,
      branchesCount: 1,
      createdDate: "2026-08-21",
      mrr: newTenantForm.plan === "Enterprise" ? "$299.00" : newTenantForm.plan === "Professional" ? "$149.00" : "$49.00",
    };
    setTenants([newT, ...tenants]);
    setIsNewTenantModalOpen(false);
    setNewTenantForm({ code: "TNT-NEW", nameAr: "", plan: "Professional", adminEmail: "" });
    showToast();
  };

  const handleAddAdmin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAdminEmail) return;
    setAdminsList([
      ...adminsList,
      { id: String(adminsList.length + 1), name: "مشرف نظام جديد", email: newAdminEmail, role: "Cloud Ops Engineer", lastActive: "جديد", status: "active" },
    ]);
    setNewAdminEmail("");
    setIsNewAdminModalOpen(false);
    showToast();
  };

  const handleRefreshDiagnostics = () => {
    setIsDiagnosticsRefreshing(true);
    setTimeout(() => {
      setIsDiagnosticsRefreshing(false);
      showToast();
    }, 800);
  };

  const showToast = () => {
    setIsSavedToastOpen(true);
    setTimeout(() => setIsSavedToastOpen(false), 2000);
  };

  const filteredTenants = tenants.filter(
    (t) =>
      t.name.toLowerCase().includes(tenantSearch.toLowerCase()) ||
      t.nameAr.includes(tenantSearch) ||
      t.code.toLowerCase().includes(tenantSearch.toLowerCase())
  );

  return (
    <div className="space-y-4 font-sans">
      {/* Toast Notification */}
      {isSavedToastOpen && (
        <div className="fixed top-4 end-4 z-50 bg-emerald-600 text-white px-4 py-2.5 rounded-xl shadow-2xl text-xs font-bold flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
          <CheckCircle2 className="h-4 w-4" />
          <span>{locale === "ar" ? "تم تنفيذ الإجراء وحفظ التعديلات بنجاح" : "Action executed successfully"}</span>
        </div>
      )}

      {/* Impersonation Active Banner */}
      {impersonatedTenant && (
        <div className="p-3 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-700 dark:text-amber-300 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 font-semibold">
            <Eye className="h-4 w-4 shrink-0" />
            <span>
              {locale === "ar" ? "أنت الآن في وضع انتحال هوية المستأجر: " : "Impersonating Tenant: "}
              <strong className="underline font-bold">{impersonatedTenant}</strong>
            </span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => { setImpersonatedTenant(null); showToast(); }}
            className="h-7 text-xs bg-background gap-1 text-foreground font-bold"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "إنهاء الجلسة والعودة للـ SuperAdmin" : "Exit Impersonation"}</span>
          </Button>
        </div>
      )}

      {/* Header & Sub-Tabs Navigation */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-2 border-b">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-purple-500/10 text-purple-600">
            <ShieldAlert className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-foreground">{locale === "ar" ? "مركز إدارة وتشغيل المنصة السحابية" : "Cloud Platform Control Center"}</h1>
              {isMaintenanceActive && (
                <Badge variant="destructive" className="text-[10px] animate-pulse">
                  {locale === "ar" ? "وضع الصيانة مفعل" : "Maintenance Active"}
                </Badge>
              )}
            </div>
            <p className="text-[11px] text-muted-foreground">{locale === "ar" ? "إدارة المستأجرين، الباقات، أعلام الميزات، وصحة الخوادم" : "Multi-tenant management, SaaS billing, flags & infrastructure telemetry"}</p>
          </div>
        </div>

        {/* Global Action */}
        <div className="flex items-center gap-2">
          <Button size="sm" onClick={() => setIsNewTenantModalOpen(true)} className="gap-1 text-xs bg-purple-600 hover:bg-purple-700 font-bold h-8">
            <Plus className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "إضافة صيدلية جديدة" : "New Tenant"}</span>
          </Button>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex flex-wrap items-center gap-1.5 p-1 bg-muted/40 rounded-xl border text-xs w-fit">
        <Button variant={activeTab === "overview" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("overview")} className="h-7 text-xs font-semibold gap-1">
          <Activity className="h-3.5 w-3.5" /> {locale === "ar" ? "نظرة عامة" : "Overview"}
        </Button>
        <Button variant={activeTab === "tenants" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("tenants")} className="h-7 text-xs font-semibold gap-1">
          <Building2 className="h-3.5 w-3.5" /> {locale === "ar" ? "المستأجرين" : "Tenants"}
        </Button>
        <Button variant={activeTab === "plans" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("plans")} className="h-7 text-xs font-semibold gap-1">
          <CreditCard className="h-3.5 w-3.5" /> {locale === "ar" ? "الباقات والأسعار" : "SaaS Plans"}
        </Button>
        <Button variant={activeTab === "flags" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("flags")} className="h-7 text-xs font-semibold gap-1">
          <Flag className="h-3.5 w-3.5" /> {locale === "ar" ? "أعلام الميزات (Flags)" : "Flags"}
        </Button>
        <Button variant={activeTab === "users" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("users")} className="h-7 text-xs font-semibold gap-1">
          <UserCheck className="h-3.5 w-3.5" /> {locale === "ar" ? "مشرفو المنصة" : "Admins"}
        </Button>
        <Button variant={activeTab === "health" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("health")} className="h-7 text-xs font-semibold gap-1">
          <Server className="h-3.5 w-3.5" /> {locale === "ar" ? "صحة الخوادم" : "Health"}
        </Button>
        <Button variant={activeTab === "maintenance" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("maintenance")} className="h-7 text-xs font-semibold gap-1">
          <AlertTriangle className="h-3.5 w-3.5" /> {locale === "ar" ? "وضع الصيانة" : "Maintenance"}
        </Button>
        <Button variant={activeTab === "audit" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("audit")} className="h-7 text-xs font-semibold gap-1">
          <History className="h-3.5 w-3.5" /> {locale === "ar" ? "سجل التدقيق" : "Audit"}
        </Button>
        <Button variant={activeTab === "settings" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("settings")} className="h-7 text-xs font-semibold gap-1">
          <SettingsIcon className="h-3.5 w-3.5" /> {locale === "ar" ? "الإعدادات" : "Settings"}
        </Button>
      </div>

      {/* Tab 1: Overview */}
      {activeTab === "overview" && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <Card className="p-3.5 rounded-xl border bg-card">
              <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "إجمالي المؤسسات والصيدليات" : "Total Tenants"}</span>
              <p className="text-xl font-extrabold mt-1 text-foreground font-mono">{tenants.length}</p>
              <p className="text-[10px] text-emerald-600 mt-1 font-semibold">{tenants.filter(t => t.status === "active").length} نشط • {tenants.filter(t => t.status === "trial").length} تجريبي</p>
            </Card>

            <Card className="p-3.5 rounded-xl border bg-card">
              <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "الإيراد الشهري المتكرر (MRR)" : "Monthly Recurring Revenue"}</span>
              <p className="text-xl font-extrabold mt-1 text-emerald-600 font-mono">$12,450.00</p>
              <p className="text-[10px] text-muted-foreground mt-1">+18.5% YoY</p>
            </Card>

            <Card className="p-3.5 rounded-xl border bg-card">
              <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "الميزات المفعلة" : "Active Feature Flags"}</span>
              <p className="text-xl font-extrabold mt-1 text-purple-600 font-mono">{flags.filter(f => f.isEnabled).length} / {flags.length}</p>
              <p className="text-[10px] text-muted-foreground mt-1">{locale === "ar" ? "التحكم اللحظي مفعل" : "Live toggle enabled"}</p>
            </Card>

            <Card className="p-3.5 rounded-xl border bg-card">
              <span className="text-[11px] text-muted-foreground font-medium">{locale === "ar" ? "صحة واستجابة الخوادم" : "Infrastructure Health"}</span>
              <p className="text-xl font-extrabold mt-1 text-emerald-600">100%</p>
              <p className="text-[10px] text-muted-foreground mt-1">{locale === "ar" ? "جميع الخدمات تعمل بكفاءة" : "All services operational"}</p>
            </Card>
          </div>

          {/* Infrastructure Health Cards */}
          <Card className="rounded-xl border bg-card overflow-hidden">
            <CardHeader className="flex flex-row items-center justify-between p-3 border-b bg-muted/20">
              <CardTitle className="text-xs font-bold text-foreground">{locale === "ar" ? "حالة الخوادم وقواعد البيانات اللحظية" : "Live Microservices & Database Status"}</CardTitle>
              <Button variant="outline" size="sm" onClick={handleRefreshDiagnostics} disabled={isDiagnosticsRefreshing} className="h-7 text-xs gap-1">
                <RefreshCw className={cn("h-3 w-3", isDiagnosticsRefreshing && "animate-spin")} />
                <span>{locale === "ar" ? "فحص وتحديث" : "Refresh Telemetry"}</span>
              </Button>
            </CardHeader>
            <CardContent className="p-3 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-2.5 rounded-lg border bg-muted/20 flex items-center gap-2.5">
                <Database className="h-4 w-4 text-emerald-600 shrink-0" />
                <div>
                  <p className="font-bold text-[11px]">PostgreSQL 16</p>
                  <span className="text-emerald-600 text-[10px] font-medium">سليم (4.2ms)</span>
                </div>
              </div>

              <div className="p-2.5 rounded-lg border bg-muted/20 flex items-center gap-2.5">
                <HardDrive className="h-4 w-4 text-emerald-600 shrink-0" />
                <div>
                  <p className="font-bold text-[11px]">Redis 7 Cache</p>
                  <span className="text-emerald-600 text-[10px] font-medium">سليم (1.1ms)</span>
                </div>
              </div>

              <div className="p-2.5 rounded-lg border bg-muted/20 flex items-center gap-2.5">
                <Cpu className="h-4 w-4 text-emerald-600 shrink-0" />
                <div>
                  <p className="font-bold text-[11px]">Celery Workers (8x)</p>
                  <span className="text-emerald-600 text-[10px] font-medium">0 مهام في الانتظار</span>
                </div>
              </div>

              <div className="p-2.5 rounded-lg border bg-muted/20 flex items-center gap-2.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <div>
                  <p className="font-bold text-[11px]">النسخ الاحتياطي</p>
                  <span className="text-muted-foreground text-[10px] font-mono">اليوم 02:00 UTC</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tab 2: Tenants */}
      {activeTab === "tenants" && (
        <Card className="rounded-xl border bg-card overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between p-3 border-b bg-muted/20">
            <div className="relative w-64 md:w-80">
              <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-muted-foreground rtl:left-auto rtl:right-2.5 pointer-events-none" />
              <Input
                placeholder={locale === "ar" ? "بحث عن مؤسسة، رمز المستأجر..." : "Search tenant name, code..."}
                value={tenantSearch}
                onChange={(e) => setTenantSearch(e.target.value)}
                className="pl-8 text-xs rtl:pl-2.5 rtl:pr-8 h-7.5"
              />
            </div>
            <Button size="sm" onClick={() => setIsNewTenantModalOpen(true)} className="gap-1 text-xs bg-purple-600 hover:bg-purple-700 font-bold h-7.5">
              <Plus className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "إنشاء مؤسسة" : "Add Tenant"}</span>
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left rtl:text-right">
                <thead className="bg-muted/30 font-medium text-muted-foreground border-b text-[11px]">
                  <tr>
                    <th className="p-2.5">رمز المؤسسة</th>
                    <th className="p-2.5">اسم المنشأة الصيدلانية</th>
                    <th className="p-2.5">الباقة</th>
                    <th className="p-2.5">الفروع والمستخدمين</th>
                    <th className="p-2.5">الحالة</th>
                    <th className="p-2.5 text-right rtl:text-left">الإجراءات</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {filteredTenants.map((tItem) => (
                    <tr key={tItem.id} className="hover:bg-muted/40 transition-colors">
                      <td className="p-2.5 font-mono font-bold text-purple-600">{tItem.code}</td>
                      <td className="p-2.5 font-semibold text-foreground">{locale === "ar" ? tItem.nameAr : tItem.name}</td>
                      <td className="p-2.5"><Badge variant="outline" className="text-[10px]">{tItem.plan}</Badge></td>
                      <td className="p-2.5 font-mono text-[11px]">{tItem.branchesCount} فروع • {tItem.usersCount} مستخدم</td>
                      <td className="p-2.5">
                        <Badge variant={tItem.status === "active" ? "success" : tItem.status === "trial" ? "warning" : "destructive"} className="text-[9px] px-1.5 py-0">
                          {tItem.status === "active" ? "نشط" : tItem.status === "trial" ? "تجريبي" : "موقوف"}
                        </Badge>
                      </td>
                      <td className="p-2.5 text-right rtl:text-left space-x-1 rtl:space-x-reverse">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => { setImpersonatedTenant(locale === "ar" ? tItem.nameAr : tItem.name); showToast(); }}
                          className="h-6.5 text-[11px] gap-1 hover:bg-purple-500/10 text-purple-700 dark:text-purple-300 font-semibold"
                        >
                          <Eye className="h-3 w-3" />
                          <span>انتحال هوية</span>
                        </Button>
                        {tItem.status === "active" ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleStatusChange(tItem.id, "suspended")}
                            className="h-6.5 text-[11px] text-destructive hover:bg-destructive/10"
                          >
                            <Pause className="h-3 w-3 mr-1" /> إيقاف
                          </Button>
                        ) : (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleStatusChange(tItem.id, "active")}
                            className="h-6.5 text-[11px] text-emerald-600 hover:bg-emerald-500/10"
                          >
                            <Play className="h-3 w-3 mr-1" /> تفعيل
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab 3: SaaS Plans */}
      {activeTab === "plans" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {plans.map((p) => (
              <Card key={p.id} className="p-4 rounded-xl border bg-card flex flex-col justify-between space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-sm text-foreground">{locale === "ar" ? p.nameAr : p.name}</h3>
                    <Badge variant="outline" className="font-mono text-xs">{p.activeCount} مشترك</Badge>
                  </div>
                  <p className="text-xl font-extrabold text-purple-600 font-mono">{p.price}</p>
                  <div className="space-y-1 text-xs text-muted-foreground pt-1 border-t">
                    <p>• حتى {p.maxBranches} فروع صيدلية</p>
                    <p>• حتى {p.maxUsers} مستخدم وصيدلي</p>
                    <p>• دعم فني ونسخ احتياطي سحابي</p>
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-2 border-t">
                  <Button variant="outline" size="sm" onClick={showToast} className="w-full text-xs h-7.5 font-semibold">
                    <Edit className="h-3 w-3 mr-1" /> {locale === "ar" ? "تعديل الميزات" : "Edit Plan"}
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: Feature Flags */}
      {activeTab === "flags" && (
        <Card className="rounded-xl border bg-card overflow-hidden">
          <CardHeader className="p-3 border-b bg-muted/20">
            <CardTitle className="text-xs font-bold">{locale === "ar" ? "التحكم في الميزات والتجارب الحية (Feature Flags)" : "Feature Flags"}</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-xs text-left rtl:text-right">
              <thead className="bg-muted/30 font-medium text-muted-foreground border-b text-[11px]">
                <tr>
                  <th className="p-2.5">معرف الميزة (Key)</th>
                  <th className="p-2.5">اسم الميزة</th>
                  <th className="p-2.5">النطاق</th>
                  <th className="p-2.5 text-right rtl:text-left">حالة التفعيل</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {flags.map((flag) => (
                  <tr key={flag.key} className="hover:bg-muted/40">
                    <td className="p-2.5 font-mono font-semibold text-foreground">{flag.key}</td>
                    <td className="p-2.5">{flag.name}</td>
                    <td className="p-2.5"><Badge variant="outline" className="text-[10px]">{flag.scope}</Badge></td>
                    <td className="p-2.5 text-right rtl:text-left">
                      <Button
                        variant={flag.isEnabled ? "default" : "outline"}
                        size="sm"
                        onClick={() => toggleFlag(flag.key)}
                        className={`h-7 text-xs font-bold ${flag.isEnabled ? "bg-emerald-600 hover:bg-emerald-700" : ""}`}
                      >
                        <ToggleRight className="h-3.5 w-3.5 mr-1" />
                        <span>{flag.isEnabled ? (locale === "ar" ? "مفعلة ✅" : "Enabled") : (locale === "ar" ? "معطلة ❌" : "Disabled")}</span>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Tab 5: SuperAdmins Users */}
      {activeTab === "users" && (
        <Card className="rounded-xl border bg-card overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between p-3 border-b bg-muted/20">
            <CardTitle className="text-xs font-bold">{locale === "ar" ? "قائمة مشرفي المنصة السحابية" : "Platform SuperAdmins"}</CardTitle>
            <Button size="sm" onClick={() => setIsNewAdminModalOpen(true)} className="gap-1 text-xs bg-purple-600 hover:bg-purple-700 font-bold h-7.5">
              <Plus className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "دعوة مشرف جديد" : "Invite Admin"}</span>
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-xs text-left rtl:text-right">
              <thead className="bg-muted/30 font-medium text-muted-foreground border-b text-[11px]">
                <tr>
                  <th className="p-2.5">الاسم والبريد الإلكتروني</th>
                  <th className="p-2.5">المستوى الإداري</th>
                  <th className="p-2.5">آخر نشاط</th>
                  <th className="p-2.5 text-right rtl:text-left">الإجراء</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {adminsList.map((admin) => (
                  <tr key={admin.id} className="hover:bg-muted/40">
                    <td className="p-2.5">
                      <div className="font-bold text-foreground">{admin.name}</div>
                      <div className="text-[10px] text-muted-foreground font-mono">{admin.email}</div>
                    </td>
                    <td className="p-2.5"><Badge variant="default" className="text-[10px] bg-purple-600">{admin.role}</Badge></td>
                    <td className="p-2.5 text-muted-foreground text-[11px]">{admin.lastActive}</td>
                    <td className="p-2.5 text-right rtl:text-left">
                      <Button variant="ghost" size="sm" onClick={showToast} className="h-6.5 text-[11px] text-muted-foreground hover:text-foreground">
                        {locale === "ar" ? "إدارة الصلاحيات" : "Manage"}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Tab 6: Maintenance Mode */}
      {activeTab === "maintenance" && (
        <Card className="p-5 space-y-4 max-w-xl rounded-xl border bg-card">
          <div className="flex items-center justify-between border-b pb-3">
            <div>
              <h3 className="font-bold text-sm text-foreground">{locale === "ar" ? "التحكم في وضع الصيانة الطارئة" : "Emergency Maintenance Mode"}</h3>
              <p className="text-[11px] text-muted-foreground">{locale === "ar" ? "حظر مؤقت للعمليات غير الحرجة أثناء التحديثات الكبرى." : "Temporary lock for scheduled deployments."}</p>
            </div>
            <Badge variant={isMaintenanceActive ? "destructive" : "success"} className="text-xs px-2 py-0.5">
              {isMaintenanceActive ? "الصيانة مفعلة" : "المنصة متاحة"}
            </Badge>
          </div>

          <div className="space-y-1.5 text-xs">
            <label className="font-semibold text-foreground">رسالة التنبيه للمستخدمين</label>
            <Input
              value={maintenanceMessage}
              onChange={(e) => setMaintenanceMessage(e.target.value)}
              className="text-xs"
            />
          </div>

          <div className="flex justify-end pt-2 border-t">
            <Button
              variant={isMaintenanceActive ? "destructive" : "default"}
              onClick={() => { setIsMaintenanceActive(!isMaintenanceActive); showToast(); }}
              className="text-xs font-bold h-8.5"
            >
              {isMaintenanceActive ? "إيقاف وضع الصيانة وإتاحة الدخول" : "تفعيل وضع الصيانة الطارئة للمنصة"}
            </Button>
          </div>
        </Card>
      )}

      {/* Tab 7: Audit Log */}
      {activeTab === "audit" && (
        <Card className="rounded-xl border bg-card overflow-hidden">
          <CardHeader className="p-3 border-b bg-muted/20">
            <CardTitle className="text-xs font-bold">{locale === "ar" ? "سجل تدقيق عمليات الـ SuperAdmin (غير قابل للتعديل)" : "Immutable Platform Audit Trail"}</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-xs text-left rtl:text-right">
              <thead className="bg-muted/30 font-medium text-muted-foreground border-b text-[11px]">
                <tr>
                  <th className="p-2.5">الإجراء الإداري</th>
                  <th className="p-2.5">مشرف المنصة</th>
                  <th className="p-2.5">الهدف</th>
                  <th className="p-2.5">الوقت و IP</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                <tr className="hover:bg-muted/40">
                  <td className="p-2.5 font-bold text-foreground">TENANT_IMPERSONATION</td>
                  <td className="p-2.5 font-mono text-purple-600">platform_admin@pharmacloud.com</td>
                  <td className="p-2.5">سلسلة صيدليات الأمل (TNT-AMAL)</td>
                  <td className="p-2.5 font-mono text-muted-foreground text-[10px]">2026-08-21 21:50 • 127.0.0.1</td>
                </tr>
                <tr className="hover:bg-muted/40">
                  <td className="p-2.5 font-bold text-foreground">FLAG_TOGGLE_OCR</td>
                  <td className="p-2.5 font-mono text-purple-600">platform_admin@pharmacloud.com</td>
                  <td className="p-2.5">Global (All Tenants)</td>
                  <td className="p-2.5 font-mono text-muted-foreground text-[10px]">2026-08-21 18:10 • 192.168.1.10</td>
                </tr>
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Tab 8: Platform Settings */}
      {activeTab === "settings" && (
        <Card className="p-5 space-y-4 max-w-xl rounded-xl border bg-card">
          <div className="border-b pb-2">
            <h3 className="font-bold text-sm text-foreground">{locale === "ar" ? "إعدادات وهوية المنصة السحابية" : "Global Cloud Platform Configuration"}</h3>
          </div>

          <div className="space-y-3 text-xs">
            <div className="space-y-1">
              <label className="font-semibold text-foreground">اسم المنصة الرسمي</label>
              <Input
                value={platformSettings.platformName}
                onChange={(e) => setPlatformSettings({ ...platformSettings, platformName: e.target.value })}
                className="text-xs"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="font-semibold text-foreground">بريد الدعم الفني</label>
                <Input
                  value={platformSettings.supportEmail}
                  onChange={(e) => setPlatformSettings({ ...platformSettings, supportEmail: e.target.value })}
                  className="text-xs font-mono"
                />
              </div>
              <div className="space-y-1">
                <label className="font-semibold text-foreground">أيام التجربة المجانية (Trial)</label>
                <Input
                  value={platformSettings.trialDays}
                  onChange={(e) => setPlatformSettings({ ...platformSettings, trialDays: e.target.value })}
                  className="text-xs font-mono"
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-2 border-t">
            <Button onClick={showToast} className="gap-1.5 text-xs font-bold bg-purple-600 hover:bg-purple-700 h-8">
              <Save className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "حفظ الإعدادات" : "Save Changes"}</span>
            </Button>
          </div>
        </Card>
      )}

      {/* Tab 9: System Health Full */}
      {activeTab === "health" && (
        <Card className="p-5 space-y-4 rounded-xl border bg-card">
          <div className="flex items-center justify-between border-b pb-2">
            <h3 className="font-bold text-sm text-foreground">{locale === "ar" ? "مركز القياس والتشخيص السحابي" : "Telemetry Diagnostics"}</h3>
            <Button variant="outline" size="sm" onClick={handleRefreshDiagnostics} disabled={isDiagnosticsRefreshing} className="h-7 text-xs gap-1">
              <RefreshCw className={cn("h-3 w-3", isDiagnosticsRefreshing && "animate-spin")} />
              <span>{locale === "ar" ? "فحص وتحديث المؤشرات" : "Refresh Telemetry"}</span>
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="p-3 rounded-lg border bg-muted/20 space-y-1">
              <span className="font-bold text-foreground">معدل استجابة الـ API</span>
              <p className="text-lg font-mono font-extrabold text-emerald-600">32 ms (p95)</p>
              <span className="text-[10px] text-muted-foreground">متوسط 500,000 طلب / يوم</span>
            </div>
            <div className="p-3 rounded-lg border bg-muted/20 space-y-1">
              <span className="font-bold text-foreground">مساحة تخزين الوسائط (S3/MinIO)</span>
              <p className="text-lg font-mono font-extrabold text-foreground">14.8 GB / 100 GB</p>
              <span className="text-[10px] text-muted-foreground">نسخ احتياطي متعدد المناطق</span>
            </div>
            <div className="p-3 rounded-lg border bg-muted/20 space-y-1">
              <span className="font-bold text-foreground">استهلاك ذاكرة الخوادم</span>
              <p className="text-lg font-mono font-extrabold text-emerald-600">28.4%</p>
              <span className="text-[10px] text-muted-foreground">أداء مستقر وفائق السرعة</span>
            </div>
          </div>
        </Card>
      )}

      {/* Modal: Add New Tenant */}
      {isNewTenantModalOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="max-w-md w-full p-5 space-y-4 shadow-2xl border bg-card rounded-2xl animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-2">
              <div className="flex items-center gap-2">
                <Building2 className="h-5 w-5 text-purple-600" />
                <h3 className="font-bold text-sm text-foreground">
                  {locale === "ar" ? "إنشاء مستأجر / صيدلية جديدة" : "Provision New Pharmacy Tenant"}
                </h3>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsNewTenantModalOpen(false)} className="h-7 w-7">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <form onSubmit={handleCreateTenant} className="space-y-3 text-xs">
              <div className="space-y-1">
                <label className="font-semibold text-foreground">رمز المؤسسة (Tenant Code)</label>
                <Input
                  value={newTenantForm.code}
                  onChange={(e) => setNewTenantForm({ ...newTenantForm, code: e.target.value })}
                  placeholder="TNT-EXAMPLE"
                  className="font-mono text-xs"
                  required
                />
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-foreground">اسم الصيدلية أو المنشأة</label>
                <Input
                  value={newTenantForm.nameAr}
                  onChange={(e) => setNewTenantForm({ ...newTenantForm, nameAr: e.target.value })}
                  placeholder="مثال: صيدليات الحياة الحديثة"
                  className="text-xs"
                  required
                />
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-foreground">باقة الاشتراك السحابية</label>
                <select
                  value={newTenantForm.plan}
                  onChange={(e) => setNewTenantForm({ ...newTenantForm, plan: e.target.value })}
                  className="w-full h-8.5 rounded-md border border-input bg-background px-3 text-xs text-foreground focus:outline-none"
                >
                  <option value="Starter">Starter ($49/mo)</option>
                  <option value="Professional">Professional ($149/mo)</option>
                  <option value="Enterprise">Enterprise ($299/mo)</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsNewTenantModalOpen(false)} className="text-xs h-8">
                  {locale === "ar" ? "إلغاء" : "Cancel"}
                </Button>
                <Button type="submit" size="sm" className="text-xs font-bold bg-purple-600 hover:bg-purple-700 h-8">
                  {locale === "ar" ? "إنشاء وحفظ" : "Provision"}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}

      {/* Modal: Add New SuperAdmin */}
      {isNewAdminModalOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="max-w-md w-full p-5 space-y-4 shadow-2xl border bg-card rounded-2xl animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-2">
              <div className="flex items-center gap-2">
                <UserCheck className="h-5 w-5 text-purple-600" />
                <h3 className="font-bold text-sm text-foreground">
                  {locale === "ar" ? "دعوة مشرف منصة جديد (SuperAdmin)" : "Invite SuperAdmin"}
                </h3>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsNewAdminModalOpen(false)} className="h-7 w-7">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <form onSubmit={handleAddAdmin} className="space-y-3 text-xs">
              <div className="space-y-1">
                <label className="font-semibold text-foreground">البريد الإلكتروني للمشرف</label>
                <Input
                  type="email"
                  value={newAdminEmail}
                  onChange={(e) => setNewAdminEmail(e.target.value)}
                  placeholder="admin@pharmacloud.com"
                  className="font-mono text-xs"
                  required
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsNewAdminModalOpen(false)} className="text-xs h-8">
                  {locale === "ar" ? "إلغاء" : "Cancel"}
                </Button>
                <Button type="submit" size="sm" className="text-xs font-bold bg-purple-600 hover:bg-purple-700 h-8">
                  {locale === "ar" ? "إرسال الدعوة" : "Send Invite"}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
