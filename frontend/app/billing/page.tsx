"use client";

import React, { useState } from "react";
import {
  Check,
  CreditCard,
  ShieldCheck,
  Zap,
  Download,
  Calendar,
  Building2,
  Users,
  CheckCircle2,
  X,
  Plus,
  ArrowRight,
  Printer,
  Sparkles,
  Layers,
  FileText,
  AlertCircle,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useI18n } from "@/lib/i18n";
import { formatCurrency } from "@/lib/utils";

interface BillingPlan {
  id: string;
  nameAr: string;
  nameEn: string;
  priceMonthly: number;
  branchesQuota: number;
  usersQuota: number;
  features: string[];
}

const availablePlans: BillingPlan[] = [
  {
    id: "starter",
    nameAr: "الباقة الأساسية (Starter)",
    nameEn: "Starter Plan",
    priceMonthly: 49.0,
    branchesQuota: 1,
    usersQuota: 3,
    features: ["نقطة بيع واحدة (POS)", "إدارة المخزون الأساسية", "نسخ احتياطي أسبوعي"],
  },
  {
    id: "pro",
    nameAr: "الباقة المتقدمة (Professional)",
    nameEn: "Professional Plan",
    priceMonthly: 149.0,
    branchesQuota: 3,
    usersQuota: 10,
    features: ["3 نقاط بيع متزامنة", "دفتر الأستاذ والمالية", "تتبع تواريخ الصلاحية FEFO", "دعم فني على مدار الساعة"],
  },
  {
    id: "enterprise",
    nameAr: "باقة سلاسل الصيدليات المتكاملة (Enterprise)",
    nameEn: "Enterprise Chain Plan",
    priceMonthly: 299.0,
    branchesQuota: 10,
    usersQuota: 25,
    features: ["نقاط بيع متزامنة لكافة الفروع", "محرك القيود ودفتر الأستاذ المزدوج", "المتجر الإلكتروني وتطبيق الجوال", "النسخ الاحتياطي التلقائي اللحظي"],
  },
  {
    id: "ultimate",
    nameAr: "باقة المؤسسات الكبرى (Ultimate)",
    nameEn: "Ultimate Enterprise",
    priceMonthly: 499.0,
    branchesQuota: 25,
    usersQuota: 100,
    features: ["فروع ومستخدمين غير محدودين", "خادم سحابي مخصص", "ربط API مخصص للمستشفيات", "مدير حساب تنفيذي خاص"],
  },
];

interface AddonItem {
  id: string;
  nameAr: string;
  priceMonthly: number;
  enabled: boolean;
  desc: string;
}

const initialAddons: AddonItem[] = [
  { id: "sms", nameAr: "خدمة إشعارات الرسائل القصيرة والواتساب (SMS & WhatsApp)", priceMonthly: 19.0, enabled: true, desc: "إرسال رسائل التنبيه بمواعيد صرف الأدوية والفواتير الإلكترونية للعملاء" },
  { id: "ai_ocr", nameAr: "المساعد الذكي لفحص وقراءة الوصفات الطبية (AI OCR)", priceMonthly: 39.0, enabled: true, desc: "التعرف البصري الآلي على خط يد الطبيب في الروشتات مع فحص التعارضات" },
  { id: "ecom", nameAr: "بوابة المتجر الإلكتروني وتطبيقات التوصيل (E-Commerce B2C)", priceMonthly: 49.0, enabled: true, desc: "استقبال طلبات المرضى أونلاين والدفع الإلكتروني عبر أبل باي وفيزا ومدى" },
  { id: "branches_pack", nameAr: "حزمة فروع إضافية (+3 فروع صيدلية)", priceMonthly: 35.0, enabled: false, desc: "توسيع حصة الفروع المرخصة بالسلسلة" },
];

const mockBillingInvoices = [
  { id: "INV-SaaS-2026-08", date: "2026-08-15", desc: "اشتراك باقة Enterprise (أغسطس 2026) + خدمات إضافية", amount: 357.0, status: "paid" },
  { id: "INV-SaaS-2026-07", date: "2026-07-15", desc: "اشتراك باقة Enterprise (يوليو 2026)", amount: 299.0, status: "paid" },
  { id: "INV-SaaS-2026-06", date: "2026-06-15", desc: "اشتراك باقة Enterprise (يونيو 2026)", amount: 299.0, status: "paid" },
];

