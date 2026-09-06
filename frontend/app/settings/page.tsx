"use client";

import React, { useState } from "react";
import {
  Building2,
  GitBranch,
  Users,
  ShieldCheck,
  Receipt,
  Printer,
  Lock,
  History,
  Save,
  CheckCircle2,
  ShieldAlert,
  Plus,
  ToggleRight,
  FileCheck2,
  Award,
  Search,
  KeyRound,
  Check,
  Minus,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useI18n } from "@/lib/i18n";

type SettingsTab = "org" | "branches" | "staff" | "matrix" | "rules" | "invoicing" | "hardware" | "security" | "audit";

interface PharmacyStaffMember {
  id: string;
  name: string;
  nameAr: string;
  role: string;
  roleAr: string;
  email: string;
  licenseNumber: string;
  branch: string;
  branchAr: string;
  status: "active" | "inactive";
  mfaEnabled: boolean;
}

const initialStaff: PharmacyStaffMember[] = [
  { id: "1", name: "Dr. Ahmed Mansoor", nameAr: "د. أحمد منصور", role: "Supervising Pharmacist / Manager", roleAr: "صيدلي مشرف ومسؤول فرع", email: "ahmed.m@alamal-rx.com", licenseNumber: "PH-88912", branch: "Main Branch", branchAr: "الفرع الرئيسي", status: "active", mfaEnabled: true },
  { id: "2", name: "Sarah Al-Ghamdi", nameAr: "سارة الغامدي", role: "Licensed Clinical Pharmacist", roleAr: "صيدلانية إكلينيكية مرخصة", email: "sarah.g@alamal-rx.com", licenseNumber: "PH-91044", branch: "Main Branch", branchAr: "الفرع الرئيسي", status: "active", mfaEnabled: true },
  { id: "3", name: "Fahad Al-Harbi", nameAr: "فهد الحربي", role: "POS Cashier & Dispenser", roleAr: "أمين صندوق وصرف سريع", email: "fahad.h@alamal-rx.com", licenseNumber: "N/A", branch: "Branch #2 (Al-Malaz)", branchAr: "فرع 2 (الملز)", status: "active", mfaEnabled: false },
  { id: "4", name: "Tariq Salem", nameAr: "طارق سالم", role: "Inventory & Warehouse Officer", roleAr: "أمين ومراقب مستودع الأدوية", email: "tariq.s@alamal-rx.com", licenseNumber: "N/A", branch: "Central Warehouse", branchAr: "المستودع المركزي", status: "active", mfaEnabled: true },
];

const rbacMatrixData = [
  { module: "POS Terminal (Point of Sale)", moduleAr: "نقطة البيع والصرف السريع", admin: true, manager: true, pharmacist: true, cashier: true, inventory: false, accountant: false },
  { module: "Prescriptions & Clinical Verification", moduleAr: "الوصفات الطبية والتحقق السريري", admin: true, manager: true, pharmacist: true, cashier: false, inventory: false, accountant: false },
  { module: "Controlled Narcotics Tracking", moduleAr: "سجل الأدوية المراقبة والمخدرات", admin: true, manager: true, pharmacist: true, cashier: false, inventory: false, accountant: false },
  { module: "Inventory & Warehouse Movements", moduleAr: "المخزون وحركات المستودعات", admin: true, manager: true, pharmacist: true, cashier: false, inventory: true, accountant: false },
  { module: "Purchasing & Supplier POs", moduleAr: "أوامر الشراء وفواتير الموردين", admin: true, manager: true, pharmacist: false, cashier: false, inventory: true, accountant: false },
  { module: "Accounts Payable (AP)", moduleAr: "الذمم الدائنة وسندات الصرف", admin: true, manager: true, pharmacist: false, cashier: false, inventory: false, accountant: true },
  { module: "Accounts Receivable (AR)", moduleAr: "الذمم المدينة ومطالبات العيادات", admin: true, manager: true, pharmacist: false, cashier: false, inventory: false, accountant: true },
  { module: "General Ledger (GL Journals)", moduleAr: "دفتر الأستاذ والقيود المحاسبية", admin: true, manager: true, pharmacist: false, cashier: false, inventory: false, accountant: true },
  { module: "Cash Drawer Session Float", moduleAr: "إدارة ورديات الصندوق والعهدة", admin: true, manager: true, pharmacist: false, cashier: true, inventory: false, accountant: true },
  { module: "Staff & User RBAC Admin", moduleAr: "إدارة المستخدمين والصلاحيات", admin: true, manager: true, pharmacist: false, cashier: false, inventory: false, accountant: false },
  { module: "Fiscal & Pharmacy Settings", moduleAr: "الإعدادات العامة والضريبية", admin: true, manager: false, pharmacist: false, cashier: false, inventory: false, accountant: false },
];

