"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  ShoppingCart,
  Pill,
  Package,
  FileText,
  DollarSign,
  TrendingUp,
  Building2,
  Settings,
  Bell,
  Search,
  ShieldCheck,
  CreditCard,
  Globe,
  Sun,
  Moon,
  Menu,
  Stethoscope,
  KeyRound,
  ShieldAlert,
  GitBranch,
  LogOut,
  X,
  Lock,
  ArrowRight,
  UserCheck,
  AlertOctagon,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Breadcrumbs, BreadcrumbItem } from "@/components/ui/breadcrumbs";
import { Card } from "@/components/ui/card";
import { useI18n } from "@/lib/i18n";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { t, locale, toggleLocale } = useI18n();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [activeRole, setActiveRole] = useState<string>("pharmacist");
  const [isSwitchUserModalOpen, setIsSwitchUserModalOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  // Sync active role from storage strictly on mount
  useEffect(() => {
    setIsMounted(true);
    const savedRole = localStorage.getItem("pharma_user_role");
    if (savedRole) {
      setActiveRole(savedRole);
    } else {
      // Default to pharmacist if none set
      setActiveRole("pharmacist");
      localStorage.setItem("pharma_user_role", "pharmacist");
    }
  }, []);

  // Close mobile drawer on route change
  useEffect(() => {
    setIsMobileDrawerOpen(false);
  }, [pathname]);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle("dark");
  };

  // Do not render sidebar / topbar on login or root redirect pages
  if (pathname === "/login" || pathname === "/") {
    return <main className="min-h-screen w-full bg-background">{children}</main>;
  }

  // --------------------------------------------------------------------------
  // STRICT ROLE DEFINITIONS & ROUTE PERMISSIONS (RBAC Isolation)
  // --------------------------------------------------------------------------
  interface RoleConfig {
    name: string;
    title: string;
    userName: string;
    userSubtitle: string;
    initials: string;
    scopeName: string;
    badgeBg: string;
    defaultRoute: string;
    allowedRoutes: string[];
    navItems: Array<{ title: string; href: string; icon: any; badge?: string }>;
  }

  const roleConfigs: Record<string, RoleConfig> = {
    superadmin: {
      name: "superadmin",
      title: locale === "ar" ? "مشرف المنصة (SuperAdmin)" : "Platform SuperAdmin",
      userName: locale === "ar" ? "مشرف النظام السحابي" : "Platform SuperAdmin",
      userSubtitle: locale === "ar" ? "إدارة المستأجرين والتراخيص" : "Global SaaS Scope",
      initials: "SA",
      scopeName: locale === "ar" ? "نطاق المنصة السحابية الموحدة" : "Global Cloud Platform Scope",
      badgeBg: "bg-purple-600 hover:bg-purple-700",
      defaultRoute: "/admin",
      allowedRoutes: ["/admin"],
      navItems: [
        { title: locale === "ar" ? "نظرة عامة والتشغيل" : "Overview & KPIs", href: "/admin", icon: LayoutDashboard },
        { title: locale === "ar" ? "إدارة المستأجرين" : "Tenants & Chains", href: "/admin", icon: Building2 },
        { title: locale === "ar" ? "الباقات والاشتراكات" : "SaaS Plans", href: "/admin", icon: CreditCard },
        { title: locale === "ar" ? "أعلام الميزات (Flags)" : "Feature Flags", href: "/admin", icon: KeyRound },
        { title: locale === "ar" ? "صحة النظام والخوادم" : "System Health", href: "/admin", icon: ShieldCheck },
      ],
    },
    pharmacist: {
      name: "pharmacist",
      title: locale === "ar" ? "صيدلي إكلينيكي مرخص" : "Licensed Pharmacist",
      userName: locale === "ar" ? "د. سارة — صيدلي إكلينيكي" : "Dr. Sarah — Clinical Pharmacist",
      userSubtitle: locale === "ar" ? "قسم الوصفات والاعتماد السريري" : "Rx Verification & Dispensing",
      initials: "SP",
      scopeName: locale === "ar" ? "الفرع الرئيسي — قسم الصرف السريري" : "Main Branch — Clinical Dept",
      badgeBg: "bg-emerald-600 hover:bg-emerald-700",
      defaultRoute: "/pharmacy",
      allowedRoutes: ["/pharmacy", "/prescriptions", "/pos", "/sales"],
      navItems: [
        { title: locale === "ar" ? "محطة الصيدلي الإكلينيكي" : "Pharmacist Station", href: "/pharmacy", icon: Stethoscope },
        { title: locale === "ar" ? "طابور الوصفات والاعتماد" : "Prescriptions Queue", href: "/prescriptions", icon: Pill, badge: "Rx" },
      ],
    },
    cashier: {
      name: "cashier",
      title: locale === "ar" ? "أمين الصندوق (الكاشير)" : "POS Cashier Station",
      userName: locale === "ar" ? "فهد — أمين الصندوق" : "Fahad — POS Cashier",
      userSubtitle: locale === "ar" ? "صندوق #1 (وردية نشطة)" : "Register #01 (Active Shift)",
      initials: "FK",
      scopeName: locale === "ar" ? "الفرع الرئيسي — نقطة البيع #1" : "Main Branch — Register #01",
      badgeBg: "bg-emerald-600 hover:bg-emerald-700",
      defaultRoute: "/pos",
      allowedRoutes: ["/pos", "/sales"],
      navItems: [
        { title: locale === "ar" ? "نقطة البيع السريعة (POS)" : "Fast POS Terminal", href: "/pos", icon: ShoppingCart },
        { title: locale === "ar" ? "سجل فواتير المبيعات" : "Sales Receipts", href: "/sales", icon: FileText },
      ],
    },
    inventory_manager: {
      name: "inventory_manager",
      title: locale === "ar" ? "إدارة المخزون والمستودعات" : "Inventory Workspace",
      userName: locale === "ar" ? "عمر — مدير المستودع" : "Omar — Warehouse Manager",
      userSubtitle: locale === "ar" ? "المستودع المركزي وسلسلة الإمداد" : "Central Warehouse & FEFO",
      initials: "OM",
      scopeName: locale === "ar" ? "المستودع الدوائي المركزي" : "Central Pharma Warehouse",
      badgeBg: "bg-blue-600 hover:bg-blue-700",
      defaultRoute: "/inventory",
      allowedRoutes: ["/inventory", "/purchasing"],
      navItems: [
        { title: locale === "ar" ? "المخزون والتشغيلات (FEFO)" : "Inventory & Batches", href: "/inventory", icon: Package },
        { title: locale === "ar" ? "المشتريات وسلسلة التوريد" : "Procurement & Suppliers", href: "/purchasing", icon: DollarSign },
      ],
    },
    accountant: {
      name: "accountant",
      title: locale === "ar" ? "المالية والأستاذ العام" : "Accounting Workspace",
      userName: locale === "ar" ? "طارق — الإدارة المالية" : "Tariq — Financial Accountant",
      userSubtitle: locale === "ar" ? "دفتر الأستاذ والقيود المحاسبية" : "General Ledger & Audit",
      initials: "TM",
      scopeName: locale === "ar" ? "الإدارة المالية المركزية" : "Central Financial Ledger",
      badgeBg: "bg-amber-600 hover:bg-amber-700",
      defaultRoute: "/accounting",
      allowedRoutes: ["/accounting", "/reports", "/billing"],
      navItems: [
        { title: locale === "ar" ? "دفتر الأستاذ والقيود" : "General Ledger & Journals", href: "/accounting", icon: TrendingUp },
        { title: locale === "ar" ? "التقارير والذكاء المالي" : "Financial Reports", href: "/reports", icon: FileText },
        { title: locale === "ar" ? "الاشتراكات والتراخيص" : "Billing & SaaS Subscriptions", href: "/billing", icon: CreditCard },
      ],
    },
    branch_manager: {
      name: "branch_manager",
      title: locale === "ar" ? "إدارة الفرع" : "Branch Management",
      userName: locale === "ar" ? "أحمد المنصوري — مدير الفرع" : "Ahmed — Branch Manager",
      userSubtitle: locale === "ar" ? "إشراف المبيعات ومخزون الفرع" : "Branch Sales & Stock Supervision",
      initials: "AM",
      scopeName: locale === "ar" ? "الفرع الرئيسي — صيدلية الأمل" : "Main Branch — Al-Amal",
      badgeBg: "bg-indigo-600 hover:bg-indigo-700",
      defaultRoute: "/branch",
      allowedRoutes: ["/branch", "/pos", "/sales", "/inventory", "/reports"],
      navItems: [
        { title: locale === "ar" ? "لوحة إدارة الفرع" : "Branch Dashboard", href: "/branch", icon: GitBranch },
        { title: locale === "ar" ? "مبيعات وصناديق الفرع" : "Branch Sales", href: "/sales", icon: FileText },
        { title: locale === "ar" ? "مخزون الفرع" : "Branch Inventory", href: "/inventory", icon: Package },
        { title: locale === "ar" ? "تقارير أداء الفرع" : "Branch Reports", href: "/reports", icon: TrendingUp },
      ],
    },
    pharmacy_admin: {
      name: "pharmacy_admin",
      title: locale === "ar" ? "إدارة الصيدلية (Admin)" : "Pharmacy Admin",
      userName: locale === "ar" ? "د. عبد الله — المدير التنفيذي" : "Dr. Abdullah — Pharmacy Executive",
      userSubtitle: locale === "ar" ? "إدارة المنشأة ومصفوفة الصلاحيات" : "Enterprise Governance & RBAC",
      initials: "PC",
      scopeName: locale === "ar" ? "مؤسسة صيدليات الأمل — سلسلة الفروع" : "Al-Amal Pharmacy Chain",
      badgeBg: "bg-primary",
      defaultRoute: "/app",
      allowedRoutes: ["/app", "/pos", "/sales", "/pharmacy", "/prescriptions", "/inventory", "/purchasing", "/accounting", "/reports", "/billing", "/settings", "/branch", "/dashboard"],
      navItems: [
        { title: locale === "ar" ? "لوحة الإدارة التنفيذية" : "Executive Dashboard", href: "/app", icon: Building2 },
        { title: locale === "ar" ? "إعدادات الصيدلية و RBAC" : "Settings & RBAC Matrix", href: "/settings", icon: Settings },
        { title: locale === "ar" ? "التقارير الشاملة" : "Enterprise Reports", href: "/reports", icon: TrendingUp },
        { title: locale === "ar" ? "الاشتراكات والتراخيص" : "Billing & SaaS", href: "/billing", icon: CreditCard },
      ],
    },
  };

  const currentRoleConfig = roleConfigs[activeRole] || roleConfigs["pharmacist"];

  // --------------------------------------------------------------------------
  // STRICT ROUTE PERMISSION CHECK
  // --------------------------------------------------------------------------
  const isCurrentRouteAllowed = currentRoleConfig.allowedRoutes.some((allowed) =>
    pathname === allowed || pathname.startsWith(allowed + "/")
  );

  const handleSwitchUser = (newRole: string) => {
    localStorage.setItem("pharma_user_role", newRole);
    setActiveRole(newRole);
    setIsSwitchUserModalOpen(false);
    const targetRoute = roleConfigs[newRole]?.defaultRoute || "/login";
    router.push(targetRoute);
  };

  const handleLogout = () => {
    localStorage.removeItem("pharma_user_role");
    router.push("/login");
  };

  // Dynamic Breadcrumb computation
  const getBreadcrumbs = (): BreadcrumbItem[] => {
    if (pathname === "/admin") return [{ label: locale === "ar" ? "إدارة المنصة" : "Platform Admin" }];
    if (pathname === "/app") return [{ label: locale === "ar" ? "إدارة الصيدلية" : "Management Portal" }];
    if (pathname === "/pharmacy") return [{ label: locale === "ar" ? "محطة الصيدلي" : "Pharmacist Station" }];
    if (pathname === "/pos") return [{ label: locale === "ar" ? "نقطة البيع" : "POS Station" }];
    if (pathname === "/inventory") return [{ label: locale === "ar" ? "المخزون والمستودعات" : "Inventory & Batches" }];
    if (pathname === "/accounting") return [{ label: locale === "ar" ? "دفتر الأستاذ والمالية" : "General Ledger" }];
    if (pathname === "/purchasing") return [{ label: locale === "ar" ? "المشتريات والموردين" : "Procurement" }];
    if (pathname === "/sales") return [{ label: locale === "ar" ? "المبيعات والفواتير" : "Sales Ledger" }];
    if (pathname === "/prescriptions") return [{ label: locale === "ar" ? "الوصفات الطبية" : "Prescriptions" }];
    if (pathname === "/settings") return [{ label: locale === "ar" ? "الإعدادات العامة" : "Organization Settings" }];
    if (pathname === "/billing") return [{ label: locale === "ar" ? "الاشتراكات والتراخيص" : "Billing & SaaS" }];
    if (pathname === "/branch") return [{ label: locale === "ar" ? "إدارة الفرع" : "Branch Operations" }];
    if (pathname === "/reports") return [{ label: locale === "ar" ? "التقارير والتحليلات" : "Reports & BI" }];
    return [{ label: locale === "ar" ? "لوحة التحكم" : "Dashboard" }];
  };

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden font-sans">
      {/* Mobile Drawer Backdrop */}
      {isMobileDrawerOpen && (
        <div
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setIsMobileDrawerOpen(false)}
        />
      )}

      {/* Sidebar (Desktop + Mobile Drawer) */}
      <aside
        className={cn(
          "flex flex-col border-r bg-card transition-all duration-300 z-50",
          "fixed lg:static inset-y-0 start-0",
          isSidebarOpen ? "w-64" : "w-20",
          isMobileDrawerOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        {/* Brand Header */}
        <div className="flex h-16 items-center justify-between px-4 border-b">
          <div className="flex items-center gap-3">
            <div className={cn("flex h-9 w-9 items-center justify-center rounded-xl text-white font-bold shadow-md", currentRoleConfig.badgeBg)}>
              {currentRoleConfig.initials}
            </div>
            {isSidebarOpen && (
              <div className="flex flex-col">
                <span className="font-bold tracking-tight text-foreground text-sm">
                  {currentRoleConfig.name === "superadmin" ? (locale === "ar" ? "منصة فارما كلاود" : "PharmaCloud Platform") : t("nav.brand")}
                </span>
                <span className="text-[11px] text-muted-foreground">{t("nav.tagline")}</span>
              </div>
            )}
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => {
              if (window.innerWidth < 1024) {
                setIsMobileDrawerOpen(false);
              } else {
                setIsSidebarOpen(!isSidebarOpen);
              }
            }}
            aria-label="Toggle Navigation Sidebar"
          >
            {isMobileDrawerOpen ? <X className="h-4 w-4 lg:hidden" /> : <Menu className="h-4 w-4" />}
          </Button>
        </div>

        {/* Tenant/Branch or Platform Shell Badge */}
        {isSidebarOpen && (
          <div className="px-4 py-3 border-b bg-muted/40 flex items-center justify-between">
            <div className="flex items-center gap-2 truncate">
              {currentRoleConfig.name === "superadmin" ? (
                <ShieldAlert className="h-4 w-4 text-purple-600 shrink-0" />
              ) : (
                <Building2 className="h-4 w-4 text-primary shrink-0" />
              )}
              <span className="text-xs font-medium text-foreground truncate">
                {currentRoleConfig.scopeName}
              </span>
            </div>
            <Badge variant="success" className="text-[10px] px-1.5 py-0">{t("nav.online")}</Badge>
          </div>
        )}

        {/* Strict Role-Isolated Navigation Items */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-1" aria-label="Main Navigation">
          {currentRoleConfig.navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href + item.title}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all",
                  isActive
                    ? "bg-primary text-primary-foreground shadow-sm font-semibold"
                    : "text-muted-foreground hover:bg-muted/70 hover:text-foreground"
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {isSidebarOpen && <span className="flex-1 truncate">{item.title}</span>}
                {isSidebarOpen && item.badge && (
                  <Badge variant={isActive ? "secondary" : "default"} className="text-[10px] px-1.5 py-0">
                    {item.badge}
                  </Badge>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Role Identity Footer with quick switch trigger */}
        <div className="p-3 border-t flex items-center justify-between bg-card">
          <div className="flex items-center gap-2.5 truncate">
            <div className={cn("h-8 w-8 rounded-xl flex items-center justify-center font-bold text-xs text-white shrink-0 shadow-sm", currentRoleConfig.badgeBg)}>
              {currentRoleConfig.initials}
            </div>
            {isSidebarOpen && (
              <div className="flex flex-col truncate">
                <span className="text-xs font-semibold text-foreground truncate">{currentRoleConfig.userName}</span>
                <span className="text-[10px] text-muted-foreground truncate">
                  {currentRoleConfig.userSubtitle}
                </span>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Header */}
        <header className="flex h-16 items-center justify-between border-b bg-card px-4 lg:px-6 z-30">
          <div className="flex items-center gap-3 flex-1">
            {/* Mobile Hamburger Toggle */}
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setIsMobileDrawerOpen(true)}
              aria-label="Open Mobile Menu"
            >
              <Menu className="h-5 w-5" />
            </Button>

            {/* Breadcrumb Navigation */}
            <div className="hidden md:flex items-center">
              <Breadcrumbs items={getBreadcrumbs()} />
            </div>

            {/* Search Box */}
            <div className="relative w-full max-w-xs sm:max-w-sm hidden sm:block">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-2.5 pointer-events-none" />
              <input
                type="text"
                placeholder={
                  activeRole === "pharmacist"
                    ? (locale === "ar" ? "بحث في الوصفات الطبية والأدوية... (Ctrl+K)" : "Search prescriptions & drugs... (Ctrl+K)")
                    : activeRole === "cashier"
                    ? (locale === "ar" ? "مسح الباركود أو بحث عن دواء... (F2)" : "Scan barcode or search medicine... (F2)")
                    : `${t("header.search_placeholder")}`
                }
                className="h-9 w-full rounded-md border border-input bg-background pl-9 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-primary rtl:pl-4 rtl:pr-9"
              />
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            {/* Active Role Badge */}
            <Badge variant="default" className={cn("text-[11px] font-semibold hidden sm:flex items-center gap-1.5 text-white", currentRoleConfig.badgeBg)}>
              <span>{currentRoleConfig.title}</span>
            </Badge>

            {/* Switch User Session Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsSwitchUserModalOpen(true)}
              className="h-8 gap-1.5 text-xs font-semibold border-primary/30 text-primary hover:bg-primary/5"
              title={locale === "ar" ? "تبديل المستخدم والصلاحية" : "Switch User / Role"}
            >
              <UserCheck className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">{locale === "ar" ? "تبديل المستخدم" : "Switch User"}</span>
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="h-8 gap-1.5 text-xs text-muted-foreground hover:text-destructive"
              title={locale === "ar" ? "تسجيل الخروج" : "Logout"}
            >
              <LogOut className="h-3.5 w-3.5" />
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={toggleLocale}
              className="gap-1.5 text-xs font-medium h-8"
              title={t("header.toggle_lang")}
            >
              <Globe className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "English" : "العربية"}</span>
            </Button>

            <Button variant="ghost" size="icon" onClick={toggleTheme} className="h-8 w-8" title={t("header.toggle_theme")}>
              {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>

            <Button variant="ghost" size="icon" className="h-8 w-8 relative" title={t("header.notifications")}>
              <Bell className="h-4 w-4" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive" />
            </Button>
          </div>
        </header>

        {/* Main Work Area with Strict Route Access Guard */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-background">
          {isMounted && !isCurrentRouteAllowed ? (
            /* Access Denied (403 Unauthorized Route Guard) */
            <div className="h-full flex items-center justify-center p-4">
              <Card className="max-w-lg w-full p-8 text-center space-y-5 shadow-xl border-destructive/20 bg-card rounded-2xl">
                <div className="mx-auto h-16 w-16 rounded-2xl bg-destructive/10 text-destructive flex items-center justify-center">
                  <AlertOctagon className="h-8 w-8" />
                </div>

                <div className="space-y-2">
                  <Badge variant="destructive" className="text-xs px-2.5 py-0.5">
                    {locale === "ar" ? "403 — وصول غير مصرح به" : "403 — Access Denied"}
                  </Badge>
                  <h2 className="text-lg font-bold text-foreground">
                    {locale === "ar" ? "غير مصرح لك بالوصول إلى هذه الشاشة" : "Unauthorized Role Access"}
                  </h2>
                  <p className="text-xs text-muted-foreground leading-relaxed max-w-md mx-auto">
                    {locale === "ar"
                      ? `أنت مسجل حالياً بدور [${currentRoleConfig.userName}]. لا تملك الصلاحيات الكافية للوصول إلى هذا المسار.`
                      : `You are currently authenticated as [${currentRoleConfig.userName}]. You do not have permission to view this workspace.`}
                  </p>
                </div>

                <div className="p-3 bg-muted/40 rounded-xl border text-xs flex items-center justify-between text-muted-foreground">
                  <span>{locale === "ar" ? "المسار المطلوب:" : "Requested Path:"}</span>
                  <span className="font-mono font-bold text-foreground">{pathname}</span>
                </div>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-2.5 pt-2">
                  {pathname === "/pos" && (
                    <Button
                      onClick={() => handleSwitchUser("cashier")}
                      className="w-full sm:w-auto gap-2 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 h-9 text-white shadow-sm"
                    >
                      <ShoppingCart className="h-3.5 w-3.5" />
                      <span>{locale === "ar" ? "الدخول الفوري بدور الكاشير (POS)" : "Switch to Cashier Terminal"}</span>
                    </Button>
                  )}
                  <Button
                    onClick={() => router.push(currentRoleConfig.defaultRoute)}
                    className="w-full sm:w-auto gap-2 text-xs font-bold bg-primary h-9"
                  >
                    <span>{locale === "ar" ? "العودة إلى بيئة عملك المعتمدة" : "Return to Workspace"}</span>
                    <ArrowRight className="h-3.5 w-3.5 rtl:rotate-180" />
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setIsSwitchUserModalOpen(true)}
                    className="w-full sm:w-auto gap-2 text-xs font-semibold h-9"
                  >
                    <UserCheck className="h-3.5 w-3.5" />
                    <span>{locale === "ar" ? "تبديل المستخدم" : "Switch User"}</span>
                  </Button>
                </div>
              </Card>
            </div>
          ) : (
            children
          )}
        </main>
      </div>

      {/* Clean Modal: Switch User & Role Switcher */}
      {isSwitchUserModalOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="max-w-md w-full p-5 space-y-4 shadow-2xl border bg-card rounded-2xl animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-primary/10 text-primary">
                  <UserCheck className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-foreground">
                    {locale === "ar" ? "تبديل المستخدم وبيئة العمل" : "Switch User Workspace"}
                  </h3>
                  <p className="text-[11px] text-muted-foreground">
                    {locale === "ar" ? "اختر الحساب والمسمى الوظيفي المراد تفعيله" : "Select authenticated staff identity to switch session"}
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsSwitchUserModalOpen(false)} className="h-7 w-7">
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
              {Object.values(roleConfigs).map((cfg) => {
                const isSelected = activeRole === cfg.name;
                return (
                  <div
                    key={cfg.name}
                    onClick={() => handleSwitchUser(cfg.name)}
                    className={cn(
                      "flex items-center justify-between p-3 rounded-xl border cursor-pointer transition-all",
                      isSelected
                        ? "border-primary bg-primary/5 shadow-sm"
                        : "hover:border-border/80 hover:bg-muted/40"
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <div className={cn("h-8 w-8 rounded-xl flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-sm", cfg.badgeBg)}>
                        {cfg.initials}
                      </div>
                      <div className="flex flex-col">
                        <span className="text-xs font-bold text-foreground">{cfg.userName}</span>
                        <span className="text-[10px] text-muted-foreground">{cfg.userSubtitle}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Badge variant={isSelected ? "default" : "outline"} className="text-[10px] px-1.5 py-0">
                        {cfg.defaultRoute}
                      </Badge>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="flex items-center justify-end pt-2 border-t">
              <Button variant="ghost" size="sm" onClick={() => setIsSwitchUserModalOpen(false)} className="text-xs h-8">
                {locale === "ar" ? "إغلاق" : "Close"}
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
