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
  Users,
  Building2,
  Settings,
  Bell,
  Search,
  ShieldCheck,
  CreditCard,
  Globe,
  Sun,
  Moon,
  ChevronRight,
  Menu,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

const navItems: NavItem[] = [
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { title: "POS Terminal", href: "/pos", icon: ShoppingCart },
  { title: "Prescriptions", href: "/prescriptions", icon: Pill, badge: "Rx" },
  { title: "Inventory & Stock", href: "/inventory", icon: Package },
  { title: "Sales & Invoices", href: "/sales", icon: FileText },
  { title: "Purchasing & AP", href: "/purchasing", icon: DollarSign },
  { title: "Accounting & GL", href: "/accounting", icon: TrendingUp },
  { title: "E-Commerce", href: "/ecommerce", icon: Store },
  { title: "Reports & BI", href: "/reports", icon: TrendingUp },
  { title: "Super Admin", href: "/admin", icon: ShieldCheck },
  { title: "SaaS Billing", href: "/billing", icon: CreditCard },
  { title: "Settings", href: "/settings", icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [language, setLanguage] = useState<"en" | "ar">("en");

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle("dark");
  };

  const toggleLanguage = () => {
    const nextLang = language === "en" ? "ar" : "en";
    setLanguage(nextLang);
    document.documentElement.setAttribute("dir", nextLang === "ar" ? "rtl" : "ltr");
    document.documentElement.setAttribute("lang", nextLang);
  };

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden">
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
                <span className="font-bold tracking-tight text-foreground text-sm">PharmaCloud</span>
                <span className="text-xs text-muted-foreground">Enterprise ERP</span>
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
              <span className="text-xs font-medium text-foreground truncate">Main Branch - Al-Amal</span>
            </div>
            <Badge variant="success" className="text-[10px] px-1.5 py-0">Online</Badge>
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
                <span className="text-xs font-medium truncate">Dr. Ahmed Pharmacist</span>
                <span className="text-[10px] text-muted-foreground">Pharmacist / Admin</span>
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
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search medicines, SKU, barcode, invoices, patients... (Ctrl+K)"
                className="h-9 w-full rounded-md border border-input bg-background pl-9 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={toggleLanguage} title="Switch Language">
              <Globe className="h-4 w-4" />
            </Button>

            <Button variant="ghost" size="icon" onClick={toggleTheme} title="Toggle Theme">
              {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>

            <Button variant="ghost" size="icon" className="relative" title="Notifications">
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