export default function SettingsPage() {
  const { t, locale } = useI18n();
  const [activeTab, setActiveTab] = useState<SettingsTab>("org");
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);
  const [isSuccessToast, setIsSuccessToast] = useState(false);
  const [staff, setStaff] = useState<PharmacyStaffMember[]>(initialStaff);
  const [staffSearch, setStaffSearch] = useState("");
  const [isAddUserModalOpen, setIsAddUserModalOpen] = useState(false);

  // New User Form State
  const [newUserName, setNewUserName] = useState("");
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserRole, setNewUserRole] = useState("pharmacist");
  const [newUserBranch, setNewUserBranch] = useState("Main Branch");
  const [newUserLicense, setNewUserLicense] = useState("");

  // Form State
  const [legalName, setLegalName] = useState(locale === "ar" ? "سلسلة صيدليات الأمل الحديثة المحدودة" : "Al-Amal Modern Pharmacy Chain LLC");
  const [commercialName, setCommercialName] = useState(locale === "ar" ? "صيدليات الأمل" : "Al-Amal Pharmacies");
  const [crNumber, setCrNumber] = useState("1010889922");
  const [taxNumber, setTaxNumber] = useState("300998877600003");
  const [pharmacyLicense, setPharmacyLicense] = useState("MOH-RX-2026-991");
  const [currency, setCurrency] = useState("USD ($)");
  const [vatRate, setVatRate] = useState("5.0");
  const [invoicePrefix, setInvoicePrefix] = useState("INV");
  const [printerIp, setPrinterIp] = useState("192.168.1.220:9100");

  // Dispensing Rules State
  const [rules, setRules] = useState([
    { key: "STRICT_FEFO_DISPENSING", labelAr: "الإلزام بالصرف حسب الأقرب انتهاءً (Strict FEFO)", labelEn: "Enforce First-Expiry-First-Out (Strict FEFO)", enabled: true },
    { key: "NARCOTICS_DOUBLE_SIGNATURE", labelAr: "توقيع صيدليين اثنين لصرف الأدوية المراقبة (Narcotics)", labelEn: "Dual Pharmacist Sign-Off for Controlled Substances", enabled: true },
    { key: "BLOCK_EXPIRED_BATCH_SALE", labelAr: "حظر بيع أي تشغيلة منتهية الصلاحية تماماً", labelEn: "Strictly Block Sale of Expired Batches", enabled: true },
    { key: "ENFORCE_POS_MAX_DISCOUNT", labelAr: "تقييد الحد الأقصى لخصم الكاشير بنسبة 10%", labelEn: "Cap Cashier POS Discount to Maximum 10%", enabled: true },
    { key: "MANDATORY_FLOAT_ENTRY", labelAr: "إلزام الكاشير بتسجيل العهدة النقدية عند فتح الوردية", labelEn: "Mandatory Starting Float Entry on POS Shift Open", enabled: true },
  ]);

  const toggleRule = (key: string) => {
    setRules((prev) => prev.map((r) => (r.key === key ? { ...r, enabled: !r.enabled } : r)));
  };

  const handleSave = () => {
    setIsConfirmModalOpen(false);
    setIsSuccessToast(true);
    setTimeout(() => setIsSuccessToast(false), 2500);
  };

  const handleCreateUser = () => {
    if (!newUserName || !newUserEmail) return;
    const newMember: PharmacyStaffMember = {
      id: String(staff.length + 1),
      name: newUserName,
      nameAr: newUserName,
      role: newUserRole,
      roleAr: newUserRole === "pharmacist" ? "صيدلي إكلينيكي" : newUserRole === "cashier" ? "أمين صندوق" : "موظف صيدلية",
      email: newUserEmail,
      licenseNumber: newUserLicense || "N/A",
      branch: newUserBranch,
      branchAr: newUserBranch,
      status: "active",
      mfaEnabled: true,
    };
    setStaff((prev) => [...prev, newMember]);
    setIsAddUserModalOpen(false);
    setNewUserName("");
    setNewUserEmail("");
    setNewUserLicense("");
  };

  const filteredStaff = staff.filter(
    (s) =>
      s.name.toLowerCase().includes(staffSearch.toLowerCase()) ||
      s.nameAr.includes(staffSearch) ||
      s.email.toLowerCase().includes(staffSearch.toLowerCase()) ||
      s.licenseNumber.toLowerCase().includes(staffSearch.toLowerCase())
  );

  return (
    <div className="space-y-6 font-sans">
      {/* Header & Pharmacy Admin Identity Badge */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="default" className="bg-emerald-600 hover:bg-emerald-700 text-[11px] gap-1 px-2.5 py-0.5">
              <Building2 className="h-3.5 w-3.5" />
              <span>{t("settings.admin_badge")}</span>
            </Badge>
            <Badge variant="outline" className="text-[10px] text-muted-foreground">
              {locale === "ar" ? "نطاق المؤسسة المستأجرة (Tenant-Level)" : "Tenant-Level Scope"}
            </Badge>
          </div>
          <h1 className="text-2xl font-bold tracking-tight">{t("settings.title")}</h1>
          <p className="text-sm text-muted-foreground">{t("settings.subtitle")}</p>
        </div>
      </div>

      {isSuccessToast && (
        <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 text-xs flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4" />
          <span>{locale === "ar" ? "تم حفظ وتحديث إعدادات المنشأة الصيدلانية بنجاح." : "Pharmacy organization settings saved successfully."}</span>
        </div>
      )}

      {/* Navigation Sub-Tabs */}
      <div className="flex flex-wrap items-center gap-1.5 p-1.5 bg-muted/40 rounded-xl border text-xs">
        <Button variant={activeTab === "org" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("org")} className="h-8 gap-1.5">
          <Building2 className="h-3.5 w-3.5" /> {t("settings.tab_org")}
        </Button>
        <Button variant={activeTab === "branches" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("branches")} className="h-8 gap-1.5">
          <GitBranch className="h-3.5 w-3.5" /> {t("settings.tab_branches")}
        </Button>
        <Button variant={activeTab === "staff" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("staff")} className="h-8 gap-1.5">
          <Users className="h-3.5 w-3.5" /> {t("settings.tab_staff")}
        </Button>
        <Button variant={activeTab === "matrix" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("matrix")} className="h-8 gap-1.5">
          <KeyRound className="h-3.5 w-3.5" /> {t("settings.tab_matrix")}
        </Button>
        <Button variant={activeTab === "rules" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("rules")} className="h-8 gap-1.5">
          <FileCheck2 className="h-3.5 w-3.5" /> {t("settings.tab_rules")}
        </Button>
        <Button variant={activeTab === "invoicing" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("invoicing")} className="h-8 gap-1.5">
          <Receipt className="h-3.5 w-3.5" /> {t("settings.tab_invoicing")}
        </Button>
        <Button variant={activeTab === "hardware" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("hardware")} className="h-8 gap-1.5">
          <Printer className="h-3.5 w-3.5" /> {t("settings.tab_hardware")}
        </Button>
        <Button variant={activeTab === "security" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("security")} className="h-8 gap-1.5">
          <Lock className="h-3.5 w-3.5" /> {t("settings.tab_security")}
        </Button>
        <Button variant={activeTab === "audit" ? "default" : "ghost"} size="sm" onClick={() => setActiveTab("audit")} className="h-8 gap-1.5">
          <History className="h-3.5 w-3.5" /> {t("settings.tab_audit")}
        </Button>
      </div>

      {/* Tab: Organization Profile */}
      {activeTab === "org" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("settings.company_info")}</CardTitle>
              <CardDescription>{locale === "ar" ? "البيانات القانونية المعتمدة لدى وزارة الصحة والجهات الضريبية." : "Official legal identity printed on tax invoices and receipts."}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="font-medium text-foreground">{t("settings.org_name")}</label>
                <Input value={legalName} onChange={(e) => setLegalName(e.target.value)} />
              </div>
              <div className="space-y-1">
                <label className="font-medium text-foreground">{locale === "ar" ? "الاسم التجاري للصيدلية" : "Commercial Brand Name"}</label>
                <Input value={commercialName} onChange={(e) => setCommercialName(e.target.value)} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-medium text-foreground">{t("settings.cr_number")}</label>
                  <Input value={crNumber} onChange={(e) => setCrNumber(e.target.value)} className="font-mono" />
                </div>
                <div className="space-y-1">
                  <label className="font-medium text-foreground">{t("settings.tax_number")}</label>
                  <Input value={taxNumber} onChange={(e) => setTaxNumber(e.target.value)} className="font-mono" />
                </div>
              </div>
              <div className="space-y-1">
                <label className="font-medium text-foreground">{t("settings.license_number")}</label>
                <Input value={pharmacyLicense} onChange={(e) => setPharmacyLicense(e.target.value)} className="font-mono" />
              </div>
              <div className="space-y-1">
                <label className="font-medium text-foreground">{t("settings.currency")}</label>
                <Input value={currency} onChange={(e) => setCurrency(e.target.value)} />
              </div>
            </CardContent>
            <CardFooter className="border-t pt-4 flex justify-end">
              <Button onClick={() => setIsConfirmModalOpen(true)} className="gap-1.5 text-xs">
                <Save className="h-3.5 w-3.5" />
                <span>{t("settings.save_btn")}</span>
              </Button>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{locale === "ar" ? "شعار وهوية الفواتير" : "Pharmacy Branding & Logo"}</CardTitle>
              <CardDescription>{locale === "ar" ? "الشعار الرسمي المطبوع أعلى الفواتير الحرارية والتقارير المالية." : "Branding rendered at the top of thermal POS receipts."}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-xs">
              <div className="border-2 border-dashed rounded-xl p-6 text-center space-y-2 bg-muted/20">
                <Award className="h-10 w-10 text-emerald-600 mx-auto" />
                <p className="font-bold text-foreground">{locale === "ar" ? "شعار صيدلية الأمل الحديثة" : "Al-Amal Modern Pharmacy Logo"}</p>
                <p className="text-muted-foreground text-[11px]">PNG, SVG, or JPG up to 2MB (200x200px recommended)</p>
                <Button variant="outline" size="sm" className="text-xs">
                  {locale === "ar" ? "تحديث الشعار" : "Upload New Logo"}
                </Button>
              </div>

              <div className="p-3 rounded-lg border bg-muted/10 space-y-1">
                <span className="font-semibold text-foreground">{locale === "ar" ? "العنوان الرسمي:" : "Official Registered Address:"}</span>
                <p className="text-muted-foreground text-[11px]">{locale === "ar" ? "شارع الملك عبدالعزيز، مبنى الأمل الطبي، الرياض، المملكة العربية السعودية" : "King Abdulaziz Road, Al-Amal Medical Tower, Riyadh, KSA"}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tab: Branches */}
      {activeTab === "branches" && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between border-b pb-3">
            <div>
              <CardTitle>{t("settings.tab_branches")}</CardTitle>
              <CardDescription>{locale === "ar" ? "شبكة فروع الصيدلية، المستودعات، ونقاط الصرف التابعة للمنشأة." : "Branch locations, cold-chain storage zones, and active registers."}</CardDescription>
            </div>
            <Button size="sm" className="gap-1.5 text-xs">
              <Plus className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "إضافة فرع جديد" : "Add Branch"}</span>
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-xs text-left rtl:text-right">
              <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
                <tr>
                  <th className="p-3">اسم الفرع</th>
                  <th className="p-3">المدينة / الحي</th>
                  <th className="p-3">مدير الفرع المشرف</th>
                  <th className="p-3">صناديق POS</th>
                  <th className="p-3">الحالة</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                <tr className="hover:bg-muted/50">
                  <td className="p-3 font-semibold text-foreground">الفرع الرئيسي - صيدلية الأمل</td>
                  <td className="p-3">الرياض - العليا</td>
                  <td className="p-3 font-mono">د. أحمد منصور (PH-88912)</td>
                  <td className="p-3 font-mono">3 صناديق نشطة</td>
                  <td className="p-3"><Badge variant="success">نشط</Badge></td>
                </tr>
                <tr className="hover:bg-muted/50">
                  <td className="p-3 font-semibold text-foreground">فرع 2 - حي الملز</td>
                  <td className="p-3">الرياض - الملز</td>
                  <td className="p-3 font-mono">د. سارة الغامدي (PH-91044)</td>
                  <td className="p-3 font-mono">2 صناديق نشطة</td>
                  <td className="p-3"><Badge variant="success">نشط</Badge></td>
                </tr>
                <tr className="hover:bg-muted/50">
                  <td className="p-3 font-semibold text-foreground">المستودع المركزي وسلسلة التبريد</td>
                  <td className="p-3">الرياض - السلي</td>
                  <td className="p-3 font-mono">طارق سالم (مراقب المستودع)</td>
                  <td className="p-3 font-mono">مستودع جملة / لوجستي</td>
                  <td className="p-3"><Badge variant="success">نشط</Badge></td>
                </tr>
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Tab: Staff Management */}
      {activeTab === "staff" && (
        <Card>
          <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-3">
            <div className="relative w-full sm:w-80">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-3 pointer-events-none" />
              <Input
                placeholder={locale === "ar" ? "بحث بالاسم، البريد، أو رقم الترخيص..." : "Search name, email, license #..."}
                value={staffSearch}
                onChange={(e) => setStaffSearch(e.target.value)}
                className="pl-9 text-xs rtl:pl-3 rtl:pr-9"
              />
            </div>
            <Button size="sm" onClick={() => setIsAddUserModalOpen(true)} className="gap-1.5 text-xs">
              <Plus className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "إضافة صيدلي / مستخدم" : "Add Staff User"}</span>
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-xs text-left rtl:text-right">
              <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
                <tr>
                  <th className="p-3">الاسم والبريد الإلكتروني</th>
                  <th className="p-3">الدور والمسؤولية</th>
                  <th className="p-3">ترخيص مزاولة المهنة</th>
                  <th className="p-3">نطاق الفرع المخصص</th>
                  <th className="p-3">التحقق MFA</th>
                  <th className="p-3">الحالة</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredStaff.map((member) => (
                  <tr key={member.id} className="hover:bg-muted/50">
                    <td className="p-3">
                      <div className="font-semibold text-foreground">{locale === "ar" ? member.nameAr : member.name}</div>
                      <div className="text-[11px] text-muted-foreground font-mono">{member.email}</div>
                    </td>
                    <td className="p-3 text-muted-foreground">{locale === "ar" ? member.roleAr : member.role}</td>
                    <td className="p-3 font-mono">{member.licenseNumber}</td>
                    <td className="p-3">{locale === "ar" ? member.branchAr : member.branch}</td>
                    <td className="p-3">
                      <Badge variant={member.mfaEnabled ? "success" : "outline"} className="text-[10px]">
                        {member.mfaEnabled ? "مفعل (OTP)" : "غير مفعل"}
                      </Badge>
                    </td>
                    <td className="p-3"><Badge variant="success">نشط</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Tab: Role-Permission Matrix (RBAC Matrix) */}
      {activeTab === "matrix" && (
        <Card>
          <CardHeader className="border-b pb-3">
            <CardTitle>{t("settings.tab_matrix")}</CardTitle>
            <CardDescription>
              {locale === "ar"
                ? "جدول مصفوفة الصلاحيات الحبيبية (Granular Permissions) الموزعة على الأدوار الوظيفية داخل الصيدلية."
                : "Authoritative granular RBAC permission matrix across operational pharmacy roles."}
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0 overflow-x-auto">
            <table className="w-full text-xs text-left rtl:text-right border-collapse">
              <thead className="bg-muted/50 font-medium text-muted-foreground border-b">
                <tr>
                  <th className="p-3 text-foreground font-bold">الوحدة / الوظيفة (Module / Action)</th>
                  <th className="p-3 text-center">المالك (Admin)</th>
                  <th className="p-3 text-center">مدير الفرع</th>
                  <th className="p-3 text-center">صيدلي مرخص</th>
                  <th className="p-3 text-center">أمين الصندوق</th>
                  <th className="p-3 text-center">أمين المستودع</th>
                  <th className="p-3 text-center">المحاسب المالي</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {rbacMatrixData.map((row, idx) => (
                  <tr key={idx} className="hover:bg-muted/40">
                    <td className="p-3 font-semibold text-foreground">
                      {locale === "ar" ? row.moduleAr : row.module}
                    </td>
                    <td className="p-3 text-center">{row.admin ? <Check className="h-4 w-4 text-emerald-600 mx-auto" /> : <Minus className="h-4 w-4 text-muted-foreground/40 mx-auto" />}</td>
                    <td className="p-3 text-center">{row.manager ? <Check className="h-4 w-4 text-emerald-600 mx-auto" /> : <Minus className="h-4 w-4 text-muted-foreground/40 mx-auto" />}</td>
                    <td className="p-3 text-center">{row.pharmacist ? <Check className="h-4 w-4 text-emerald-600 mx-auto" /> : <Minus className="h-4 w-4 text-muted-foreground/40 mx-auto" />}</td>
                    <td className="p-3 text-center">{row.cashier ? <Check className="h-4 w-4 text-emerald-600 mx-auto" /> : <Minus className="h-4 w-4 text-muted-foreground/40 mx-auto" />}</td>
                    <td className="p-3 text-center">{row.inventory ? <Check className="h-4 w-4 text-emerald-600 mx-auto" /> : <Minus className="h-4 w-4 text-muted-foreground/40 mx-auto" />}</td>
                    <td className="p-3 text-center">{row.accountant ? <Check className="h-4 w-4 text-emerald-600 mx-auto" /> : <Minus className="h-4 w-4 text-muted-foreground/40 mx-auto" />}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Tab: Rules */}
      {activeTab === "rules" && (
        <Card className="max-w-3xl">
          <CardHeader className="border-b pb-3">
            <CardTitle>{t("settings.tab_rules")}</CardTitle>
            <CardDescription>{locale === "ar" ? "ضوابط الصرف السريري، أمان الأدوية المخدرة، وسياسات المخزون المزدوج." : "Clinical safety ceiling, strict FEFO dispatch, and cashier discount limits."}</CardDescription>
          </CardHeader>
          <CardContent className="p-4 space-y-3 divide-y">
            {rules.map((rule) => (
              <div key={rule.key} className="pt-3 first:pt-0 flex items-center justify-between text-xs">
                <div>
                  <p className="font-bold text-foreground">{locale === "ar" ? rule.labelAr : rule.labelEn}</p>
                  <p className="text-muted-foreground text-[11px] font-mono mt-0.5">{rule.key}</p>
                </div>
                <Button
                  variant={rule.enabled ? "default" : "outline"}
                  size="sm"
                  onClick={() => toggleRule(rule.key)}
                  className={`h-7 text-xs ${rule.enabled ? "bg-emerald-600 hover:bg-emerald-700" : ""}`}
                >
                  <ToggleRight className="h-3.5 w-3.5 mr-1" />
                  <span>{rule.enabled ? (locale === "ar" ? "مفعل" : "Enabled") : (locale === "ar" ? "معطل" : "Disabled")}</span>
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Tab: Invoicing */}
      {activeTab === "invoicing" && (
        <Card className="max-w-2xl">
          <CardHeader className="border-b pb-3">
            <CardTitle>{t("settings.tab_invoicing")}</CardTitle>
            <CardDescription>{locale === "ar" ? "الضرائب وتنسيق الفواتير الضريبية المبسطة المتوافقة مع متطلبات ZATCA." : "Tax rates, simplified tax invoice formats, and QR code embedding."}</CardDescription>
          </CardHeader>
          <CardContent className="p-6 space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="font-medium text-foreground">نسبة ضريبة القيمة المضافة (VAT %)</label>
                <Input value={vatRate} onChange={(e) => setVatRate(e.target.value)} className="font-mono" />
              </div>
              <div className="space-y-1">
                <label className="font-medium text-foreground">بادئة ترقيم الفواتير (Prefix)</label>
                <Input value={invoicePrefix} onChange={(e) => setInvoicePrefix(e.target.value)} className="font-mono" />
              </div>
            </div>

            <div className="space-y-1 pt-2">
              <label className="font-medium text-foreground">رسالة أسفل الفاتورة الحرارية (Receipt Footer Note)</label>
              <Input defaultValue="شكراً لثقتكم بصيدليات الأمل — صحتك هي أولويتنا" />
            </div>

            <div className="p-3 rounded-lg border bg-emerald-500/10 text-emerald-600 text-[11px] flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 shrink-0" />
              <span>{locale === "ar" ? "الفواتير متوافقة تلقائياً مع متطلبات الفوترة الإلكترونية ورمز الاستجابة السريع (QR Code)." : "Invoices include encrypted TLV Base64 QR code compliant with e-invoicing standards."}</span>
            </div>
          </CardContent>
          <CardFooter className="border-t pt-4 flex justify-end">
            <Button onClick={() => setIsConfirmModalOpen(true)} className="gap-1.5 text-xs">
              <Save className="h-3.5 w-3.5" />
              <span>{t("settings.save_btn")}</span>
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Tab: Hardware */}
      {activeTab === "hardware" && (
        <Card className="max-w-2xl">
          <CardHeader className="border-b pb-3">
            <CardTitle>{t("settings.tab_hardware")}</CardTitle>
            <CardDescription>{locale === "ar" ? "ربط طابعات الإيصالات الحرارية، وماسحات الباركود السلكية واللاسلكية." : "Network thermal receipt printers and barcode scanner hardware."}</CardDescription>
          </CardHeader>
          <CardContent className="p-6 space-y-4 text-xs">
            <div className="space-y-1">
              <label className="font-medium text-foreground">عنوان IP طابعة الفواتير الحرارية (ESC/POS)</label>
              <Input value={printerIp} onChange={(e) => setPrinterIp(e.target.value)} className="font-mono" />
            </div>

            <div className="p-3 rounded-lg border bg-muted/20 flex items-center justify-between">
              <div>
                <p className="font-semibold">ماسح الباركود السريع (USB / Bluetooth HID)</p>
                <p className="text-[11px] text-muted-foreground">التعرف التلقائي على معايير GS1-DataMatrix و EAN-13</p>
              </div>
              <Badge variant="success">متصل ومفعل</Badge>
            </div>
          </CardContent>
          <CardFooter className="border-t pt-4 flex justify-end">
            <Button onClick={() => setIsConfirmModalOpen(true)} className="gap-1.5 text-xs">
              <Save className="h-3.5 w-3.5" />
              <span>{t("settings.save_btn")}</span>
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Tab: Security */}
      {activeTab === "security" && (
        <Card className="max-w-2xl">
          <CardHeader className="border-b pb-3">
            <CardTitle>{t("settings.security_policies")}</CardTitle>
            <CardDescription>{locale === "ar" ? "قواعد تسجيل الدخول وسياسات انتهاء الجلسات داخل الصيدلية." : "Session timeout rules and enterprise tenant policies."}</CardDescription>
          </CardHeader>
          <CardContent className="p-6 space-y-3 text-xs">
            <div className="p-3 rounded-lg border bg-muted/20 flex items-center justify-between">
              <div>
                <p className="font-semibold">{locale === "ar" ? "التحقق الثنائي الإلزامي (MFA)" : "Enforce Multi-Factor Authentication"}</p>
                <p className="text-[11px] text-muted-foreground">{locale === "ar" ? "إلزام الصيادلة والمحاسبين برمز OTP" : "Mandatory for pharmacists and accountants"}</p>
              </div>
              <span className="text-emerald-600 font-bold">{locale === "ar" ? "مفعل" : "Enabled"}</span>
            </div>

            <div className="p-3 rounded-lg border bg-muted/20 flex items-center justify-between">
              <div>
                <p className="font-semibold">{locale === "ar" ? "مهلة انتهاء الجلسة التلقائي" : "Automatic Session Inactivity Timeout"}</p>
                <p className="text-[11px] text-muted-foreground">{locale === "ar" ? "قفل شاشة نقطة البيع بعد 15 دقيقة خمول" : "Lock POS screen after 15 mins of idle time"}</p>
              </div>
              <span className="font-mono font-bold">15 {locale === "ar" ? "دقيقة" : "mins"}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab: Audit */}
      {activeTab === "audit" && (
        <Card>
          <CardHeader className="border-b pb-3">
            <CardTitle>{t("settings.tab_audit")}</CardTitle>
            <CardDescription>{locale === "ar" ? "سجل الإجراءات التشغيلية والتعديلات المنفذة داخل نطاق صيدلية الأمل." : "Tenant-scoped activity and audit log."}</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-xs text-left rtl:text-right">
              <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
                <tr>
                  <th className="p-3">الإجراء</th>
                  <th className="p-3">المستخدم / الصيدلي</th>
                  <th className="p-3">التفاصيل والبيان</th>
                  <th className="p-3">الوقت</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                <tr className="hover:bg-muted/50">
                  <td className="p-3 font-semibold">BRANCH_UPDATED</td>
                  <td className="p-3 font-mono">ahmed.m@alamal-rx.com</td>
                  <td className="p-3">تحديث بيانات صندوق الكاشير في الفرع الرئيسي</td>
                  <td className="p-3 font-mono text-muted-foreground">2026-08-16 00:05</td>
                </tr>
                <tr className="hover:bg-muted/50">
                  <td className="p-3 font-semibold">DISPENSING_RULE_TOGGLE</td>
                  <td className="p-3 font-mono">ahmed.m@alamal-rx.com</td>
                  <td className="p-3">تأكيد تفعيل سياسة FEFO الصارمة لصرف الأدوية</td>
                  <td className="p-3 font-mono text-muted-foreground">2026-08-15 19:30</td>
                </tr>
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Add Staff User Modal */}
      {isAddUserModalOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="max-w-md w-full p-6 space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-primary/10 text-primary">
                <Users className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-foreground">
                  {locale === "ar" ? "إضافة صيدلي / مستخدم جديد" : "Provision New Pharmacy Staff User"}
                </h3>
                <p className="text-xs text-muted-foreground">
                  {locale === "ar" ? "تعيين الصلاحيات والنطاق الجغرافي للفرع." : "Assign role permissions and branch data scope."}
                </p>
              </div>
            </div>

            <div className="space-y-3 py-2 text-xs">
              <div className="space-y-1">
                <label className="font-semibold text-foreground">{locale === "ar" ? "الاسم الكامل" : "Full Name"}</label>
                <Input value={newUserName} onChange={(e) => setNewUserName(e.target.value)} placeholder="Dr. Sarah Al-Ali" />
              </div>
              <div className="space-y-1">
                <label className="font-semibold text-foreground">{locale === "ar" ? "البريد الإلكتروني" : "Email Address"}</label>
                <Input value={newUserEmail} onChange={(e) => setNewUserEmail(e.target.value)} placeholder="sarah.ali@alamal-rx.com" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <label className="font-semibold text-foreground">{locale === "ar" ? "الدور الوظيفي" : "Role"}</label>
                  <select
                    value={newUserRole}
                    onChange={(e) => setNewUserRole(e.target.value)}
                    className="w-full h-9 rounded-md border border-input bg-background px-3 text-xs"
                  >
                    <option value="pharmacist">{locale === "ar" ? "صيدلي مرخص" : "Licensed Pharmacist"}</option>
                    <option value="cashier">{locale === "ar" ? "أمين صندوق" : "POS Cashier"}</option>
                    <option value="inventory_manager">{locale === "ar" ? "أمين مستودع" : "Inventory Manager"}</option>
                    <option value="accountant">{locale === "ar" ? "محاسب مالي" : "Accountant"}</option>
                    <option value="branch_manager">{locale === "ar" ? "مدير فرع" : "Branch Manager"}</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="font-semibold text-foreground">{locale === "ar" ? "نطاق الفرع" : "Branch Scope"}</label>
                  <select
                    value={newUserBranch}
                    onChange={(e) => setNewUserBranch(e.target.value)}
                    className="w-full h-9 rounded-md border border-input bg-background px-3 text-xs"
                  >
                    <option value="Main Branch">{locale === "ar" ? "الفرع الرئيسي" : "Main Branch"}</option>
                    <option value="Branch #2 (Al-Malaz)">{locale === "ar" ? "فرع 2 (الملز)" : "Branch #2 (Al-Malaz)"}</option>
                    <option value="Central Warehouse">{locale === "ar" ? "المستودع المركزي" : "Central Warehouse"}</option>
                  </select>
                </div>
              </div>
              <div className="space-y-1">
                <label className="font-semibold text-foreground">{locale === "ar" ? "رقم ترخيص مزاولة المهنة" : "Professional License #"}</label>
                <Input value={newUserLicense} onChange={(e) => setNewUserLicense(e.target.value)} placeholder="PH-99214" className="font-mono" />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t">
              <Button variant="outline" size="sm" onClick={() => setIsAddUserModalOpen(false)}>
                {locale === "ar" ? "إلغاء" : "Cancel"}
              </Button>
              <Button size="sm" onClick={handleCreateUser}>
                <Plus className="h-4 w-4 mr-1.5" />
                {locale === "ar" ? "حفظ وتفعيل الحساب" : "Create User"}
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Two-Step Confirmation Modal */}
      {isConfirmModalOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="max-w-md w-full p-6 space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-amber-500/10 text-amber-600">
                <ShieldAlert className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-foreground">
                  {locale === "ar" ? "تأكيد تحديث بيانات المنشأة الصيدلانية" : "Confirm Pharmacy Settings Update"}
                </h3>
                <p className="text-xs text-muted-foreground">
                  {locale === "ar" ? "سيتم تطبيق التغييرات على الفواتير الضريبية وسندات الصرف القادمة عبر كافة الفروع." : "Changes will take effect on future invoices and receipts across all pharmacy branches."}
                </p>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t">
              <Button variant="outline" size="sm" onClick={() => setIsConfirmModalOpen(false)}>
                {locale === "ar" ? "إلغاء" : "Cancel"}
              </Button>
              <Button size="sm" onClick={handleSave}>
                <CheckCircle2 className="h-4 w-4 mr-1.5" />
                {locale === "ar" ? "تأكيد وحفظ" : "Confirm & Save"}
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
