"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ShoppingCart,
  Pill,
  Package,
  FileText,
  DollarSign,
  TrendingUp,
  Store,
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
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { t, locale, toggleLocale } = useI18n();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle("dark");
  };

  const navItems = [
    { title: t("nav.dashboard"), href: "/dashboard", icon: LayoutDashboard },
    { title: t("nav.pos"), href: "/pos", icon: ShoppingCart },
    { title: t("nav.prescriptions"), href: "/prescriptions", icon: Pill, badge: "Rx" },
    { title: t("nav.inventory"), href: "/inventory", icon: Package },
    { title: t("nav.sales"), href: "/sales", icon: FileText },
    { title: t("nav.purchasing"), href: "/purchasing", icon: DollarSign },
    { title: t("nav.accounting"), href: "/accounting", icon: TrendingUp },
    { title: t("nav.ecommerce"), href: "/ecommerce", icon: Store },
    { title: t("nav.reports"), href: "/reports", icon: TrendingUp },
    { title: t("nav.admin"), href: "/admin", icon: ShieldCheck },
    { title: t("nav.billing"), href: "/billing", icon: CreditCard },
    { title: t("nav.settings"), href: "/settings", icon: Settings },
  ];

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden font-sans">
      {/* Sidebar */}
      <aside
        className={cn(
          "flex flex-col border-r bg-card transition-all duration-300 z-30",
          isSidebarOpen ? "w-64" : "w-20"
        )}
      >
        {/* Brand Header */}
        <div className="flex h-16 items-center justify-between px-4 border-b">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold shadow-md">
              PC
            </div>
            {isSidebarOpen && (
              <div className="flex flex-col">
                <span className="font-bold tracking-tight text-foreground text-sm">{t("nav.brand")}</span>
                <span className="text-[11px] text-muted-foreground">{t("nav.tagline")}</span>
              </div>
            )}
          </div>
          <Button variant="ghost" size="icon" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
            <Menu className="h-4 w-4" />
          </Button>
        </div>

        {/* Tenant/Branch Badge */}
        {isSidebarOpen && (
          <div className="px-4 py-3 border-b bg-muted/40 flex items-center justify-between">
            <div className="flex items-center gap-2 truncate">
              <Building2 className="h-4 w-4 text-primary shrink-0" />
              <span className="text-xs font-medium text-foreground truncate">{t("nav.branch_label")}</span>
            </div>
            <Badge variant="success" className="text-[10px] px-1.5 py-0">{t("nav.online")}</Badge>
          </div>
        )}

        {/* Navigation Items */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
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

        {/* User Footer */}
        <div className="p-3 border-t flex items-center justify-between">
          <div className="flex items-center gap-3 truncate">
            <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center font-bold text-xs text-primary">
              DR
            </div>
            {isSidebarOpen && (
              <div className="flex flex-col truncate">
                <span className="text-xs font-medium truncate">{t("nav.user_role")}</span>
                <span className="text-[10px] text-muted-foreground">{locale === "ar" ? "صيدلي / مدير النظام" : "Pharmacist / Admin"}</span>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Header */}
        <header className="flex h-16 items-center justify-between border-b bg-card px-6">
          <div className="flex items-center gap-4 flex-1 max-w-md">
            <div className="relative w-full">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-2.5" />
              <input
                type="text"
                placeholder={t("header.search_placeholder")}
                className="h-9 w-full rounded-md border border-input bg-background pl-9 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-primary rtl:pl-4 rtl:pr-9"
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={toggleLocale}
              className="gap-2 text-xs font-medium"
              title={t("header.toggle_lang")}
            >
              <Globe className="h-3.5 w-3.5" />
              <span>{locale === "ar" ? "English (EN)" : "العربية (AR)"}</span>
            </Button>

            <Button variant="ghost" size="icon" onClick={toggleTheme} title={t("header.toggle_theme")}>
              {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>

            <Button variant="ghost" size="icon" className="relative" title={t("header.notifications")}>
              <Bell className="h-4 w-4" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive" />
            </Button>
          </div>
        </header>

        {/* Main Work Area */}
        <main className="flex-1 overflow-y-auto p-6 bg-background">
          {children}
        </main>
      </div>
    </div>
  );
}
