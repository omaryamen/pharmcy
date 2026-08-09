"""Domain choices for Enterprise Inventory & Batch Management."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class BatchStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    QUARANTINE = "quarantine", _("Quarantine")
    EXPIRED = "expired", _("Expired")
    RECALLED = "recalled", _("Recalled")
    BLOCKED = "blocked", _("Blocked")
    DEPLETED = "depleted", _("Depleted")
    ARCHIVED = "archived", _("Archived")


class InventoryStatus(models.TextChoices):
    AVAILABLE = "available", _("Available")
    RESERVED = "reserved", _("Reserved")
    QUARANTINE = "quarantine", _("Quarantine")
    DAMAGED = "damaged", _("Damaged")
    EXPIRED = "expired", _("Expired")
    BLOCKED = "blocked", _("Blocked")
    RECALLED = "recalled", _("Recalled")
    INACTIVE = "inactive", _("Inactive")


class TransactionType(models.TextChoices):
    OPENING_BALANCE = "opening_balance", _("Opening Balance")
    RECEIPT = "receipt", _("Goods Receipt")
    ISSUE = "issue", _("Stock Issue")
    SALE = "sale", _("POS / Sales Issue")
    SALE_RETURN = "sale_return", _("Sales Return")
    PURCHASE_RETURN = "purchase_return", _("Purchase Return")
    TRANSFER_IN = "transfer_in", _("Transfer In")
    TRANSFER_OUT = "transfer_out", _("Transfer Out")
    ADJUSTMENT = "adjustment", _("Stock Adjustment")
    ADJUSTMENT_INCREASE = "adjustment_increase", _("Stock Adjustment (+)")
    ADJUSTMENT_DECREASE = "adjustment_decrease", _("Stock Adjustment (-)")
    DAMAGE = "damage", _("Damaged Stock")
    EXPIRY = "expiry", _("Expired Stock")
    QUARANTINE = "quarantine", _("Placed in Quarantine")
    RELEASE_QUARANTINE = "release_quarantine", _("Released from Quarantine")
    RESERVATION = "reservation", _("Stock Reservation")
    RELEASE_RESERVATION = "release_reservation", _("Stock Reservation Release")
    CORRECTION = "correction", _("System Correction")


class AdjustmentReason(models.TextChoices):
    OPENING_BALANCE = "opening_balance", _("Opening Balance Load")
    CORRECTION = "correction", _("Count Correction")
    DAMAGE = "damage", _("Physical Damage")
    EXPIRY = "expiry", _("Product Expiration")
    LOSS = "loss", _("Shrinkage / Loss")
    FOUND_STOCK = "found_stock", _("Found Surplus Stock")
    SYSTEM_CORRECTION = "system_correction", _("System Data Fix")
    OTHER = "other", _("Other Reason")