export default function BillingPage() {
  const { t, locale } = useI18n();
  const [currentPlan, setCurrentPlan] = useState<BillingPlan>(availablePlans[2]);
  const [addons, setAddons] = useState<AddonItem[]>(initialAddons);
  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState(false);
  const [isAddonsModalOpen, setIsAddonsModalOpen] = useState(false);
  const [isCardModalOpen, setIsCardModalOpen] = useState(false);
  const [selectedInvoiceToView, setSelectedInvoiceToView] = useState<any | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Payment Card state
  const [cardLast4, setCardLast4] = useState("4242");
  const [cardExp, setCardExp] = useState("09/28");

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 2500);
  };

  const handleSelectPlan = (plan: BillingPlan) => {
    setCurrentPlan(plan);
    setIsUpgradeModalOpen(false);
    showToast(locale === "ar" ? `تم ترقية اشتراك المنشأة إلى ${plan.nameAr} بنجاح` : `Plan updated to ${plan.nameEn}`);
  };

  const toggleAddon = (id: string) => {
    setAddons((prev) =>
      prev.map((a) => (a.id === id ? { ...a, enabled: !a.enabled } : a))
    );
    showToast(locale === "ar" ? "تم تحديث الخدمات الإضافية للاشتراك" : "Add-on preferences saved");
  };

  const activeAddonsCost = addons.filter((a) => a.enabled).reduce((acc, a) => acc + a.priceMonthly, 0);
  const totalMonthlyBilling = currentPlan.priceMonthly + activeAddonsCost;

  return (
    <div className="space-y-4 font-sans antialiased text-foreground">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-4 end-4 z-50 bg-emerald-600 text-white px-4 py-2.5 rounded-xl shadow-2xl text-xs font-bold flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
          <CheckCircle2 className="h-4 w-4" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-primary/10 text-primary shrink-0">
            <CreditCard className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-foreground">{locale === "ar" ? "الاشتراكات وتراخيص المنصة السحابية" : "SaaS Subscriptions & Licenses"}</h1>
            <p className="text-[11px] text-muted-foreground">{locale === "ar" ? "إدارة خطة الصيدلية، حصص الفروع والمستخدمين، وفواتير الاشتراك السحابي" : "Manage subscription plan, branch quotas & SaaS billing"}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setIsCardModalOpen(true)} className="gap-1.5 text-xs font-semibold h-8 border-border">
            <CreditCard className="h-3.5 w-3.5" />
            <span>بطاقة الدفع (••• {cardLast4})</span>
          </Button>

          <Button size="sm" onClick={() => setIsUpgradeModalOpen(true)} className="gap-1.5 text-xs bg-primary hover:bg-primary/90 font-bold h-8 shadow-sm text-white">
            <Sparkles className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "ترقية الباقة" : "Upgrade Plan"}</span>
          </Button>
        </div>
      </div>

      {/* Main Billing Plan Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Current Active Plan (Left 2 Cols) */}
        <Card className="p-5 lg:col-span-2 space-y-4 rounded-xl border bg-card shadow-sm">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">{locale === "ar" ? "الباقة الحالية المفعلة" : "Current Plan"}</span>
              <h2 className="text-lg font-extrabold text-foreground">{currentPlan.nameAr}</h2>
              <p className="text-[11px] text-muted-foreground">صيدليات الأمل الحديثة المحدودة (مستأجر TNT-AMAL)</p>
            </div>
            <Badge variant="success" className="text-xs px-2.5 py-0.5">
              {locale === "ar" ? "اشتراك نشط ومحدث" : "Active Subscription"}
            </Badge>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 py-3 border-y text-xs">
            <div className="space-y-1">
              <span className="text-muted-foreground text-[11px]">الاشتراك الشهري</span>
              <p className="font-extrabold text-emerald-600 text-base font-mono">{formatCurrency(totalMonthlyBilling)} / {locale === "ar" ? "شهر" : "mo"}</p>
            </div>
            <div className="space-y-1">
              <span className="text-muted-foreground text-[11px]">الفروع المتاحة</span>
              <p className="font-bold text-foreground font-mono text-sm">5 / {currentPlan.branchesQuota} فروع</p>
            </div>
            <div className="space-y-1">
              <span className="text-muted-foreground text-[11px]">المستخدمين المرخصين</span>
              <p className="font-bold text-foreground font-mono text-sm">18 / {currentPlan.usersQuota} مستخدم</p>
            </div>
            <div className="space-y-1">
              <span className="text-muted-foreground text-[11px]">تاريخ التجديد القادم</span>
              <p className="font-bold text-foreground font-mono text-xs">2026-09-15</p>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-1">
            <Button variant="outline" size="sm" onClick={() => setIsUpgradeModalOpen(true)} className="text-xs h-8 font-semibold">
              {locale === "ar" ? "تغيير الباقة" : "Change Plan"}
            </Button>
            <Button size="sm" onClick={() => setIsAddonsModalOpen(true)} className="text-xs font-bold gap-1.5 h-8 bg-blue-600 hover:bg-blue-700 text-white">
              <Zap className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "إدارة الخدمات الإضافية والحصص" : "Manage Add-ons"}</span>
            </Button>
          </div>
        </Card>

        {/* Included Features Card */}
        <Card className="p-5 space-y-3 rounded-xl border bg-card shadow-sm">
          <div className="flex items-center justify-between border-b pb-2">
            <h3 className="font-bold text-xs text-foreground">{locale === "ar" ? "الميزات والخصائص المشمولة" : "Included Entitlements"}</h3>
            <ShieldCheck className="h-4 w-4 text-emerald-600" />
          </div>
          <ul className="space-y-2 text-xs text-muted-foreground">
            {currentPlan.features.map((feat, idx) => (
              <li key={idx} className="flex items-center gap-2 text-foreground font-medium">
                <Check className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                <span className="text-[11px]">{feat}</span>
              </li>
            ))}
            {addons.filter((a) => a.enabled).map((addon) => (
              <li key={addon.id} className="flex items-center gap-2 text-primary font-bold">
                <Sparkles className="h-3.5 w-3.5 text-primary shrink-0" />
                <span className="text-[11px]">{addon.nameAr}</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      {/* SaaS Billing History & Tax Invoices Table */}
      <Card className="rounded-xl border bg-card overflow-hidden shadow-sm">
        <CardHeader className="flex flex-row items-center justify-between p-3 border-b bg-muted/20">
          <div>
            <CardTitle className="text-xs font-bold text-foreground">{locale === "ar" ? "سجل فواتير الاشتراك السحابي والمدفوعات" : "SaaS Billing Invoices & Receipts"}</CardTitle>
            <p className="text-[10px] text-muted-foreground">{locale === "ar" ? "فواتير الاشتراك الشهري للمنظومة مع إمكانية التحميل والطباعة" : "Monthly subscription tax invoices with print and PDF support"}</p>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-right">
              <thead className="bg-muted/30 font-semibold text-muted-foreground border-b text-[11px]">
                <tr>
                  <th className="p-2.5">رقم فاتورة الاشتراك</th>
                  <th className="p-2.5">تاريخ الاستحقاق</th>
                  <th className="p-2.5">البيان والخدمات</th>
                  <th className="p-2.5 text-left">المبلغ المسدد</th>
                  <th className="p-2.5 text-center">حالة السداد</th>
                  <th className="p-2.5 text-center">الإجراءات</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {mockBillingInvoices.map((inv) => (
                  <tr key={inv.id} className="hover:bg-muted/40 transition-colors">
                    <td className="p-2.5 font-mono font-bold text-primary">{inv.id}</td>
                    <td className="p-2.5 font-mono text-[11px] text-muted-foreground">{inv.date}</td>
                    <td className="p-2.5 font-medium text-foreground">{inv.desc}</td>
                    <td className="p-2.5 text-left font-bold font-mono text-emerald-600">{formatCurrency(inv.amount)}</td>
                    <td className="p-2.5 text-center">
                      <Badge variant="success" className="text-[10px] px-2 py-0.5 font-semibold">
                        مدفوعة ومسددة بالكامل
                      </Badge>
                    </td>
                    <td className="p-2.5 text-center">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedInvoiceToView(inv)}
                        className="h-6.5 text-[11px] gap-1 font-semibold text-primary hover:bg-primary/5"
                      >
                        <FileText className="h-3 w-3" />
                        <span>معاينة الفاتورة</span>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Modal: Upgrade / Change SaaS Plan */}
      {isUpgradeModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
          <div className="max-w-3xl w-full bg-card rounded-2xl border border-border shadow-2xl p-6 space-y-5 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-primary/10 text-primary">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-foreground">
                    {locale === "ar" ? "ترقية باقة الاشتراك السحابية" : "Upgrade SaaS Subscription Plan"}
                  </h3>
                  <p className="text-[11px] text-muted-foreground">
                    {locale === "ar" ? "اختر الباقة المناسبة لحجم ونمو سلسلة صيدلياتك" : "Select the best plan for your pharmacy branch network"}
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsUpgradeModalOpen(false)} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 text-xs">
              {availablePlans.map((p) => {
                const isSelected = currentPlan.id === p.id;
                return (
                  <div
                    key={p.id}
                    className={`p-4 rounded-xl border transition-all flex flex-col justify-between space-y-3 ${
                      isSelected ? "border-primary bg-primary/5 ring-1 ring-primary shadow-sm" : "hover:border-border/80 bg-card"
                    }`}
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="font-bold text-sm text-foreground">{p.nameAr}</h4>
                        {isSelected && <Badge variant="default" className="text-[9px]">الباقة الحالية</Badge>}
                      </div>
                      <p className="text-lg font-extrabold text-primary font-mono">{formatCurrency(p.priceMonthly)} <span className="text-xs font-normal text-muted-foreground">/ شهر</span></p>
                      <div className="text-[11px] text-muted-foreground space-y-1 pt-1 border-t">
                        <p>• حتى {p.branchesQuota} فروع صيدلية مرخصة</p>
                        <p>• حتى {p.usersQuota} مستخدم وصيدلي</p>
                      </div>
                    </div>

                    <Button
                      variant={isSelected ? "outline" : "default"}
                      size="sm"
                      onClick={() => handleSelectPlan(p)}
                      disabled={isSelected}
                      className="w-full text-xs h-8 font-bold"
                    >
                      {isSelected ? "الباقة المفعلة حالياً" : "اختيار هذه الباقة"}
                    </Button>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Modal: Manage Add-ons & Quotas */}
      {isAddonsModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="max-w-lg w-full bg-card rounded-2xl border border-border shadow-2xl p-6 space-y-4 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-blue-500/10 text-blue-600">
                  <Zap className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-foreground">
                    {locale === "ar" ? "إدارة الخدمات والميزات الإضافية" : "Manage Add-ons & Services"}
                  </h3>
                  <p className="text-[11px] text-muted-foreground">
                    {locale === "ar" ? "تفعيل أو تعطيل الخدمات الذكية الإضافية على اشتراكك" : "Enable or disable premium add-ons for your account"}
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsAddonsModalOpen(false)} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-2.5 max-h-80 overflow-y-auto pr-1 text-xs">
              {addons.map((addon) => (
                <div key={addon.id} className="p-3 rounded-xl border bg-muted/20 flex items-center justify-between gap-3">
                  <div className="space-y-0.5 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-foreground">{addon.nameAr}</span>
                      <span className="font-mono text-emerald-600 font-bold">+{formatCurrency(addon.priceMonthly)}/ش</span>
                    </div>
                    <p className="text-[10px] text-muted-foreground">{addon.desc}</p>
                  </div>

                  <Button
                    variant={addon.enabled ? "default" : "outline"}
                    size="sm"
                    onClick={() => toggleAddon(addon.id)}
                    className={`h-7 text-xs font-bold shrink-0 ${addon.enabled ? "bg-emerald-600 hover:bg-emerald-700" : ""}`}
                  >
                    {addon.enabled ? "مفعلة ✅" : "تعطيل"}
                  </Button>
                </div>
              ))}
            </div>

            <div className="p-3 rounded-xl bg-primary/10 border border-primary/20 flex justify-between items-center text-xs font-bold">
              <span>إجمالي قيمة الاشتراك بعد الخدمات:</span>
              <span className="font-mono text-primary text-sm font-extrabold">{formatCurrency(totalMonthlyBilling)} / شهر</span>
            </div>

            <div className="flex justify-end pt-2 border-t">
              <Button size="sm" onClick={() => setIsAddonsModalOpen(false)} className="text-xs font-bold h-8 px-5">
                حفظ وإغلاق
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: View SaaS Invoice Document */}
      {selectedInvoiceToView && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-card rounded-2xl border border-border shadow-2xl p-6 space-y-4 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                <div>
                  <h3 className="text-sm font-bold text-foreground font-mono">{selectedInvoiceToView.id}</h3>
                  <p className="text-[10px] text-muted-foreground">فاتورة اشتراك المنصة السحابية</p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setSelectedInvoiceToView(null)} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-border/40">
                <span className="text-muted-foreground">الجهة المصدرة:</span>
                <span className="font-bold text-foreground">منصة فارما كلاود السحابية (PharmaCloud)</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/40">
                <span className="text-muted-foreground">المستفيد:</span>
                <span className="font-bold text-foreground">سلسلة صيدليات الأمل الحديثة المحدودة</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/40">
                <span className="text-muted-foreground">تاريخ الفاتورة:</span>
                <span className="font-mono">{selectedInvoiceToView.date}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/40">
                <span className="text-muted-foreground">البيان:</span>
                <span className="font-medium text-foreground">{selectedInvoiceToView.desc}</span>
              </div>
              <div className="flex justify-between py-2 text-sm font-bold border-t">
                <span>المبلغ المسدد:</span>
                <span className="font-mono text-emerald-600">{formatCurrency(selectedInvoiceToView.amount)}</span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-3 border-t">
              <Button variant="outline" size="sm" onClick={() => setSelectedInvoiceToView(null)} className="text-xs h-8">
                إغلاق
              </Button>
              <Button size="sm" onClick={() => window.print()} className="gap-1 text-xs font-bold bg-primary hover:bg-primary/90 h-8 text-white">
                <Printer className="h-3.5 w-3.5" />
                <span>طباعة الفاتورة</span>
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Update Payment Card */}
      {isCardModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="max-w-sm w-full bg-card rounded-2xl border border-border shadow-2xl p-6 space-y-4 animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <CreditCard className="h-5 w-5 text-primary" />
                <h3 className="font-bold text-sm text-foreground">تحديث بطاقة السداد</h3>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsCardModalOpen(false)} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="space-y-1">
                <label className="font-semibold text-foreground block text-right">رقم البطاقة الائتمانية (Visa / Mada / Master)</label>
                <Input defaultValue="•••• •••• •••• 4242" className="h-9 font-mono text-xs" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <label className="font-semibold text-foreground block text-right">تاريخ الانتهاء</label>
                  <Input defaultValue="09/28" className="h-9 font-mono text-xs text-center" />
                </div>
                <div className="space-y-1">
                  <label className="font-semibold text-foreground block text-right">رمز الأمان (CVC)</label>
                  <Input defaultValue="•••" className="h-9 font-mono text-xs text-center" />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t">
              <Button variant="outline" size="sm" onClick={() => setIsCardModalOpen(false)} className="text-xs h-8">
                إلغاء
              </Button>
              <Button
                size="sm"
                onClick={() => {
                  setIsCardModalOpen(false);
                  showToast("تم تحديث بطاقة الدفع المعتمدة بنجاح");
                }}
                className="text-xs font-bold bg-primary h-8"
              >
                حفظ البطاقة
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
