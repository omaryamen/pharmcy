"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Mail, Building2, ShieldCheck } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  const router = useRouter();
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
    <div className="min-h-screen w-full flex items-center justify-center bg-muted/40 p-4">
      <Card className="max-w-md w-full shadow-lg">
        <CardHeader className="space-y-1 text-center">
          <div className="mx-auto h-12 w-12 rounded-xl bg-primary flex items-center justify-center text-primary-foreground font-bold text-xl shadow-md mb-2">
            PC
          </div>
          <CardTitle className="text-xl font-bold">PharmaCloud ERP</CardTitle>
          <CardDescription>Enter your credentials and tenant domain to access your workspace.</CardDescription>
        </CardHeader>

        <form onSubmit={handleLogin}>
          <CardContent className="space-y-4 text-xs">
            <div className="space-y-1">
              <label className="font-medium text-foreground">Tenant Organization Code</label>
              <div className="relative">
                <Building2 className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  value={tenantCode}
                  onChange={(e) => setTenantCode(e.target.value)}
                  className="pl-9 text-xs"
                  required
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="font-medium text-foreground">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-9 text-xs"
                  required
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="font-medium text-foreground">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-9 text-xs"
                  required
                />
              </div>
            </div>
          </CardContent>

          <CardFooter className="flex flex-col gap-3">
            <Button type="submit" className="w-full text-xs" disabled={isLoading}>
              {isLoading ? "Authenticating..." : "Sign In to PharmaCloud"}
            </Button>
            <span className="text-[11px] text-muted-foreground text-center">
              Secured by Enterprise Dynamic RBAC & Multi-Tenant Isolation
            </span>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
