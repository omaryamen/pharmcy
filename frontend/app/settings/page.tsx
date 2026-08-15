"use client";

import React from "react";
import { Settings, Users, Shield, Building, Bell } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">System Settings & User Management</h1>
        <p className="text-sm text-muted-foreground">Configure organization details, branch assignments, and RBAC permissions.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2 p-6 space-y-4">
          <h3 className="text-sm font-semibold">Tenant & Pharmacy Information</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="space-y-1">
              <label className="text-muted-foreground font-medium">Organization Name</label>
              <Input defaultValue="Al-Amal Pharmacy Chain LLC" />
            </div>
            <div className="space-y-1">
              <label className="text-muted-foreground font-medium">Commercial Registration #</label>
              <Input defaultValue="CR-1010884920" />
            </div>
            <div className="space-y-1">
              <label className="text-muted-foreground font-medium">Tax / VAT Number</label>
              <Input defaultValue="30099482100003" />
            </div>
            <div className="space-y-1">
              <label className="text-muted-foreground font-medium">Default Currency</label>
              <Input defaultValue="USD ($)" />
            </div>
          </div>
          <div className="flex justify-end pt-2">
            <Button>Save Settings</Button>
          </div>
        </Card>

        <Card className="p-6 space-y-4">
          <h3 className="text-sm font-semibold">Security & RBAC Policies</h3>
          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-2 rounded-lg border">
              <span>MFA Enforcement</span>
              <span className="font-semibold text-emerald-600">Enabled</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded-lg border">
              <span>Token Rotation Policy</span>
              <span className="font-semibold text-emerald-600">Strict</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded-lg border">
              <span>Password Expiry</span>
              <span className="font-semibold text-foreground">90 Days</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
