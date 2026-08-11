"""CashRegister and RegisterSession models for POS counter management."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.sales.models.enums import RegisterStatus, SessionStatus


class CashRegister(TenantAwareModel, FullAuditModel):
    """Physical cash register or checkout counter terminal."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="cash_registers",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.PROTECT,
        related_name="cash_registers",
        verbose_name=_("Branch"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.PROTECT,
        related_name="cash_registers",
        verbose_name=_("Warehouse"),
    )

    register_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Register Number (REG)"))
    name = models.CharField(max_length=100, verbose_name=_("Register Counter Name"))

    status = models.CharField(
        max_length=20,
        choices=RegisterStatus.choices,
        default=RegisterStatus.CLOSED,
        db_index=True,
        verbose_name=_("Register Status"),
    )

    opening_balance = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Default Float Opening Balance"))
    current_balance = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Current Cash Balance"))

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        db_table = "cash_registers"
        verbose_name = _("Cash Register")
        verbose_name_plural = _("Cash Registers")
        ordering = ["register_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "register_number"],
                name="cash_register_tenant_number_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.register_number} - {self.name} ({self.status})"


class RegisterSession(TenantAwareModel, FullAuditModel):
    """Active shift session for a cashier operating a CashRegister."""

    cash_register = models.ForeignKey(
        CashRegister,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name=_("Cash Register"),
        db_index=True,
    )
    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="register_sessions",
        verbose_name=_("Cashier"),
        db_index=True,
    )

    session_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Session Number (SES)"))

    opening_cash = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Opening Float Cash"))
    cash_sales = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Cash Sales"))
    cash_refunds = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Cash Refunds"))
    cash_adjustments = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Cash Adjustments / Expenses"))

    expected_cash = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Expected Till Cash"))
    actual_cash = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Counted Actual Cash"))
    variance = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Variance Amount"))

    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.OPEN,
        db_index=True,
        verbose_name=_("Session Status"),
    )

    opened_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Opened At"))
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Closed At"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "register_sessions"
        verbose_name = _("Register Session")
        verbose_name_plural = _("Register Sessions")
        ordering = ["-opened_at"]

    def calculate_reconciliation(self) -> None:
        """Calculate expected cash and variance against actual counted cash."""
        self.expected_cash = (self.opening_cash + self.cash_sales + self.cash_adjustments) - self.cash_refunds
        self.variance = self.actual_cash - self.expected_cash

    def __str__(self) -> str:
        return f"{self.session_number} - {self.cashier.get_full_name()} ({self.status})"
