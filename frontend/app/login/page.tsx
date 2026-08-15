"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Mail, Building2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useI18n } from "@/lib/i18n";

export default function LoginPage() {
  const router = useRouter();
  const { t } = useI18n();
  const [email, setEmail] = useState("admin@pharmacloud.com");
  const [password, setPassword] = useState("password");
  const [tenantCode, setTenantCode] = useState("TNT-AMAL");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      router.push("/dashboard");
    }, 800);
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-muted/40 p-4 font-sans">
      <Card className="max-w-md w-full shadow-lg">
        <CardHeader className="space-y-1 text-center">
          <div className="mx-auto h-12 w-12 rounded-xl bg-primary flex items-center justify-center text-primary-foreground font-bold text-xl shadow-md mb-2">
            PC
          </div>
          <CardTitle className="text-xl font-bold">{t("login.title")}</CardTitle>
          <CardDescription>{t("login.subtitle")}</CardDescription>
        </CardHeader>

        <form onSubmit={handleLogin}>
          <CardContent className="space-y-4 text-xs">
            <div className="space-y-1">
              <label className="font-medium text-foreground">{t("login.tenant_code")}</label>
              <div className="relative">
                <Building2 className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-3" />
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
                <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-3" />
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
                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground rtl:left-auto rtl:right-3" />
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-9 text-xs rtl:pl-3 rtl:pr-9"
                  required
                />
              </div>
            </div>
          </CardContent>

          <CardFooter className="flex flex-col gap-3">
            <Button type="submit" className="w-full text-xs" disabled={isLoading}>
              {isLoading ? t("login.loading") : t("login.btn_submit")}
            </Button>
            <span className="text-[11px] text-muted-foreground text-center">
              {t("login.security_footer")}
            </span>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
