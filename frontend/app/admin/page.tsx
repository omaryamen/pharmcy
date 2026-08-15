"use client";

import React from "react";
import { ShieldCheck, Activity, Server, AlertCircle, ToggleRight, UserCheck } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function AdminPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Super Admin & Platform Operations</h1>
        <p className="text-sm text-muted-foreground">Multi-tenant SaaS monitoring, system health checks, and global feature flags.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4 flex items-center gap-4">
          <div className="p-3 rounded-full bg-emerald-500/10 text-emerald-600">
            <Activity className="h-6 w-6" />
          </div>
          <div>
            <span className="text-xs text-muted-foreground font-medium">System Health</span>
            <p className="text-lg font-bold text-emerald-600">100% Operational</p>
          </div>
        </Card>

        <Card className="p-4 flex items-center gap-4">
          <div className="p-3 rounded-full bg-blue-500/10 text-blue-600">
            <Server className="h-6 w-6" />
          </div>
          <div>
            <span className="text-xs text-muted-foreground font-medium">Active SaaS Tenants</span>
            <p className="text-lg font-bold text-foreground">42 Organizations</p>
          </div>
        </Card>

        <Card className="p-4 flex items-center gap-4">
          <div className="p-3 rounded-full bg-purple-500/10 text-purple-600">
            <ToggleRight className="h-6 w-6" />
          </div>
          <div>
            <span className="text-xs text-muted-foreground font-medium">Feature Flags</span>
            <p className="text-lg font-bold text-foreground">8 Active Rollouts</p>
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader className="border-b">
          <CardTitle>Platform Audit & Impersonation Log</CardTitle>
          <CardDescription>Immutable tracking of privileged platform engineering actions.</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-xs text-left">
            <thead className="bg-muted/40 font-medium text-muted-foreground border-b">
              <tr>
                <th className="p-3">Action</th>
                <th className="p-3">Operator</th>
                <th className="p-3">Target Tenant</th>
                <th className="p-3">Reason</th>
                <th className="p-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr className="hover:bg-muted/50">
                <td className="p-3 font-semibold">Tenant Impersonation</td>
                <td className="p-3 font-mono">superadmin@pharmacloud.com</td>
                <td className="p-3 font-medium">Al-Amal Pharmacy Chain</td>
                <td className="p-3">Troubleshooting POS sync issue #T-992</td>
                <td className="p-3 text-muted-foreground">2026-08-15 01:22</td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
