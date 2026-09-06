import React from "react";
import { LucideIcon, Inbox } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  actionLabel,
  onAction,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-8 text-center rounded-xl border border-dashed bg-muted/20 space-y-3",
        className
      )}
    >
      <div className="p-3 rounded-full bg-muted/50 text-muted-foreground">
        <Icon className="h-8 w-8" />
      </div>
      <div className="space-y-1 max-w-sm">
        <h3 className="text-sm font-bold text-foreground">{title}</h3>
        {description && (
          <p className="text-xs text-muted-foreground leading-relaxed">{description}</p>
        )}
      </div>
      {actionLabel && onAction && (
        <Button size="sm" onClick={onAction} className="text-xs mt-2">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
