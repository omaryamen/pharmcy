"""CashMovement domain model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.cash_and_bank.models.enums import CashMovementType
from apps.common.models import FullAuditModel, TenantAwareModel


class CashMovement(TenantAwareModel, FullAuditModel):
    """Detailed audit record representing individual cash flows in/out of a CashAccount or POS RegisterSession."""

    cash_account = models.ForeignKey(
        "cash_and_bank.CashAccount",
        on_delete=models.CASCADE,
        related_name="movements",
        verbose_name=_("Cash Account"),
        db_index=True,
    )
    register_session = models.ForeignKey(
        "sales.RegisterSession",
        on_delete=models.SET_NULL,
        related_name="cash_movements",
        null=True,
        blank=True,
        verbose_name=_("POS Register Session"),
    )

    movement_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Movement Number (CSM)"))
    movement_type = models.CharField(
        max_length=35,
        choices=CashMovementType.choices,
        default=CashMovementType.SALE,
        db_index=True,
        verbose_name=_("Movement Type"),
    )

    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Cash Movement Amount"))
    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))

    reference_type = models.CharField(max_length=50, blank=True, default="", db_index=True, verbose_name=_("Reference Type"))
    reference_id = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Reference ID"))

    description = models.TextField(blank=True, default="", verbose_name=_("Movement Description"))

    class Meta:
        db_table = "cash_movements"
        verbose_name = _("Cash Movement")
        verbose_name_plural = _("Cash Movements")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "movement_number"],
                name="csm_tenant_number_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.movement_number} [{self.movement_type}] - ${self.amount}"
