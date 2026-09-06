"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Mail, Building2, UserCheck, ShieldCheck, Globe, Moon, Sun, Pill } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";

export default function LoginPage() {
  const router = useRouter();
  const { t, locale, toggleLocale } = useI18n();
  const [email, setEmail] = useState("admin@pharmacloud.com");
  const [password, setPassword] = useState("password");
  const [tenantCode, setTenantCode] = useState("TNT-AMAL");
  const [selectedRole, setSelectedRole] = useState("pharmacist");
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle("dark");
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    localStorage.setItem("pharma_user_role", selectedRole);

    setTimeout(() => {
      setIsLoading(false);
      // Automatic Role-Based Routing Target
      switch (selectedRole) {
        case "superadmin":
          router.push("/admin");
          break;
        case "pharmacy_admin":
          router.push("/app");
          break;
        case "pharmacist":
          router.push("/pharmacy");
          break;
        case "cashier":
          router.push("/pos");
          break;
        case "inventory_manager":
          router.push("/inventory");
          break;
        case "accountant":
          router.push("/accounting");
          break;
        case "branch_manager":
          router.push("/branch");
          break;
        default:
          router.push("/dashboard");
      }
    }, 500);
  };

  return (
    <div className="min-h-screen w-full flex flex-col justify-between bg-muted/20 font-sans">
      {/* Top Header Bar for Login */}
      <header className="flex items-center justify-between px-6 py-4 border-b bg-card/60 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground font-bold shadow-sm">
            PC
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-sm tracking-tight text-foreground">{t("nav.brand")}</span>
            <span className="text-[11px] text-muted-foreground">{t("nav.tagline")}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={toggleLocale}
            className="gap-1.5 text-xs font-medium h-8"
          >
            <Globe className="h-3.5 w-3.5" />
            <span>{locale === "ar" ? "English" : "العربية"}</span>
          </Button>

          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="h-8 w-8"
          >
            {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
        </div>
      </header>

      {/* Main Centered Login Card */}
      <main className="flex-1 flex items-center justify-center p-4">
        <Card className="max-w-md w-full shadow-xl border-border bg-card">
          <CardHeader className="space-y-1.5 text-center pb-4">
            <div className="mx-auto h-12 w-12 rounded-2xl bg-primary/10 text-primary flex items-center justify-center font-bold text-xl shadow-inner mb-1">
              <Pill className="h-6 w-6" />
            </div>
            <CardTitle className="text-xl font-bold tracking-tight text-foreground">{t("login.title")}</CardTitle>
            <CardDescription className="text-xs text-muted-foreground">{t("login.subtitle")}</CardDescription>
          </CardHeader>

          <form onSubmit={handleLogin}>
            <CardContent className="space-y-3.5 text-xs">
              <div className="space-y-1">
                <label className="font-medium text-foreground">{t("login.tenant_code")}</label>
                <div className="relative">
                  <Building2 className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-3 pointer-events-none" />
                  <Input
                    value={tenantCode}
                    onChange={(e) => setTenantCode(e.target.value)}
                    className="pl-9 text-xs rtl:pl-3 rtl:pr-9 font-mono"
                    required
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-medium text-foreground">{t("login.email")}</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-3 pointer-events-none" />
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-9 text-xs rtl:pl-3 rtl:pr-9 font-mono"
                    required
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-medium text-foreground">{t("login.password")}</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-3 pointer-events-none" />
                  <Input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-9 text-xs rtl:pl-3 rtl:pr-9"
                    required
                  />
                </div>
              </div>

              {/* Authenticated Staff Role Selection */}
              <div className="space-y-1 pt-1">
                <label className="font-medium text-foreground flex items-center gap-1.5">
                  <UserCheck className="h-3.5 w-3.5 text-primary" />
                  <span>{locale === "ar" ? "نوع الحساب والدور الوظيفي" : "Authenticated Staff Role"}</span>
                </label>
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  className="w-full h-9 rounded-md border border-input bg-background px-3 text-xs focus:outline-none focus:ring-1 focus:ring-primary text-foreground"
                >
                  <option value="pharmacist">{locale === "ar" ? "صيدلي مرخص (Pharmacist ➔ /pharmacy)" : "Licensed Pharmacist ➔ /pharmacy"}</option>
                  <option value="cashier">{locale === "ar" ? "أمين الصندوق (Cashier ➔ /pos)" : "POS Cashier ➔ /pos"}</option>
                  <option value="inventory_manager">{locale === "ar" ? "أمين المستودع (Inventory ➔ /inventory)" : "Inventory Manager ➔ /inventory"}</option>
                  <option value="accountant">{locale === "ar" ? "محاسب مالي (Accountant ➔ /accounting)" : "Accountant ➔ /accounting"}</option>
                  <option value="branch_manager">{locale === "ar" ? "مدير الفرع (Branch Manager ➔ /branch)" : "Branch Manager ➔ /branch"}</option>
                  <option value="pharmacy_admin">{locale === "ar" ? "مدير الصيدلية (Pharmacy Admin ➔ /app)" : "Pharmacy Admin ➔ /app"}</option>
                  <option value="superadmin">{locale === "ar" ? "مشرف المنصة (SuperAdmin ➔ /admin)" : "Platform SuperAdmin ➔ /admin"}</option>
                </select>
              </div>
            </CardContent>

            <CardFooter className="flex flex-col gap-3 pt-2">
              <Button type="submit" className="w-full text-xs font-semibold h-9" disabled={isLoading}>
                {isLoading ? t("login.loading") : t("login.btn_submit")}
              </Button>
              <div className="flex items-center justify-center gap-1.5 text-[11px] text-muted-foreground text-center">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
                <span>{t("login.security_footer")}</span>
              </div>
            </CardFooter>
          </form>
        </Card>
      </main>

      {/* Footer */}
      <footer className="py-3 px-4 text-center text-[11px] text-muted-foreground border-t bg-card/40">
        © 2026 PharmaCloud ERP. {locale === "ar" ? "جميع الحقوق محفوظة — نظام إدارة الصيدليات السحابي" : "All rights reserved — Enterprise Cloud Pharmacy ERP."}
      </footer>
    </div>
  );
}
