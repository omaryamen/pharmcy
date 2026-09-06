"use client";

import React from "react";
import { AlertTriangle, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface ConfirmationDialogProps {
  isOpen: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  isDestructive?: boolean;
  isLoading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmationDialog({
  isOpen,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  isDestructive = false,
  isLoading = false,
  onConfirm,
  onCancel,
}: ConfirmationDialogProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="max-w-md w-full p-6 space-y-4 shadow-xl border-border animate-in fade-in-0 zoom-in-95">
        <div className="flex items-start gap-3">
          <div
            className={`p-2.5 rounded-xl shrink-0 ${
              isDestructive
                ? "bg-destructive/10 text-destructive"
                : "bg-amber-500/10 text-amber-600"
            }`}
          >
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div className="space-y-1 flex-1">
            <h3 className="text-sm font-bold text-foreground">{title}</h3>
            <p className="text-xs text-muted-foreground leading-relaxed">
              {description}
            </p>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 pt-2 border-t">
          <Button
            variant="outline"
            size="sm"
            onClick={onCancel}
            disabled={isLoading}
            className="text-xs"
          >
            {cancelLabel}
          </Button>
          <Button
            variant={isDestructive ? "destructive" : "default"}
            size="sm"
            onClick={onConfirm}
            disabled={isLoading}
            className="text-xs"
          >
            {isLoading ? "Processing..." : confirmLabel}
          </Button>
        </div>
      </Card>
    </div>
  );
}
